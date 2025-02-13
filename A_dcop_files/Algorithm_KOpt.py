import copy
import random
from copy import deepcopy
from itertools import product

from networkx.classes import neighbors
from networkx.utils.misc import groups

from A_dcop_files.Algorithm_BnB_Central import Bnb_central
from B_xdcop_files.Queries import AgentForEducatedQuery
from Globals_ import *


class Group:
    def __init__(self, agents_in_group,neighbors_of_agents,all_agents):
        self.all_agents = all_agents
        self.agents_in_group = agents_in_group
        self.neighbors_of_agents = neighbors_of_agents
        self.LR = None
        self.best_context = None
        self.best_cost = None

        self.LR_leaders_dict = {}
        self.group_leader = min(self.agents_in_group.keys())
        #for n_id in neighbors_of_agents:
        #    self.LR_of_neighbors_dict[n_id] = None

    def add_learder(self,leader_id):
        self.LR_leaders_dict[leader_id] = None


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
        self.best_context,self.best_cost = self.get_best()


        ids_list = list(self.agents_in_group.keys())
        for first_agent_index in range(len(ids_list)):
            first_id = ids_list[first_agent_index]
            first_agent = self.agents_in_group[first_id]
            for second_agent_index in range(first_agent_index+1, len(ids_list)):
                second_id = ids_list[second_agent_index]
                second_agent = self.agents_in_group[second_id]
                if first_id in second_agent.neighbors_agents_id:
                    n_obj = second_agent.neighbors_obj_dict[first_id]
                    inner_cost_best = n_obj.get_cost( first_id, self.best_context[first_id], second_id, self.best_context[second_id])
                    inner_cost_current = n_obj.get_cost( first_id, self.agents_in_group[first_id].variable, second_id, self.agents_in_group[second_id].variable)
                    self.best_cost = self.best_cost-inner_cost_best
                    current_cost = current_cost-inner_cost_current
        if current_cost-self.best_cost >0:
            self.LR =  current_cost-self.best_cost
        else:
            self.LR = 0

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

    from itertools import product

    def generate_assignments(self,agent_domains):
        agents = list(agent_domains.keys())
        values_combinations = product(*agent_domains.values())

        return [dict(zip(agents, values)) for values in values_combinations]

    def create_agents_domain_dict(self):
        ans = {}
        for a_id,a_obj in self.agents_in_group.items():
            ans[a_id] = a_obj.domain
        return ans

    def get_best(self):
        agents_domains = self.create_agents_domain_dict()
        assignments = self.generate_assignments(agents_domains)
        best_context = min(assignments,key=self.calculate_cost_of_group)
        best_cost = self.calculate_cost_of_group(best_context)

        return best_context,best_cost
        #create_dummy_agents = self.create_agents_for_k_opt()
        #bnb = Bnb_central(create_dummy_agents)
        #dcop_solution = bnb.UB
        #dict_ = dcop_solution[0]
        #selected_context = {}
        #for a_id in self.agents_in_group.keys():
        #    selected_context[a_id] = dict_[a_id]
        #return selected_context
    def calculate_current_cost(self):
        cost = 0
        for a_id, a_object in self.agents_in_group.items():
            cost = cost + a_object.calc_local_price()
        return cost

    def inform_LR(self,group_sender):
        lr_of_sender = group_sender.LR
        leader_of_sender = group_sender.group_leader
        if leader_of_sender in self.LR_leaders_dict.keys():
            self.LR_leaders_dict[leader_of_sender] = lr_of_sender

    def change_values_if_can(self):
        max_lr = max(list(self.LR_leaders_dict.values()))

        if max_lr > self.LR:
            return
        if max_lr == self.LR:
            leaders_of_max_lr = []
            for id_,lr in self.LR_leaders_dict.items():
                if lr == max_lr:
                    leaders_of_max_lr.append(id_)
            if self.group_leader>min(leaders_of_max_lr):
                return
        if self.LR>0:
            #print("Group leader:",self.group_leader,"LR:",self.LR)
            for a_id, agent in self.agents_in_group.items():
                agent.variable = self.best_context[a_id]

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
        if debug_k_opt:
            print(self.iteration, ",", self.global_cost[self.iteration])
        while self.iteration<self.max_iteration:
            self.iteration = self.iteration+1

            groups,groups_dict = self.create_groups_of_k()
            for group in groups:group.groups_dict = groups_dict
            self.connect_group_leaders(groups)
            self.calculate_LR_per_group(groups)
            self.inform_all_groups(groups)
            self.check(groups)
            self.group_change_if_can(groups)
            #if self.all_LR_is_zero(groups):
            #    break
            self.calculate_global_cost()
            if debug_k_opt:
                print(self.iteration,",",self.global_cost[self.iteration],",",self.global_cost[self.iteration-1]-self.global_cost[self.iteration])

    def connect_group_leaders(self,groups):
        for first_group_index in range(len(groups)):
            first_group = groups[first_group_index]
            agents_in_first_group_dict = first_group.agents_in_group
            for second_group_index in range(first_group_index+1,len(groups)):
                second_group = groups[second_group_index]
                neighbors_in_second_group = second_group.neighbors_of_agents
                for agent_id_in_first in agents_in_first_group_dict.keys():
                    if agent_id_in_first in neighbors_in_second_group:
                        first_group.add_learder(second_group.group_leader)
                        second_group.add_learder(first_group.group_leader)
                        break
    def all_LR_is_zero(self,groups):
        for group in groups:
            if group.LR !=0:
                return False
        return True

    def group_change_if_can(self,groups):
        for group in groups:
            group.change_values_if_can()

    def check(self,groups):
        for group in groups:
            if None in group.LR_leaders_dict.values() and group.LR is None:
                raise Exception("did not inform all ")


    def inform_all_groups(self,groups):
        for group_sender in groups:
            for group_receiver in groups:
                group_receiver.inform_LR(group_sender)

    def calculate_LR_per_group(self,groups):
        for group in groups:
            group.calculate_LR()

    def insert_first_agent_to_group(self,agents_in_group,agents_non_colored):
        agent_id = self.rnd_group_selection.choice(list(agents_non_colored.keys()))
        agents_in_group[agent_id] = agents_non_colored[agent_id]
        del agents_non_colored[agent_id]
        return agent_id

    def add_neighbors_to_neighbors_in_group(self,neighbors_in_group_list,agent,agents_in_group_dict):
        if agent.id_ in neighbors_in_group_list:
             neighbors_in_group_list.remove(agent.id_)
        for neighbor_id in agent.neighbors_agents_id:

            if neighbor_id not in neighbors_in_group_list and neighbor_id not in agents_in_group_dict.keys():
                neighbors_in_group_list.append(neighbor_id)



    def create_groups_of_k(self):
        agents_non_colored = {}
        for agent in self.agents:
            agents_non_colored[agent.id_] = agent
        ans = []
        groups_dict ={}
        while len(agents_non_colored)>0:
            agents_in_group_dict = {}
            neighbors_in_group_list = []
            first_agent_id = self.insert_first_agent_to_group(agents_in_group_dict,agents_non_colored)
            self.add_neighbors_to_neighbors_in_group(neighbors_in_group_list,agents_in_group_dict[first_agent_id],agents_in_group_dict)

            current_k = self.K-1

            while current_k>0:
                agents_ids_to_select = self.potential_agent_id_to_add(neighbors_in_group_list,agents_non_colored)
                if agents_ids_to_select is None:
                    break
                agent_id_to_add = self.rnd_group_selection.choice(agents_ids_to_select)
                agents_in_group_dict[agent_id_to_add] = agents_non_colored[agent_id_to_add]
                del agents_non_colored[agent_id_to_add]
                self.add_neighbors_to_neighbors_in_group(neighbors_in_group_list,  agents_in_group_dict[agent_id_to_add],agents_in_group_dict)
                current_k = current_k - 1
            updated_neighbors_list = []
            for n_id in neighbors_in_group_list:
                if n_id not in agents_in_group_dict.keys():
                    updated_neighbors_list.append(n_id)
            groups_dict[min(agents_in_group_dict.keys())] = list(agents_in_group_dict.keys())
            ans.append(Group(agents_in_group_dict,updated_neighbors_list,self.agents))
        return ans,groups_dict


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















    def calculate_global_cost(self):
        cost = 0
        for a in self.agents:
            cost  = cost + a.calc_local_price()
        self.global_cost[self.iteration] = cost/2

