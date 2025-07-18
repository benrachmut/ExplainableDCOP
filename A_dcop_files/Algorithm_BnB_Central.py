import copy
from abc import ABC

from A_dcop_files.Agents import Agent
from Globals_ import *


class Bnb_Central_Agent(Agent,ABC):

    def __init__(self, id_, D):
        Agent.__init__(self,id_,D)



    def initialize(self):
       pass

    def send_msgs(self):
        pass



    def update_msgs_in_context(self, msgs):
        pass



    def change_status_after_update_msgs_in_context(self, msgs):
        pass

    def is_compute_in_this_iteration(self):
        pass

    def compute(self):
        pass

    def change_status_after_send_msgs(self):
       pass




class Bnb_central:
    def __init__(self, agents):
        # Sort agents based on the number of neighbors, descending
        self.agents = sorted(agents, key=lambda x: len(x.neighbors_agents_id), reverse=True)
        self.second_best = [{}, float('inf')]

        # Initialize agent levels
        self.levels_dict_agents = {i: self.agents[i] for i in range(len(self.agents))}

        # Upper and lower bounds
        self.UB = [{}, float('inf')]  # UB[1] represents the current best cost
        self.LB = [{}, 0]  # LB[1] represents the current cost of the partial solution

        if central_bnb_debug:
            for a in agents:
                print(a, "neighbors:", a.neighbors_agents_id)

        self.solve()

        if central_bnb_debug:
            print("UB at the end is:",self.UB)

    def solve(self, level=0):
        """
        Recursive method to solve the problem using Branch and Bound.
        """

        # Base case: If all levels are assigned, check and update UB and second best
        if level == len(self.levels_dict_agents):
            if len(self.LB[0]) == len(self.agents):
                cost = self.LB[1]
                if cost < self.UB[1]:
                    self.second_best = copy.deepcopy(self.UB)  # move best to second
                    self.UB = copy.deepcopy(self.LB)  # update best
                elif self.UB[1] < cost < self.second_best[1]:
                    self.second_best = copy.deepcopy(self.LB)  # update second best
            return

        # Get current agent and its domain
        current_agent = self.levels_dict_agents[level]
        if central_bnb_debug:
            print(current_agent, "start solve at level", level, "LB:", self.LB)

        domain, cost_for_each_domain = self.sort_domain_by_cost(current_agent)

        for value in domain:
            # Assign the value and update LB
            self.LB[0][current_agent.id_] = value
            self.LB[1] += cost_for_each_domain[value]

            # Prune branches if the current LB exceeds second_best[1]
            # (not just UB[1]) to allow better second-best discovery
            if self.LB[1] < self.second_best[1]:
                self.solve(level + 1)

            if central_bnb_debug:
                print(current_agent, "backtracked on value:", value,
                      "UB =", self.UB, "second_best =", self.second_best, "LB =", self.LB)

            # Backtrack
            self.LB[1] -= cost_for_each_domain[value]
            del self.LB[0][current_agent.id_]

    def is_consistent_with_lb(self, level, current_agent, value):
        """
        Check if the value is consistent with the current partial solution (LB).
        """
        for neighbor_id in current_agent.neighbors_agents_id:
            if neighbor_id in self.LB[0]:  # Neighbor already assigned
                neighbor_value = self.LB[0][neighbor_id]
                if not self.satisfies_constraint(current_agent.id, value, neighbor_id, neighbor_value):
                    return False
        return True



    def satisfies_constraint(self, agent_id, agent_value, neighbor_id, neighbor_value):
        """
        Check if the pair (agent_value, neighbor_value) satisfies the constraints.
        """
        return True  # Replace with your specific logic

    def cost_of_adding_to_lb(self, current_agent, d):
        pa = self.LB[0]
        sum = 0
        for other_agent,value in pa.items():
            if other_agent in current_agent.neighbors_agents_id:
                neighbors_obj = current_agent.neighbors_obj_dict[other_agent]
                cost = neighbors_obj.get_cost(current_agent.id_, d, other_agent, value)
                if cost is None:  # Skip infeasible assignments
                    return float('inf')
                sum +=cost


            if current_agent.id_ in current_agent.neighbors_obj_dict:
                neighbors_obj = current_agent.neighbors_obj_dict[current_agent.id_]
                cost = neighbors_obj.get_cost(current_agent.id_, d, current_agent.id_, d)
                sum += cost


        return sum

    def sort_domain_by_cost(self,current_agent):
        cost_for_each_domain = {}
        for d in current_agent.domain:
            cost_for_each_domain[d] = self.cost_of_adding_to_lb(current_agent, d)
        domain = sorted(cost_for_each_domain.keys(), key=cost_for_each_domain.get)
        return domain,cost_for_each_domain




