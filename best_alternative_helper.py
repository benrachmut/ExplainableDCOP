from Agents import Agent
from enums import DcopType, Algorithm
from Globals_ import (repetitions, REQUIRE_H_IN_GROUP, IMPROVED_ORDER, PROPAGATE_GLOBAL_UB,
                      LARGE, K_EXP, T_EXP,REQUIRE_H_IN_QUERY)
from main_multiple_expirements import create_selected_dcop
from collections import deque
from typing import Dict, List, Set, Union, Tuple, Optional, Any, TypedDict
import itertools

# דברים להחזיר בשביל הדוגמת הרצה עם RODA
#    if dcop_type == DcopType.dense_random_uniform: (צריך להחזיק לדומיין בגודל 10 ול10 סוכנים)

from problems import DCOP

SEARCH_VISITS: int = 0      # NCLO Counter


class BestAlternativeResult(TypedDict):
    alternative_assignment: Optional[Dict[int, int]]
    alternative_cost: Optional[int]
    chosen_group: Set[int]
    best_delta: int
    NCLO: int


# ---------------------------------------------------------------------------
# Helper copied from RODA.py (to avoid an import cycle)
# ---------------------------------------------------------------------------

def _copy_dict_and_find_min_cost(cost_tbl: Dict) -> Dict:
    """Return {"cost_table": <copy>, "min_cost": <min>} as in RODA."""
    ans = {}
    min_cost = LARGE
    for k, v in cost_tbl.items():
        ans[k] = v
        if v < min_cost:
            min_cost = v
    return {"cost_table": ans, "min_cost": min_cost}


"""
    Central (non-distributed) implementation of *Region* construction for a given
    agent *h* in a DCOP instance.

    It mirrors the logic of the distributed RODA handshake (DISCOVER / INFO) but
    executes it in one place, using the full knowledge stored in the DCOP object.

    Returned structure
    ------------------
    {
        "region_agents"     : set[int],               # the ids in N_t(h)
        "path_map"          : dict[int, list[int]],    # shortest path h→u (≤ t+1)
        "agent_info_store" : dict[int, dict],        # identical to RODA store
        "groups"            : list[set[int]]          # every connected B, |B|≤k, h∈B
    }

    If |N_t(h)|>k we enumerate **only** the maximal sets of size *k* (exactly as
    RODA.build_region does).  Otherwise one group – the whole neighbourhood – is
    returned."""


def build_region(DCOP_instance:  "DCOP", agent: Union["Agent", int], k: int, t: int):
    """Compute the *Region* R_h for *agent* with parameters *(k, t)*.

    This centralised procedure faithfully reproduces the DISCOVER/INFO flood
    of RODA but without sending network messages.
    """
    # ------------------------------------------------------------------
    # 0)  Normalise *agent* argument and create quick lookup dicts
    # ------------------------------------------------------------------
    if hasattr(agent, "id_"):
        h_id = agent.id_
    else:
        h_id = int(agent)

    id2agent = {ag.id_: ag for ag in DCOP_instance.agents}
    if h_id not in id2agent:
        raise ValueError(f"Agent {h_id} not found in this DCOP instance")

    # ------------------------------------------------------------------
    # 1)  Emulate DISCOVER flood up to depth t+1 (exactly as in RODA)
    # ------------------------------------------------------------------
    seen: Dict[int, int] = {h_id: 0}  # node → hop distance
    path_map: Dict[int, List[int]] = {h_id: [h_id]}  # node → path list
    agent_info_store: Dict[int, Dict] = {}

    # utility to gather the *INFO* block for agent *u* at distance d
    def _build_info(u_id: int, d: int, path: List[int]):
        ag = id2agent[u_id]
        info = {
            "agent_id": u_id,
            "current_assignment": getattr(ag, "variable", None),
            "path": list(path),
        }
        if d <= t:
            info["domain"] = list(getattr(ag, "domain", []))
            info["neighbors"] = list(getattr(ag, "neighbors_agents_id", []))
            costs = {}
            for neigh in getattr(ag, "neighbors_obj", []):
                other_id = neigh.get_other_agent(ag)
                costs[other_id] = _copy_dict_and_find_min_cost(neigh.cost_table)
            info["costs"] = costs
        return info

    # Queue holds tuples (current_node_id, distance, path_from_h)
    q: deque = deque()
    h_agent = id2agent[h_id]
    for n_id in getattr(h_agent, "neighbors_agents_id", []):
        q.append((n_id, 1, [h_id]))

    while q:
        u, d, path = q.popleft()
        if u in seen and seen[u] <= d:
            continue
        seen[u] = d
        new_path = path + [u]
        path_map[u] = new_path
        agent_info_store[u] = _build_info(u, d, new_path)
        if d < t + 1:
            u_agent = id2agent[u]
            for n_id in getattr(u_agent, "neighbors_agents_id", []):
                if n_id not in new_path:  # prevent trivial cycles
                    q.append((n_id, d + 1, new_path))

    # add mediator’s own INFO (distance 0)
    agent_info_store[h_id] = _build_info(h_id, 0, [h_id])

    # ------------------------------------------------------------------
    # 2)  Build *discovered* (N_t(h)) set and adjacency
    # ------------------------------------------------------------------
    discovered: Set[int] = {
        n for n in agent_info_store
        if len(agent_info_store[n]["path"]) <= t + 1
    }
    adj: Dict[int, Set[int]] = {
        u: set(agent_info_store[u]["neighbors"]) & discovered
        for u in discovered
    }

    # ------------------------------------------------------------------
    # 3)  Enumerate maximal connected subsets B ⊆ N_t(h) containing agent.id_, of size ≤ k
    # ------------------------------------------------------------------
    if len(discovered) <= k:
        groups = [set(discovered)]
    else:
        groups: List[Set[int]] = []
        seen_groups: Set[frozenset] = set()

        def backtrack(current: Set[int]):
            if len(current) == k:
                frozen = frozenset(current)
                if frozen not in seen_groups:
                    seen_groups.add(frozen)
                    groups.append(set(current))
                return
            # find all neighbors of 'current' not yet in it
            nbrs = set().union(*(adj[n] for n in current)) - current
            for v in nbrs:
                backtrack(current | {v})

        backtrack({h_id})

    # ------------------------------------------------------------------
    # 4)  Package result
    # ------------------------------------------------------------------
    return {
        "region_agents": discovered,
        "path_map": path_map,
        "agent_info_store": agent_info_store,
        "groups": groups,
    }


# ================================================================
#  Best-Alternative (second–best) assignment for a full-scope query
# ================================================================

def best_alternative_full_scope(
    dcop: "DCOP",
    complete_asgn: Dict[int, int],
    query_vars: Set[int],
    h_id: int,
    k_alg: int,
    t_alg: int,
)-> BestAlternativeResult:

    """
    Return (alternative_assignment, alternative_cost, chosen_group, best_delta).

    • Groups are  maximal size subsets of `query_vars` (not of the entire region):
        – each contains `h_id` if REQUIRE_H_IN_GROUP set on True
        – size = min(k, |query_vars|)
    • For every group we search the cheapest assignment ≠ current.
    • At the end we return the best alternative among all groups.
    • If PROPAGATE_GLOBAL_UB is True the algorithm forwards the best Δ-cost
      found so far as an upper-bound to subsequent groups, allowing deeper
      pruning; if False each group is searched with an infinite upper bound.
    • If REQUIRE_H_IN_QUERY is True the caller **must** include `h_id`
      itself in `query_vars`; otherwise a ValueError is raised.  When the
      flag is False the query set may omit the mediator.

    Note
    ----
    k_alg, t_alg – optimisation parameters
        (define the mediator’s region and the solution guarantees)
    K_EXP, T_EXP – explanation parameters
        (limits used when searching for the second-best alternative)
    """
    global SEARCH_VISITS
    SEARCH_VISITS = 0
    qset: Set[int] = set(query_vars)

    region = build_region(dcop, h_id, k_alg, t_alg)
    info = region["agent_info_store"]

    # ----- query must include h_id? ----------------------------------
    if REQUIRE_H_IN_QUERY and h_id not in qset:
        raise ValueError(
            f"h_id (Agent_{h_id}) is not in query_vars; "
            "when REQUIRE_H_IN_QUERY is True  h_id must be part of the query."
        )

    # Safety: every queried agent must be inside the mediator’s region
    if not qset.issubset(region["region_agents"]):
        raise ValueError(f"Some queried variables are outside Agent_{h_id } Region (i.e. N_t({h_id} where t={t_alg}).")

    # Distance filter for explanation search
    if T_EXP != LARGE:
        qset = {
            a for a in qset
            if len(region["path_map"][a]) - 1 <= T_EXP
        }
        if not qset:
            raise ValueError("No queried agent is within T_EXP hops of the mediator")

    # Enumerate candidate groups using K_EXP and T_EXP *explanation* limits
    candidate_groups = _enumerate_query_groups(qset, h_id)

    best_delta = LARGE
    best_alt_asgn: Optional[Dict[int, int]] = None
    best_alt_grp: Set[int] = set()
    best_alt_cost: Optional[int] = None

    for grp in candidate_groups:
        ub_delta_for_grp = best_delta if PROPAGATE_GLOBAL_UB else LARGE
        alt_asgn, alt_delta, current_group_cost = _second_best_for_group(
            grp, info, complete_asgn, h_id, ub_delta_for_grp
        )

        if alt_asgn is not None and alt_delta < best_delta:
            best_delta = alt_delta
            best_alt_asgn = alt_asgn
            best_alt_grp = set(grp)
            best_alt_cost = current_group_cost + alt_delta

    if best_alt_asgn is None:
        return {
            "alternative_assignment": None,
            "alternative_cost": LARGE,
            "chosen_group": set(),
            "best_delta": LARGE,
            "NCLO": SEARCH_VISITS
        }

    # Fill unchanged values for queried variables outside the chosen group
    full_reply = {
        a: (best_alt_asgn[a] if a in best_alt_asgn else complete_asgn[a])
        for a in qset
    }
    return {"alternative_assignment": full_reply, "alternative_cost": best_alt_cost,
            "chosen_group": best_alt_grp, "best_delta": best_delta, "NCLO": SEARCH_VISITS}


# ------------------------- Group enumeration ---------------------------

def _enumerate_query_groups(
    qset: Set[int],
    h_id: int,
) -> List[Set[int]]:
    """
    Enumerate all **maximal-size** subsets of `qset`
    where size = min(K_EXP, |qset|).

    • If REQUIRE_H_IN_GROUP is True  – every subset must include `h_id`.
    • Otherwise – no such constraint.
    """

    target_size = min(K_EXP, len(qset))  # maximal size required

    # --- Case 1: each subset must include h_id ------------------------
    if REQUIRE_H_IN_GROUP:
        if h_id not in qset:
            raise ValueError(f"h_id not in qset (i.e. Agent {h_id}"
                             f" is not part of the query) but REQUIRE_H_IN_GROUP is True")
        rest = qset - {h_id}
        combos = itertools.combinations(rest, target_size - 1)
        return [{h_id, *c} for c in combos]

    # --- Case 2: no requirement on h_id -------------------------------
    combos = itertools.combinations(qset, target_size)
    return [set(c) for c in combos]


# -------------------- Second-best per single group ---------------------
def _second_best_for_group(
    group: Set[int],
    info: Dict[int, Dict],
    complete_asgn: Dict[int, int],
    h_id: int,
    ub_delta: int,
) -> Tuple[Optional[Dict[int, int]], int, int]:
    """
    Return the cheapest assignment that differs from the current
    assignment of `group` inside `complete_asgn`.

    IMPROVED_ORDER toggle
    ---------------------
    If the global flag ``IMPROVED_ORDER`` is True, each non-mediator
    agent’s domain is reordered so that its *current* value appears
    first.  This usually lets the BnB encounter the “no-change” branch
    early and improves pruning efficiency; when the flag is False the
    original domain order is left intact.
    """

    # ---- ordering: put h_id last *only if it is in the group* -----------
    if h_id in group:
        G = [a for a in group if a != h_id] + [h_id]
    else:
        G = list(group)  # keep original members as-is
    n = len(G)

    # ---- current group cost ----------------------------------------
    current_group_cost: int = 0
    for i, u in enumerate(G):
        vu = complete_asgn[u]
        for v in G[i + 1:]:
            if v in info[u]["costs"]:
                current_group_cost += _edge_cost(info, u, vu, v, complete_asgn[v])
        for nbr in info[u]["neighbors"]:
            if nbr not in group:
                current_group_cost += _edge_cost(info, u, vu, nbr, complete_asgn[nbr])

    # ---- domains ----------------------------------------------------
    domains = {a: list(info[a]["domain"]) for a in G}
    if IMPROVED_ORDER:
        for a in G:
            cur = complete_asgn[a]
            if a != h_id and cur in domains[a]:
                domains[a].remove(cur)
                domains[a].insert(0, cur)

    # ---- constants --------------------------------------------------
    ext_val = {}
    for a in G:
        for nbr in info[a]["neighbors"]:
            if nbr not in group:
                ext_val[nbr] = complete_asgn[nbr]

    edge_lb = _edge_lower_bounds(G, info)

    # ---- current group assignment (for equality test) --------------------------
    current_tuple = {a: complete_asgn[a] for a in G}

    # ----  best-alternative bookkeeping -----------------------
    best_alt_delta = ub_delta           # initial UB (∞ or propagated)
    best_alt_asgn = None

    partial: Dict[int, int] = {}

    # ---- recursive BnB ---------------------------------------------

    def recurse(idx: int, acc: int) -> None:
        nonlocal best_alt_delta, best_alt_asgn, current_group_cost
        if idx == n:    # full assignment
            if partial != current_tuple:
                delta = acc - current_group_cost
                if delta < best_alt_delta:
                    best_alt_delta = delta
                    best_alt_asgn = dict(partial)
            return

        # optimistic lower bound:

        # lower-bound contribution of yet-unassigned IN-group pairs (u,v) –
        # sum of the pre-computed C_min(u,v) for every pair whose two
        # endpoints are still unassigned at this depth
        future_pairs_lb = sum(
            edge_lb[i][j] for i in range(idx, n) for j in range(i + 1, n)
        )

        # lower-bound contribution for edges that connect any still-unassigned
        # in-group agent aj (indices idx+1 … n-1) to a FIXED external neighbour.
        # We add C_min(aj, nb) only when that edge actually exists (nb appears in
        # aj’s neighbour list and in ext_val). This yields a tight optimistic
        # bound for the remaining portion of the search branch.
        future_ext_lb = 0
        for j in range(idx+1, n):
            aj = G[j]
            for nb in info[aj]["neighbors"]:
                if nb in ext_val:
                    future_ext_lb += info[aj]["costs"][nb]["min_cost"]

        a = G[idx]
        for val in domains[a]:
            extra = 0
            # inner-group edges to already-fixed agents
            for j in range(idx):
                aj = G[j]
                if aj in info[a]["costs"]:
                    extra += _edge_cost(info, a, val, aj, partial[aj])
            # edges to external fixed agents
            for _nbr in info[a]["costs"]:
                if _nbr in ext_val:
                    extra += _edge_cost(info, a, val, _nbr, ext_val[_nbr])

            new_cost = acc + extra
            optimistic_delta = (new_cost + future_pairs_lb + future_ext_lb) - current_group_cost
            if optimistic_delta >= best_alt_delta:
                continue  # prune branch

            partial[a] = val
            recurse(idx + 1, new_cost)
            del partial[a]

    recurse(0, 0)

    return best_alt_asgn, best_alt_delta, current_group_cost


# --------------------------- tiny utilities ----------------------------
def _edge_lower_bounds(G: List[int], info: Dict[int, Dict]) -> List[List[int]]:
    """Matrix of C_min(u,v) for u<v indices inside G."""
    n = len(G)
    lb = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if G[j] in info[G[i]]["costs"]:
                lb[i][j] = info[G[i]]["costs"][G[j]]["min_cost"]
    return lb


def _edge_cost(
    info: Dict[int, Dict],
    u: int,
    val_u: int,
    v: int,
    val_v: int,
) -> int:
    global SEARCH_VISITS
    tbl = info[u]["costs"][v]["cost_table"]
    _key = (("A_" + str(min(u, v)), val_u if u < v else val_v),
            ("A_" + str(max(u, v)), val_v if u < v else val_u))
    SEARCH_VISITS += 1
    return tbl.get(_key, 0)


def timed_run(label, **knobs):
    # apply flags
    for k, v in knobs.items():
        globals()[k] = v
    globals()['SEARCH_VISITS'] = 0   # reset

    import time
    t0 = time.perf_counter()
    dict = best_alternative_full_scope(
        dcop, {1:2,2:2,3:1}, {1,2,3}, h_id=2, k_alg=5, t_alg=10
    )

    alternative_assignment = dict["alternative_assignment"]
    alternative_cost = dict["alternative_cost"]
    chosen_group = dict["chosen_group"]
    best_delta = dict["best_delta"]
    NCLO = dict["NCLO"]
    dt = time.perf_counter() - t0
    print(f"{label:20} visits={SEARCH_VISITS:4}   NCLO={NCLO:4}   time={dt*1e6:.0f} µs   best_delta={best_delta}")


if __name__ == "__main__":
    # ─── CONFIGURE TEST ───────────────────────────────────────────────────────
    dcop_type = DcopType.dense_random_uniform
    algorithm = Algorithm.branch_and_bound
    # ────────────────────────────────────────────────────────────────────────────

    for run_id in range(repetitions):
        print(f"\n=== RODA TEST RUN #{run_id} ===\n")
        # build DCOP with RODA agents
        dcop = create_selected_dcop(run_id, dcop_type, algorithm)
        result = build_region(dcop,2,2,1)
        for key, value in result.items():
            if "agent_info_store" == key:
                print(key)
                for key1, value1 in value.items():
                    print(f"{key1}: {value1}")
            else:
                print(f"{key}: {value}")

        timed_run("baseline",
                  IMPROVED_ORDER=False, PROPAGATE_GLOBAL_UB=False)

        timed_run("improved-order",
                  IMPROVED_ORDER=True, PROPAGATE_GLOBAL_UB=False)

        timed_run("propagated UB",
                  IMPROVED_ORDER=False, PROPAGATE_GLOBAL_UB=True)

        timed_run("both flags",
                  IMPROVED_ORDER=True, PROPAGATE_GLOBAL_UB=True)

