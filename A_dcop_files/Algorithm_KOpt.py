import random

from networkx.classes import neighbors
from networkx.utils.misc import groups

from Globals_ import max_iteration_k


class Group():
    def __init__(self, agents):
        self.agents = agents
        self.neighbors_of_agents = self.get_neighbors_get_neighbors_of_agents()
        self.LR = None
        self.LR_of_neighbors_dict = None

class K_Opt:
    def __init__(self,  K,agents,dcop_id):
        self.K = K
        self.max_t = K
        self.iteration = 0
        self.how_many_back = 10
        self.rnd_group_selection = random.Random((dcop_id+1)*179)
        for _ in range(5):
            self.rnd_group_selection.random()


        self.max_iteration = max_iteration_k
        self.agents = agents
        self.agents_dict = {}
        for agent in self.agents: self.agents_dict[agent.id_] = agent

        self.global_cost = {}

        self.solve()

    def all_select_random_value(self):
        for a in self.agents:
            a.select_random_value()
    def solve(self):
        self.all_select_random_value()
        self.calculate_global_cost()
        while self.is_converge() == False and self.iteration<self.max_iteration:
            groups = self.create_groups_of_k()
            self.calculate_LR_per_group(groups)
            self.group_change_if_can

            self.iteration = self.iteration+1

    def insert_first_agent_to_group(self,agents_in_group,agents_non_colored):
        agent_id = self.rnd_group_selection.choice(agents_non_colored.keys())
        agents_in_group[agent_id] = agents_non_colored[agent_id]
        del agents_non_colored[agent_id]
        return agent_id

    def add_neighbors_to_neighbors_in_group(self,neighbors_in_group_list,agent):
        if agent.id_ in neighbors_in_group_list:
             neighbors_in_group_list.remove(agent.id_)
        for neighbor_id in agent.neighbors_agents_id:
            if neighbor_id not in neighbors_in_group_list:
                neighbors_in_group_list.append(neighbor_id)



    def create_groups_of_k(self):
        agents_non_colored = {}
        for agent in self.agents:
            agents_non_colored[agent.id_] = agent
        ans = []
        while len(agents_non_colored)>0:
            agents_in_group = {}
            neighbors_in_group_list = []
            first_agent_id = self.insert_first_agent_to_group(agents_in_group,agents_non_colored)
            self.add_neighbors_to_neighbors_in_group(neighbors_in_group_list,agents_in_group[first_agent_id])
            current_k = self.K-1

            while current_k>0:
                agents_ids_to_select = []
                for neighbor_in_group_id in neighbors_in_group_list:
                    if self.id_in_non_colored_agents(agents_non_colored,neighbor_in_group_id):
                        agents_ids_to_select.append(neighbor_in_group_id)
                if len(agents_ids_to_select)==0:
                    break

                agent_id_to_add = self.rnd_group_selection.choice(agents_ids_to_select)
                for agent in agents_non_colored:

                current_k = self.K - 1

    def id_in_non_colored_agents(self,agents_non_colored,neighbor_in_group_id):
        for agent_id in agents_non_colored.keys():
            if agent_id==neighbor_in_group_id:
                return True
        return False













    def is_converge(self):

        prev_global_cost_list = []
        for i in range(1,self.how_many_back):
            if len(self.global_cost)<self.how_many_back+1:
                return False
            else:
                prev_global_cost_list.append(self.global_cost[self.iteration-i-1])

        for per_cost in prev_global_cost_list:
            if per_cost !=  self.global_cost[self.iteration]:
                return False
        return True

    def calculate_global_cost(self):
        cost = 0
        for a in self.agents:
            cost  = cost + a.calc_local_price()
        self.global_cost[self.iteration] = cost
