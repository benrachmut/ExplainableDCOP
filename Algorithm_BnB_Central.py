import copy
from Globals_ import *



class Bnb_central:
    def __init__(self, agents):
        # Sort agents based on the number of neighbors, descending
        self.agents = sorted(agents, key=lambda x: len(x.neighbors_agents_id), reverse=True)

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

        # Base case: If all levels are assigned, check and update UB
        if level == len(self.levels_dict_agents):
            if len(self.LB[0]) == len(self.agents) and self.UB[1] > self.LB[1]:
                self.UB = copy.deepcopy(self.LB)
            return

        # Get current agent and its domain
        current_agent = self.levels_dict_agents[level]
        if central_bnb_debug:
            print(current_agent,"start solve at level",level,"LB:",self.LB)

        domain,cost_for_each_domain = self.sort_domain_by_cost(current_agent)

        for value in domain:
            # Check if assigning this value is consistent with the current LB
            #if self.is_consistent_with_lb(level, current_agent, value):
                # Assign the value and update LB
            self.LB[0][current_agent.id_] = value
            self.LB[1] += cost_for_each_domain[value]

            # Prune branches if the current LB exceeds UB
            if self.LB[1] < self.UB[1]:
                self.solve(level + 1)

            if central_bnb_debug:
                print(current_agent,"was not add to LB with value:",value,"because UB = ",self.UB,"and LB",self.LB)
            # Backtrack: Remove the value and restore the LB
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
                sum +=neighbors_obj.get_cost(current_agent.id_,d, other_agent,value)
        return sum

    def sort_domain_by_cost(self,current_agent):
        cost_for_each_domain = {}
        for d in current_agent.domain:
            cost_for_each_domain[d] = self.cost_of_adding_to_lb(current_agent, d)
        domain = sorted(cost_for_each_domain.keys(), key=cost_for_each_domain.get)
        return domain,cost_for_each_domain




