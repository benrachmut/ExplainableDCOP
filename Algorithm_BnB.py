import math
from enum import Enum

import globals_
import problems
from Trees import *
from agents import *
from globals_ import *

class BNB_msg_type(Enum):
    token_from_father = 1
    token_from_child = 2


class BNB_Status(Enum):
    hold_token_need_to_send_down = 1
    finished_current_role_in_tree = 2
    receive_token_from_father_continue_to_send_down = 3
    receive_token_from_father_find_best_value = 4
    wait_for_token_after_sending_to_children = 5
    wait_for_all_tokens_from_children = 6
    receive_all_tokens_from_children = 7
    finished_going_over_domain = 8

class ShouldPruneException(Exception):
    def __init__(self, message=""):
        Exception.__init__(self)
        print("\033[91m"+message+"\033[0m")


class BranchAndBoundToken:
    def __init__(self, UB_global = math.inf, UB_local = math.inf, LB = 0, variables = {}, heights = {}):
        self.UB_global= UB_global
        self.UB_local = UB_local
        self.LB = LB
        self.variables = variables
        self.heights = heights


    def __add__(self, other):

        new_variables = self.merge_variables(other)
        new_heights = self.merge_heights(other)
        if other.UB_global != self.UB_global:
            raise Exception("should be equal")

        ans = BranchAndBoundToken(UB_global= other.UB_global,variables=new_variables,heights=new_heights)
        ans.update_cost()
        ans.UB_local= ans.LB
        return ans

    def create_reseted_token(self,id_):
        new_variables = self.reset_variables(id_)
        ans = BranchAndBoundToken(UB_global = self.UB_global, UB_local = self.UB_local, LB = 0, variables = new_variables, heights = self.heights)
        ans.update_cost()
        return ans




    def agent_include_in_variables(self,id_):
        if id_ in self.variables.keys():
            return True
        else:
            return False


    def add_agent_to_token_variables(self,id_,value,local_cost):
        if self.agent_include_in_variables(id_):
            raise Exception("used it when agent is already in token")
        self.variables[id_] = (value,local_cost)
        if  id_ not in self.heights.keys():
            if len(self.heights)==0:
                self.heights[id_] = 1
            else:
                self.heights[id_] = max(self.heights.values())+1
        self.update_cost()

    def update_cost(self):
        costs = []
        for n_id, tuple_ in self.variables.items():
            costs.append(tuple_[1])
        #costs =  {key: sum(value) for key, value in self.variables.items()}.values()

        self.LB = sum(costs)
        if self.LB>=self.UB_global:
            raise ShouldPruneException("LB>UB_global move to the next domain LB="+str(self.LB)+" UB_global="+str(self.UB_local))
        if self.LB>=self.UB_local:
            raise ShouldPruneException("LB>UB_local move to the next domain LB="+str(self.LB)+" UB_global="+str(self.UB_local))

    def get_variable_dict(self,agent_list_id):
        ans = {}
        for n_id in agent_list_id:
            ans[n_id] = next(iter(self.variables[n_id]))

            #ans[n_id] = self.variables[n_id][0]
        return ans
    def __str__(self):
        return "UB:" + str(self.UB_global) + ", LB:" + str(self.LB) + ", context:" + str(self.variables)

    def __deepcopy__(self, memodict={}):
        variables_to_send = {}
        for k,v in self.variables.items():
            variables_to_send[k] = v

        heights_to_send = {}
        for k, v in self.heights.items():
            heights_to_send[k] = v
        return BranchAndBoundToken(UB_global = self.UB_global,UB_local= self.UB_local,
                                   LB = self.LB, variables = variables_to_send, heights = heights_to_send)

    def merge_heights(self, other):
        merged_dict = {}
        # Merge keys from both dictionaries
        all_keys = set(self.variables.keys()) | set(other.variables.keys())

        for key in all_keys:
            value_dict1 = self.heights.get(key)
            value_dict2 = other.heights.get(key)

            if value_dict1 is not None and value_dict2 is not None:
                if value_dict1 != value_dict2:
                    raise ValueError(f"Conflict for key {key}: {value_dict1} != {value_dict2}")
                else:
                    merged_dict[key] = value_dict1
            elif value_dict1 is not None:
                merged_dict[key] = value_dict1
            elif value_dict2 is not None:
                merged_dict[key] = value_dict2

        return merged_dict

    def merge_variables(self, other):
        merged_dict = {}
        # Merge keys from both dictionaries
        all_keys = set(self.variables.keys()) | set(other.variables.keys())

        for key in all_keys:
            value_dict1 = self.variables.get(key)
            value_dict2 = other.variables.get(key)

            if value_dict1 is not None and value_dict2 is not None:
                if value_dict1 != value_dict2:
                    raise ValueError(f"Conflict for key {key}: {value_dict1} != {value_dict2}")
                else:
                    merged_dict[key] = value_dict1
            elif value_dict1 is not None:
                merged_dict[key] = value_dict1
            elif value_dict2 is not None:
                merged_dict[key] = value_dict2

        return merged_dict

    def reset_variables(self,id_):
        ans = {}
        height_of_id = self.heights[id_]
        for n_id, dict_ in self.variables.items():
            height_of_neighbor = self.heights[n_id]
            if height_of_id > height_of_neighbor:
                ans[n_id] = dict_
        return ans

class BranchAndBound(DFS,CompleteAlgorithm):
    def __init__(self, id_, D):
        DFS.__init__(self, id_, D)
        self.domain_index = -1
        self.bnb_token = None
        self.tokens_from_children = {}

        self.local_token = None


#################
#### Main methods ####
#################

    def is_algorithm_complete(self):
        return False


    def update_msgs_in_context_tree(self,msgs):
        for msg in msgs:
            if msg.msg_type == BNB_msg_type.token_from_father:
                self.update_msgs_in_context_tree_receive_token_from_father(msgs)
            if msg.msg_type == BNB_msg_type.token_from_child:
                self.tokens_from_children[msg.sender] = msg.information.__deepcopy__()





    def change_status_after_update_msgs_in_context_tree(self, msgs):

        self.senity_check_1(msgs)

        if msgs[0].msg_type == BNB_msg_type.token_from_father:
            if len(self.dfs_children)==0:
                self.status = BNB_Status.receive_token_from_father_find_best_value
            else:
                self.status = BNB_Status.receive_token_from_father_continue_to_send_down
        if msgs[0].msg_type == BNB_msg_type.token_from_child:
            if self.change_status_is_receive_token_back_from_all_children():
                self.status = BNB_Status.receive_all_tokens_from_children
            else:
                self.status = BNB_Status.wait_for_all_tokens_from_children

        if debug_BNB:
            print(self.__str__(),"status is:", self.status)

    def is_compute_in_this_iteration_tree(self):
        if  self.status == BNB_Status.receive_token_from_father_find_best_value\
            or self.status == BNB_Status.receive_token_from_father_continue_to_send_down\
            or BNB_Status.receive_all_tokens_from_children:

            return True
        else:
            return False

    def compute_tree(self):
        if self.root_of_tree_start_algorithm:
            self.compute_root_starts_the_algorithm()
        if self.status == BNB_Status.receive_token_from_father_continue_to_send_down:
            self.compute_select_value_for_variable()
        if self.status == BNB_Status.receive_all_tokens_from_children and not self.am_i_root():
            self.compute_receive_all_tokens_from_children_not_root()
        if self.status == BNB_Status.receive_all_tokens_from_children and self.am_i_root():
            self.compute_receive_all_tokens_from_children_yes_root()

        if self.status == BNB_Status.receive_token_from_father_find_best_value:
            min_cost = self.compute_select_value_with_min_cost()
            self.update_token(min_cost)

        if self.status == BNB_Status.finished_going_over_domain:
            self.bnb_token = self.local_token.__deepcopy__()



    def send_msgs_tree(self):
        if self.status == BNB_Status.hold_token_need_to_send_down or \
                self.status == BNB_Status.receive_token_from_father_continue_to_send_down:
            self.sends_msgs_token_down_the_tree()
        if self.status == BNB_Status.receive_token_from_father_find_best_value:
            self.sends_msgs_token_up_the_tree()

        if self.status == BNB_Status.receive_all_tokens_from_children:
            self.sends_msgs_token_down_the_tree()

        if self.status == BNB_Status.finished_going_over_domain:
            self.sends_msgs_token_up_the_tree()




    def change_status_after_send_msgs_tree(self):
        old_statues = self.status
        if self.status == BNB_Status.hold_token_need_to_send_down or \
                self.status == BNB_Status.receive_token_from_father_continue_to_send_down:
            self.status = BNB_Status.wait_for_token_after_sending_to_children

        if self.status == BNB_Status.receive_token_from_father_find_best_value:
           self.status = BNB_Status.finished_current_role_in_tree

        if self.status == BNB_Status.receive_all_tokens_from_children:
            self.status = BNB_Status.wait_for_token_after_sending_to_children

        if self.status == BNB_Status.finished_going_over_domain:
            self.local_token = None
            self.status = BNB_Status.finished_current_role_in_tree


        self.bnb_token = None

        if debug_BNB:
            print(self.__str__(), "when finish iteration status was:",old_statues,"and now status updated to", self.status)

    def should_record_this_iteration(self): pass

    def record(self): pass

    #################
    #### update in context ####
    #################

    def update_msgs_in_context_tree_receive_token_from_father(self, msgs):
        if len(msgs) > 1:
            raise Exception("should receive a single msg")
        self.bnb_token = msgs[0].information.__deepcopy__()
        #self.bnb_token_local =self.bnb_token.__deepcopy__()



    #################
    #### COMPUTE ####
    #################

    def compute_select_value_for_variable(self):
        self.domain_index = self.domain_index + 1
        self.reset_tokens_from_children()

        if debug_BNB:
            print(self,  "domain index is ",self.domain_index)
        while self.domain_index<len(self.domain):
            self.variable = self.domain[self.domain_index]
            if self.dfs_father is None:
                return
            else:
                current_context = self.bnb_token.get_variable_dict(self.above_me)
                local_cost = self.calc_local_price(current_context)
                self.update_token(local_cost)
                return True

        else:
            self.status = BNB_Status.finished_going_over_domain
            self.domain_index = -1

    def compute_root_starts_the_algorithm(self):
        self.compute_select_value_for_variable()
        if debug_DFS_draw_tree:
            globals_.draw_dfs_tree_flag = True
        self.status = BNB_Status.hold_token_need_to_send_down
        self.root_of_tree_start_algorithm = False
        self.bnb_token = BranchAndBoundToken()
        self.bnb_token.add_agent_to_token_variables(id_=self.id_, value=self.variable, local_cost=0)
        self.reset_tokens_from_children()
        if debug_BNB:
            print("root",self.__str__(),"selects value:",self.variable," and creates token",self.bnb_token.__str__())

    def reset_tokens_from_children(self):
        self.tokens_from_children = {}
        for n_id in self.dfs_children:
            self.tokens_from_children[n_id] = None

    def compute_select_value_with_min_cost(self):
        current_context = self.bnb_token.get_variable_dict(self.above_me)
        potential_value_and_cost = {}
        for potential_domain in self.domain:
            potential_cost = self.calc_potential_cost(potential_domain, current_context)
            potential_value_and_cost[potential_domain] = potential_cost
        self.variable = min(potential_value_and_cost, key=lambda k: potential_value_and_cost[k])
        return potential_value_and_cost[self.variable]

    def calc_local_price(self, current_context):
        local_cost = 0
        for n_id, current_value in current_context.items():
            neighbor_obj = self.get_n_obj(n_id)
            local_cost = local_cost + neighbor_obj.get_cost(self.id_, self.variable, n_id, current_value)
        return local_cost

    def get_n_obj(self, n_id):
        for ans in self.neighbors_obj:
            if ans.is_agent_in_obj(agent_id_input=n_id):
                return ans

        if ans is None:
            raise Exception("n_id is not correct")

    def calc_potential_cost(self, potential_domain, current_context):
        local_cost = 0
        for n_id, current_value in current_context.items():
            neighbor_obj = self.get_n_obj(n_id)
            local_cost = local_cost + neighbor_obj.get_cost(self.id_, potential_domain, n_id, current_value)
        return local_cost

    def update_token(self, local_cost):

        try:
            self.bnb_token.add_agent_to_token_variables(id_=self.id_, value=self.variable, local_cost=local_cost)
            return True

        except ShouldPruneException:
            if debug_BNB:
                print(self.__str__(), "pruned", self.domain_index,"token:",self.bnb_token)
            self.domain_index = self.domain_index + 1
    #################
    #### send message ####
    #################
    def sends_msgs_token_down_the_tree(self):
        sender = self.id_
        msgs = []
        for receiver in self.dfs_children:
            temp_token = self.bnb_token.__deepcopy__()
            msg = Msg(sender=sender, receiver=receiver, information=temp_token,
                      msg_type=BNB_msg_type.token_from_father)
            msgs.append(msg)
        self.outbox.insert(msgs)
        if debug_BNB:
            print(self.__str__(), "sends messages to its children:",self.dfs_children)

    def sends_msgs_token_up_the_tree(self):
        msg = Msg(sender=self.id_,receiver=self.dfs_father,information=self.bnb_token.__deepcopy__(),msg_type=BNB_msg_type.token_from_child)
        self.outbox.insert([msg])

    def senity_check_1(self,msgs):
        if len(msgs) > 1:
            if msgs[0].msg_type != msgs[1].msg_type:
                raise Exception("by logic it does not make any sense to receive two types of msgs at the same time")

    #################
    #### change_status_after_update_msgs_in_context_tree ####
    #################

    def change_status_is_receive_token_back_from_all_children(self):
        for v in self.tokens_from_children.values():
            if v is None:
                return False
        return True

    def compute_receive_all_tokens_from_children_not_root(self):
        self.update_local_token()
        self.reset_tokens_from_children()
        self.create_local_token_after_receive_from_children()


    def update_local_token(self):
        local_token_temp = None
        for child_token in self.tokens_from_children.values():
            if local_token_temp is None:
                local_token_temp = child_token
            else:
                local_token_temp = local_token_temp + child_token

        if self.local_token is None:
            self.local_token = local_token_temp
        elif self.local_token.UB_local < local_token_temp.UB_local:
            self.local_token = local_token_temp

    def create_local_token_after_receive_from_children(self):
        self.bnb_token = self.local_token.create_reseted_token(self.id_)
        self.compute_select_value_for_variable()

    def am_i_root(self):
        return self.dfs_father is None

    def compute_receive_all_tokens_from_children_yes_root(self):
        need  to  check to local token and reset and create  new bnb token and check for new global up









