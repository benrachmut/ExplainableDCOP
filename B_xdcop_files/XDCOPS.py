from collections import deque

from networkx.algorithms.structuralholes import constraint

from B_xdcop_files.Agents_X import *
from B_xdcop_files.Queries import *
from Globals_ import *



class Explanation():
    def __init__(self, dcop,query,explanation_type,communication_type ):
        self.query = query
        self.D = dcop.D
        self.all_ids = list(dcop.agents_dict.keys())
        self.explanation_type = explanation_type
        self.communication_type = communication_type
        self.iteration = 0
        self.data_entry = {}
        self.bfs_representation = None
        self.bfs_route = None
        if communication_type == CommunicationType.BFS:
            self.bfs_representation = self.bfs_representation_()
            self.bfs_route = self.construct_routes()
        self.query_agent,query_agent_id = self.create_query_x_agent(self.query.agent)
        self.x_agents = self.create_x_agents(dcop,query_agent_id) # all
        self.x_agents.append(self.query_agent)
        self.x_agents_dict = {}
        for a in self.x_agents:
            self.x_agents_dict[a.id_]=a
        self.mailer = Mailer(self.x_agents)
        self.execute_distributed()

    def construct_routes(self ):
        routes = {}

        for node in self.bfs_representation:
            if node == self.query.agent.id_:
                continue

            path = []
            current = node

            while current is not None:
                path.append(current)
                current = self.bfs_representation[current][0]

            routes[node] = path[::-1]  # Reverse to get the route from root to node

        return routes

    def bfs_representation_(self):
        bfs_tree = {}
        visited = set()
        root = self.query.agent.id_

        queue = deque([root])
        graph = self.get_graph_of_query()


        bfs_tree[root] = (None, [])  # Root has no parent
        visited.add(root)

        while queue:
            node = queue.popleft()
            children = []

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    bfs_tree[neighbor] = (node, [])  # Set parent
                    children.append(neighbor)

            bfs_tree[node] = (bfs_tree[node][0], children)  # Update children

        return bfs_tree
    def agents_init(self):
        for a in self.x_agents:
            a.initialize()

    def execute_distributed(self):

        self.agents_init()
        while not self.query_agent.is_termination_condition_met():
            self.iteration+=1
            mailer_feedback = self.mailer.place_messages_in_agents_inbox()
            if mailer_feedback : break
            self.agents_perform_iteration()
        self.mailer.place_messages_in_agents_inbox()
        self.collect_data()



    def agents_perform_iteration(self):
        for a in self.x_agents:
            a.execute_iteration()

    def collect_constraints(self):
        ans = []
        agent_dict = self.query.variables_in_query
        alternative_partial_assignments = self.query.alternative_partial_assignments
        for aps in alternative_partial_assignments:

            ans.append(ConstraintCollection(solution_partial_assignment = self.query.solution_partial_assignment,
                                            alternative_partial_assignment=aps,
                                            complete_assignment = self.query.solution_complete_assignment, agent_dict =agent_dict))
        return ans


    def get_cumulative_delta_from_solution_dict(self):

        solution_unique_sum_cost = sum(constraint.cost for constraint in self.constraints_collections[0].solution_unique_constraints)

        cum_delta_from_solution_dict = {}
        sum_of_alternative_cost_dict = {}
        infeasible_pa = {}
        for auc in self.constraints_collections:
            cum_delta_from_solution_dict[auc] = {}
            sum_of_alternative_cost_dict[auc] = {}
            sorted_unique_alternative_constraints = sorted(auc.alternative_unique_constraints, key=lambda x: x.cost, reverse=True)
            sum_of_alternative_cost = 0
            for constraint in sorted_unique_alternative_constraints:
                cost = constraint.cost

                sum_of_alternative_cost = sum_of_alternative_cost + cost
                delta = (sum_of_alternative_cost - solution_unique_sum_cost)
                cum_delta_from_solution_dict[auc][constraint] = delta
                sum_of_alternative_cost_dict[auc][constraint]=sum_of_alternative_cost
                if cost == my_inf:
                    if auc not in infeasible_pa.keys():
                        infeasible_pa[auc] = []
                    infeasible_pa[auc].append(constraint)

        return cum_delta_from_solution_dict,sum_of_alternative_cost_dict,infeasible_pa

    def create_query_x_agent(self, agent):
        id_,variable,domain,neighbors_agents_id,neighbors_obj_dict = self.get_info_for_x_agent(agent)



        if self.explanation_type == ExplanationType.Shortest_Explanation:
            ax = AgentX_Query_BroadcastCentral(id_, variable, domain, neighbors_agents_id, neighbors_obj_dict, self.query, self.communication_type, self.bfs_representation, self.bfs_route,self.all_ids)
        if self.explanation_type == ExplanationType.Grounded_Constraints:
            ax = AgentX_Query_BroadcastCentral_NoSort(id_, variable, domain, neighbors_agents_id, neighbors_obj_dict, self.query, self.communication_type, self.bfs_representation, self.bfs_route,self.all_ids)
        if self.explanation_type == ExplanationType.Sort_Parallel:
            ax = AgentX_Query_BroadcastDistributedV2(id_, variable, domain, neighbors_agents_id, neighbors_obj_dict,
                                                     self.query, self.communication_type, self.bfs_representation, self.bfs_route,self.all_ids)

        if self.explanation_type == ExplanationType.Varint_max:
            ax = AgentX_Query_BroadcastDistributed_communication_heurtsic_max(id_, variable, domain, neighbors_agents_id, neighbors_obj_dict,
                                                                              self.query, self.communication_type, self.bfs_representation, self.bfs_route,self.all_ids)
        if self.explanation_type == ExplanationType.Varint_mean:
            ax = AgentX_Query_BroadcastDistributed_communication_heurtsic_mean(id_, variable, domain,
                                                                               neighbors_agents_id, neighbors_obj_dict,
                                                                               self.query, self.communication_type, self.bfs_representation, self.bfs_route,self.all_ids)

        if self.explanation_type == ExplanationType.Sort_Parallel_Not_Opt:
            ax = AgentX_Query_BroadcastDistributedV3(id_, variable, domain, neighbors_agents_id, neighbors_obj_dict,
                                                     self.query, self.communication_type, self.bfs_representation, self.bfs_route,self.all_ids)
        return ax,id_


    def get_info_for_x_agent(self, agent):
        id_ = agent.id_
        variable = copy.deepcopy(agent.variable)
        domain = copy.deepcopy(agent.domain)
        neighbors_agents_id = copy.deepcopy(agent.neighbors_agents_id)
        neighbors_obj_dict = agent.neighbors_obj_dict
        return id_,variable,domain,neighbors_agents_id,neighbors_obj_dict

    def create_x_agents(self, dcop, query_agent_id):
        ans = []
        a_q = self.query.agent.id_

        for agent in dcop.agents:
            id_,variable,domain,neighbors_agents_id,neighbors_obj_dict = self.get_info_for_x_agent(agent)
            if id_ != query_agent_id:

                if self.explanation_type == ExplanationType.Shortest_Explanation or  self.explanation_type == ExplanationType.Grounded_Constraints:
                    ax = AgentX_BroadcastCentral(id_, variable, domain, neighbors_agents_id, neighbors_obj_dict, self.communication_type, self.bfs_representation, self.bfs_route,a_q,self.all_ids)
                if self.explanation_type == ExplanationType.Sort_Parallel or self.explanation_type == ExplanationType.Sort_Parallel_Not_Opt:
                    ax = AgentX_BroadcastDistributed(id_, variable, domain, neighbors_agents_id, neighbors_obj_dict, self.communication_type, self.bfs_representation, self.bfs_route,a_q,self.all_ids)
                if self.explanation_type == ExplanationType.Varint_max or self.explanation_type == ExplanationType.Varint_mean:
                    ax = AgentX_BroadcastDistributed(id_, variable, domain, neighbors_agents_id, neighbors_obj_dict, self.communication_type, self.bfs_representation, self.bfs_route,a_q,self.all_ids)

                ans.append(ax)
        return ans

    def get_centralized_explanation(self):
        self.constraints_collections = self.collect_constraints()
        self.cum_delta_from_solution_dict, self.sum_of_alternative_cost_dict, self.infeasible_pa = self.get_cumulative_delta_from_solution_dict()
        self.min_constraint_collection = min(self.constraints_collections,key=lambda x: x.alternative_unique_constraints_cost)
        self.min_cum_delta_from_solution = self.cum_delta_from_solution_dict[self.min_constraint_collection]

    def collect_data(self):
        self.data_entry["Alternative_delta_cost_per_addition"] = self.query_agent.alternative_delta_constraints_cost_per_addition
        self.data_entry["Iterations"] = self.iteration
        self.data_entry["NCLO"] = self.mailer.mailer_clock
        self.data_entry["NCLO_for_valid_solution"] = self.query_agent.NCLO_for_valid_solution

        self.data_entry["Total Messages"] =self.mailer.total_msgs
        self.data_entry["Bandwidth"] = self.mailer.total_bandwidth



        self.data_entry["Alternative # Constraint"] = len(self.query_agent.alternative_constraints_for_explanations)
        self.data_entry["Cost delta of Valid"] = self.get_alternative_cost_delta(is_min_for_valid=True)
        self.data_entry["Delta Cost per Constraint"] = self.data_entry["Cost delta of Valid"]/self.data_entry["Alternative # Constraint"]
        self.data_entry["Cost delta of All Alternatives"] = self.get_alternative_cost_delta(is_min_for_valid=False)
        self.data_entry["Delta Cost of All Alternatives per Constraint"] = self.data_entry["Cost delta of All Alternatives"]/self.data_entry["Alternative # Constraint"]

        self.data_entry["agent_privacy"], self.data_entry["agent_privacy_normalized"] = self.calc_agent_privacy()
        self.data_entry["topology_privacy"], self.data_entry["topology_privacy_normalized"] = self.calc_topology_privacy()
        self.data_entry["constraint_privacy"], self.data_entry["constraint_privacy_normalized"] = self.calc_constraint_privacy()
        self.data_entry["decision_privacy_with_send_sol_constraint"], self.data_entry["decision_privacy_with_send_sol_normalized"] = self.calc_decision_privacy_with_send_sol_constraint()
        self.data_entry["decision_privacy_without_send_sol_constraint"],self.data_entry["decision_privacy_without_send_sol_constraint_normalized"] = self.calc_constraint_privacy_without_send_sol_constraint()


    def calc_constraint_privacy_without_send_sol_constraint(self):
        share_val_with_neighbors = 0
        amount_of_agent = len(self.x_agents)

        for var_obj in self.query.variables_in_query.values():
            share_val_with_neighbors = share_val_with_neighbors + len(var_obj.neighbors_obj_dict)

        ans = share_val_with_neighbors / amount_of_agent
        ans_norm = ans /(amount_of_agent-1)

        return ans,ans_norm

    def calc_decision_privacy_with_send_sol_constraint(self):
        share_val_with_neighbors = 0
        amount_of_agent = len(self.x_agents)

        for var_obj in self.query.variables_in_query.values():
            share_val_with_neighbors = share_val_with_neighbors + len(var_obj.neighbors_obj_dict)
        for var_obj in self.query.variables_in_query.values():
            share_val_with_neighbors = share_val_with_neighbors + len(self.x_agents_dict[var_obj.id_].agents_discovered)

        ans = share_val_with_neighbors / amount_of_agent
        ans_norm = ans /(amount_of_agent-1)

        return ans,ans_norm
    def calc_constraint_privacy(self):
        who_is_aware_per_agent = {}
        amount_of_agent = len(self.x_agents)

        for a_i in self.x_agents:
            who_is_aware_per_agent[a_i] = []
            for a_j in self.x_agents:
                if a_i.id_ != a_j.id_:
                    if a_i.id_ in a_j.constraint_privacy.keys():
                        what_topology_exposed_to_a_j = a_j.constraint_privacy[a_i.id_]
                        who_is_aware_per_agent[a_i].extend(what_topology_exposed_to_a_j)
        amount = {}
        amount_normalized = {}
        for who_lost, to_who_list in who_is_aware_per_agent.items():
            amount[who_lost.id_] = len(to_who_list) / (len(who_lost.neighbors_obj_dict)*(self.D*self.D))
            amount_normalized[who_lost.id_] = amount[who_lost.id_]/(amount_of_agent-1)
        ans = sum(amount.values())/len(amount.values())
        ans_normalized = sum(amount_normalized.values())/len(amount_normalized.values())


        return ans,ans_normalized

    def calc_topology_privacy(self):
        who_is_aware_per_agent = {}
        amount_of_agent = len(self.x_agents)

        for a_i in self.x_agents:
            who_is_aware_per_agent[a_i] = []
            for a_j in self.x_agents:
                if a_i.id_ != a_j.id_:
                    if a_i.id_ in a_j.topology_privacy.keys():
                        what_topology_exposed_to_a_j = a_j.topology_privacy[a_i.id_]
                        who_is_aware_per_agent[a_i].extend(what_topology_exposed_to_a_j)
        amount = {}
        amount_normalized = {}
        for who_lost, to_who_list in who_is_aware_per_agent.items():
            amount[who_lost.id_] = len(to_who_list) / len(who_lost.neighbors_obj_dict)
            amount_normalized[who_lost.id_] = amount[who_lost.id_]/(amount_of_agent-1)
        ans = sum(amount.values())/amount_of_agent
        ans_normalized = sum(amount_normalized.values())/amount_of_agent


        return ans,ans_normalized

    @staticmethod
    def measure_names():
        return ["Iterations","NCLO","Total Messages","Bandwidth","Alternative # Constraint","Cost delta","Delta Cost per Constraint",    "agent_privacy","topology_privacy","constraint_privacy","decision_privacy_with_send_sol_constraint","decision_privacy_without_send_sol_constraint",
                "agent_privacy_normalized", "topology_privacy_normalized", "constraint_privacy_normalized", "decision_privacy_with_send_sol_constraint_normalized",
                "decision_privacy_without_send_sol_constraint_normalized"
                ]
    def get_alternative_cost_delta(self,is_min_for_valid):
        if is_min_for_valid:
            alt_sum = self.query_agent.alternative_constraints_min_valid_cost
        else:
            alt_sum = self.query_agent.alternative_constraints_max_measure

        solution_sum  = self.query_agent.solution_cost

        ans = alt_sum-solution_sum

        return ans

    def get_graph_of_query(self):
        ans = {}
        variables_in_query_dict = self.query.variables_in_query
        for id_,agent in variables_in_query_dict.items():
            t = []
            for n_id in agent.neighbors_agents_id:
                if n_id in variables_in_query_dict.keys():
                    t.append(n_id)

            ans[id_] = t
        return ans

    def calc_agent_privacy(self):
        who_is_aware_per_agent = {}
        amount_of_agent = len(self.x_agents)
        for a_i in self.x_agents:
            who_is_aware_per_agent[a_i] = []
            for a_j in self.x_agents:
                if a_i.id_ != a_j.id_:
                    if a_i.id_ in a_j.agents_discovered:
                        who_is_aware_per_agent[a_i].append(a_j.id_)
        amount_normal = {}
        amount = {}
        for a, l_of_loss in who_is_aware_per_agent.items():
            amount_normal[a.id_] = len(l_of_loss) / (amount_of_agent-len(a.neighbors_obj_dict))
            amount[a.id_] = len(l_of_loss)
        ans_normalize = sum(amount_normal.values())/amount_of_agent
        ans = sum(amount.values())/amount_of_agent
        return ans,ans_normalize


class XDCOP:
    def __init__(self,dcop,query):
        self.dcop = dcop
        self.query = query
        #self.explanation = Explanation(query,explanation_type,dcop)



