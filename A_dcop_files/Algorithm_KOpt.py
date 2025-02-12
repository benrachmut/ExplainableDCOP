import copy
import random
from copy import deepcopy

from networkx.classes import neighbors
from networkx.utils.misc import groups

from A_dcop_files.Algorithm_BnB_Central import Bnb_central
from B_xdcop_files.Queries import AgentForEducatedQuery
from Globals_ import max_iteration_k


class Group():
    def __init__(self, agents_in_group,neighbors_of_agents,all_agents):
        self.all_agents = all_agents
        self.agents_in_group = agents_in_group
        self.neighbors_of_agents = neighbors_of_agents
        self.LR = None

        self.LR_of_neighbors_dict = {}
        for n_id in neighbors_of_agents:
            self.LR_of_neighbors_dict[n_id] = None

    def get_current_context(self):
        ans = {}
        for a_id, a_obj in self.agents_in_group.items():
            ans[a_id] = a_obj.variable
        return ans
    def calculate_cost_of_group(self,context_):
        total_cost = 0
        for a_id, a_obj in self.agents_in_group.items():
            total_cost = total_cost+a_obj.calculate_cost_given_context(context_)
        return total_cost
    def calculate_LR(self):
        current_context = self.get_current_context()
        current_cost = self.calculate_cost_of_group(current_context)
        best_context = self.get_best_context()
        best_potential_cost = self.calculate_cost_of_group(best_context)

        if best_potential_cost-current_cost>0:
            self.LR = best_potential_cost-current_cost
        else: self.LR = 0

    def create_agents_for_k_opt(self):
        ans = []
        for agent_object in self.all_agents:
            id_ = copy.deepcopy(agent_object.id_)
            solution_value = agent_object.variable
            full_domain_list = copy.deepcopy(agent_object.domain)
            if id_ in self.agents_in_group.keys():
                domain_list = full_domain_list
            else:
                domain_list = [solution_value]

            neighbors_obj = agent_object.neighbors_obj
            neighbors_obj_dict = agent_object.neighbors_obj_dict
            neighbors_agents_id = copy.deepcopy(agent_object.neighbors_agents_id)
            a = AgentForEducatedQuery(id_, domain_list, neighbors_obj, neighbors_obj_dict, neighbors_agents_id, None)
            ans.append(a)
        return ans
            #ans[algo].append(a)





    def get_best_context(self):
        create_dummy_agents = self.create_agents_for_k_opt()
        bnb = Bnb_central(create_dummy_agents)
        dcop_solution = bnb.UB
        dict_ = dcop_solution[0]
        selected_context = {}
        for a_id in self.agents_in_group.keys():
            selected_context[a_id] = dict_[a_id]
        return selected_context
    def calculate_current_cost(self):
        cost = 0
        for a_id, a_object in self.agents_in_group.items():
            cost = cost + a_object.calc_local_price()
        return cost

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
        while self.iteration<self.max_iteration:
            groups = self.create_groups_of_k()
            self.calculate_LR_per_group(groups)
            self.group_change_if_can()
            if self.all_LR_is_zero():
                break
            self.iteration = self.iteration+1

    def calculate_LR_per_group(self,groups):
        for group in groups:
            group.calculate_LR()
    def insert_first_agent_to_group(self,agents_in_group,agents_non_colored):
        agent_id = self.rnd_group_selection.choice(list(agents_non_colored.keys()))
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
            agents_in_group_dict = {}
            neighbors_in_group_list = []
            first_agent_id = self.insert_first_agent_to_group(agents_in_group_dict,agents_non_colored)
            self.add_neighbors_to_neighbors_in_group(neighbors_in_group_list,agents_in_group_dict[first_agent_id])

            current_k = self.K-1

            while current_k>0:
                agents_ids_to_select = self.potential_agent_id_to_add(neighbors_in_group_list,agents_non_colored)
                if agents_ids_to_select is None:
                    break
                agent_id_to_add = self.rnd_group_selection.choice(agents_ids_to_select)
                agents_in_group_dict[agent_id_to_add] = agents_non_colored[agent_id_to_add]
                del agents_non_colored[agent_id_to_add]
                self.add_neighbors_to_neighbors_in_group(neighbors_in_group_list,  agents_in_group_dict[agent_id_to_add])
                current_k = current_k - 1
            ans.append(Group(agents_in_group_dict,neighbors_in_group_list,self.agents))
        return ans


    def potential_agent_id_to_add(self,neighbors_in_group_list,agents_non_colored):
        agents_ids_to_select = []
        for neighbor_in_group_id in neighbors_in_group_list:
            if self.id_in_non_colored_agents(agents_non_colored, neighbor_in_group_id):
                agents_ids_to_select.append(neighbor_in_group_id)
        if len(agents_ids_to_select) == 0:
            return None
        return agents_ids_to_select

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
