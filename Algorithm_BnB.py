import math
from enum import Enum

from Scripts._testmultiphase import Example

import globals_
import problems
from Trees import *
from agents import *
from globals_ import *

class BNB_msg_type(Enum):
    token_from_father = 1
    token_from_child = 2
    token_empty = 3


class BNB_Status(Enum):
    hold_token_send_down = 1
    finished_going_over_domain = 2
    finished_temp_role_in_tree = 3

    wait_tokens_from_children = 4

    receive_token_from_father_mid = 5
    receive_token_from_father_leaf = 6
    receive_token_from_all_children = 7

    send_token_to_children = 8
    send_empty_to_father = 9
    send_token_to_father = 10
    send_best_local_token_to_father = 11

    receive_all_tokens_from_children = 12
    #receive_token_from_father = 10


    ####


class ShouldPruneException(Exception):
    def __init__(self, message=""):
        Exception.__init__(self)
        print("\033[91m"+message+"\033[0m")


class BranchAndBoundToken:
    def __init__(self, best_token = None, UB = None, LB = 0, variables=None, heights=None):
        if heights is None:
            heights = {}
        if variables is None:
            variables = {}
        self.best_token= best_token
        self.UB = UB
        self.LB = LB
        self.variables = variables
        self.heights = heights

    def __add__(self, other):

        new_variables = self.merge_variables(other)
        new_heights = self.merge_heights(other)


        ans = BranchAndBoundToken(best_token= other.best_token, variables=new_variables, heights=new_heights)
        ans.update_cost()

        variables_to_send = {}
        for k, v in self.variables.items():
            variables_to_send[k] = v

        ans.UB= (ans.LB,variables_to_send)

        # todo check if best variables is the same if not there is a bug raise exp
        return ans

    def create_reseted_token(self,id_):
        new_variables = self.reset_variables(id_)
        ans = BranchAndBoundToken(best_token = self.best_token, UB= self.UB, LB = 0, variables = new_variables, heights = self.heights)
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

        best_token = self.best_token
        if best_token is not None and self.LB>=best_token.UB[0]:
            raise ShouldPruneException("LB>UB_global move to the next domain LB=" + str(self.LB) +" UB_global=" + str(best_token.UB))

        if self.UB is not None and self.LB>=self.UB[0]:
            raise ShouldPruneException("LB>UB_local move to the next domain LB=" + str(self.LB) +" UB_local=" + str(self.UB))

    def get_variable_dict(self,agent_list_id):
        ans = {}
        for n_id in agent_list_id:
            ans[n_id] = next(iter(self.variables[n_id]))

            #ans[n_id] = self.variables[n_id][0]
        return ans
    def __str__(self):
        return "UB:" + str(self.UB) + ", LB:" + str(self.LB) + ", context:" + str(self.variables)

    def __deepcopy__(self, memodict={},flag = False):
        variables_to_send = {}
        for k,v in self.variables.items():
            variables_to_send[k] = v

        heights_to_send = {}
        for k, v in self.heights.items():
            heights_to_send[k] = v

        best_token = None
        if self.best_token is not None and not flag:
            best_token = self.best_token.__deepcopy__(flag = True)


        return BranchAndBoundToken(best_token = best_token, UB= self.UB,LB = self.LB, variables = variables_to_send, heights = heights_to_send)

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

class BranchAndBound_Try(DFS,CompleteAlgorithm):
    def __init__(self, id_, D):
        DFS.__init__(self, id_, D)
        self.domain_index = -1
        self.global_token = None
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
                self.status = BNB_Status.receive_token_from_father_leaf
            else:
                self.status = BNB_Status.receive_token_from_father_mid
        if msgs[0].msg_type == BNB_msg_type.token_from_child:
            if self.change_status_is_receive_token_back_from_all_children():
                self.status = BNB_Status.receive_all_tokens_from_children
            else:
                self.status = BNB_Status.wait_tokens_from_children

        if debug_BNB:
            print(self.__str__(),"status is:", self.status)

    def is_compute_in_this_iteration_tree(self):
        if  self.status == BNB_Status.receive_token_from_father_leaf\
            or self.status == BNB_Status.receive_token_from_father_mid\
            or BNB_Status.receive_all_tokens_from_children:

            return True
        else:
            return False

    def compute_tree(self):
        if self.root_of_tree_start_algorithm:
            self.compute_root_starts_the_algorithm()
        if self.status == BNB_Status.receive_token_from_father_mid:
            self.compute_select_value_for_variable()
        if self.status == BNB_Status.receive_all_tokens_from_children and not self.am_i_root():
            self.compute_receive_all_tokens_from_children_not_root()
        if self.status == BNB_Status.receive_all_tokens_from_children and self.am_i_root():
            self.compute_receive_all_tokens_from_children_yes_root()
        if self.status == BNB_Status.receive_token_from_father_leaf:
            min_cost = self.compute_select_value_with_min_cost()
            self.update_token(min_cost)
        if self.status == BNB_Status.finished_going_over_domain:
            self.global_token = self.local_token.__deepcopy__()



    def send_msgs_tree(self):
        if self.status == BNB_Status.hold_token_send_down or \
                self.status == BNB_Status.receive_token_from_father_mid:
            self.sends_msgs_token_down_the_tree()
        if self.status == BNB_Status.receive_token_from_father_leaf:
            self.sends_msgs_token_up_the_tree()

        if self.status == BNB_Status.receive_all_tokens_from_children:
            self.sends_msgs_token_down_the_tree()

        if self.status == BNB_Status.finished_going_over_domain:
            self.sends_msgs_token_up_the_tree()




    def change_status_after_send_msgs_tree(self):
        old_statues = self.status
        if self.status == BNB_Status.hold_token_send_down or \
                self.status == BNB_Status.receive_token_from_father_mid:
            self.status = BNB_Status.wait_tokens_from_children

        if self.status == BNB_Status.receive_token_from_father_leaf:
           self.status = BNB_Status.finished_temp_role_in_tree

        if self.status == BNB_Status.receive_all_tokens_from_children:
            self.status = BNB_Status.wait_tokens_from_children

        if self.status == BNB_Status.finished_going_over_domain:
            self.local_token = None
            self.status = BNB_Status.finished_temp_role_in_tree


        self.global_token = None

        if debug_BNB:
            print(self.__str__(), "when finish iteration status was:",old_statues,"and now status updated to", self.status)


    #################
    #### update in context ####
    #################

    def update_msgs_in_context_tree_receive_token_from_father(self, msgs):
        if len(msgs) > 1:
            raise Exception("should receive a single msg")
        self.global_token = msgs[0].information.__deepcopy__()
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
                current_context = self.global_token.get_variable_dict(self.above_me)
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
        self.status = BNB_Status.hold_token_send_down
        self.root_of_tree_start_algorithm = False
        self.create_global_bnb_token()

        if debug_BNB:
            print("root", self.__str__(),"selects value:", self.variable," and creates token", self.global_token.__str__())

    def reset_tokens_from_children(self):
        self.tokens_from_children = {}
        for n_id in self.dfs_children:
            self.tokens_from_children[n_id] = None

    def compute_select_value_with_min_cost(self):
        current_context = self.global_token.get_variable_dict(self.above_me)
        potential_value_and_cost = {}
        for potential_domain in self.domain:
            potential_cost = self.calc_potential_cost(potential_domain, current_context)
            potential_value_and_cost[potential_domain] = potential_cost
        self.variable = min(potential_value_and_cost, key=lambda k: potential_value_and_cost[k])
        return potential_value_and_cost[self.variable]



    def calc_potential_cost(self, potential_domain, current_context):
        local_cost = 0
        for n_id, current_value in current_context.items():
            neighbor_obj = self.get_n_obj(n_id)
            local_cost = local_cost + neighbor_obj.get_cost(self.id_, potential_domain, n_id, current_value)
        return local_cost

    def update_token(self, local_cost):

        try:
            self.global_token.add_agent_to_token_variables(id_=self.id_, value=self.variable, local_cost=local_cost)
            return True

        except ShouldPruneException:
            if debug_BNB:
                print(self.__str__(), "pruned", self.domain_index,"token:", self.global_token)
            self.domain_index = self.domain_index + 1
    #################
    #### send message ####
    #################
    def sends_msgs_token_down_the_tree(self):
        sender = self.id_
        msgs = []
        for receiver in self.dfs_children:
            temp_token = self.global_token.__deepcopy__()
            msg = Msg(sender=sender, receiver=receiver, information=temp_token,
                      msg_type=BNB_msg_type.token_from_father)
            msgs.append(msg)
        self.outbox.insert(msgs)
        if debug_BNB:
            print(self.__str__(), "sends messages to its children:",self.dfs_children)

    def sends_msgs_token_up_the_tree(self):
        msg = Msg(sender=self.id_, receiver=self.dfs_father, information=self.global_token.__deepcopy__(), msg_type=BNB_msg_type.token_from_child)
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
        self.global_token = self.local_token.create_reseted_token(self.id_)
        self.compute_select_value_for_variable()

    def am_i_root(self):
        return self.dfs_father is None

    def compute_receive_all_tokens_from_children_yes_root(self):
        self.compute_receive_all_tokens_from_children_not_root()
        self.create_global_bnb_token()
        self.global_token.best_global_token = self.local_token.__deepcopy__()


    def create_global_bnb_token(self):
        self.global_token = BranchAndBoundToken()
        self.global_token.add_agent_to_token_variables(id_=self.id_, value=self.variable, local_cost=0)
        self.reset_tokens_from_children()


class BranchAndBound(DFS,CompleteAlgorithm):
    def __init__(self, id_, D):
        DFS.__init__(self, id_, D)
        self.domain_index = -1
        self.best_global_token = None
        self.best_local_token = None
        self.token = None
        self.tokens_from_children = {}


    def is_algorithm_complete(self):
        return False

    def update_msgs_in_context_tree(self, msgs):
        for msg in msgs:
            if msg.msg_type == BNB_msg_type.token_from_father:
                self.recieve_token_from_father(msgs)
            if msg.msg_type == BNB_msg_type.token_from_child:
                self.tokens_from_children[msg.sender] = msg.information.__deepcopy__()
            if msg.msg_type == BNB_msg_type.token_empty:
                self.tokens_from_children[msg.sender] = object()
            if debug_BNB:
                print(self.__str__(), "receive", msg.msg_type,"from A_",msg.sender,"info:", msg.information)
    def change_status_after_update_msgs_in_context_tree(self, msgs):
        if debug_BNB:
            print(self.__str__(), "status WAS:", self.status)

        if msgs[0].msg_type == BNB_msg_type.token_from_father:
            if len(self.dfs_children) == 0:
                self.status = BNB_Status.receive_token_from_father_leaf
            else:
                self.status = BNB_Status.receive_token_from_father_mid


        if msgs[0].msg_type == BNB_msg_type.token_from_child or msgs[0].msg_type == BNB_msg_type.token_empty:
            if self.is_receive_from_all_children():
                if self.is_receive_tokens_from_all():
                    if self.dfs_father is not None:
                        self.status = BNB_Status.receive_all_tokens_from_children
                    else:
                        raise Exception("TODO need for root to aggregate")

                else:
                    raise Exception("TODO need to continue send up empty")
                    #self.status = BNB_Status.hold_token_send_down
                    #if self.best_local_token != None:
                    #    self.token = self.best_local_token.reset_token(self.id_)
            else:
                self.status = BNB_Status.wait_tokens_from_children



        if debug_BNB:
            print(self.__str__(), "status IS:", self.status)

    def is_compute_in_this_iteration_tree(self):
        return self.root_of_tree_start_algorithm or \
               self.status == BNB_Status.receive_token_from_father_mid or\
               self.status == BNB_Status.receive_token_from_father_leaf or \
               self.status == BNB_Status.receive_all_tokens_from_children


    def compute_tree(self):
        if self.root_of_tree_start_algorithm:
            self.compute_start_algorithm()
        if self.status == BNB_Status.receive_token_from_father_mid:
            self.compute_receive_token_from_father_mid()
        if self.status == BNB_Status.receive_token_from_father_leaf:
            self.compute_receive_token_from_father_leaf()
        if self.status == BNB_Status.receive_all_tokens_from_children:
            self.compute_receive_all_tokens_from_children()
        if debug_BNB:
            print(self.__str__(), "status IS:", self.status)

    def send_msgs_tree(self):
        if self.status == BNB_Status.hold_token_send_down or self.status == BNB_Status.send_token_to_children:
            self.sends_msgs_token_down_the_tree()

        if self.status == BNB_Status.send_token_to_father:
            self.sends_msgs_token_up_the_tree()


        if self.status == BNB_Status.send_best_local_token_to_father:
            self.sends_msgs_best_token_up_the_tree()


        if self.status == BNB_Status.send_empty_to_father:
            self.send_msgs_empty_up_the_tree()





    def change_status_after_send_msgs_tree(self):
        if self.status == BNB_Status.hold_token_send_down or self.status == BNB_Status.send_token_to_children:
            self.status = BNB_Status.wait_tokens_from_children

        if self.status == BNB_Status.send_token_to_father:
            self.status = BNB_Status.finished_temp_role_in_tree

        if self.status == BNB_Status.send_empty_to_father:
            self.status = BNB_Status.finished_temp_role_in_tree


        if debug_BNB:
            print(self.__str__(), "status IS:", self.status)

        self.token = None

    # update msgs #################################################################################################

    def recieve_token_from_father(self, msgs):
        if len(msgs) > 1:
            raise Exception("should receive a single msg")
        self.token = msgs[0].information.__deepcopy__()
        if self.token.best_token is not None:
            self.best_global_token = self.token.best_token.__deepcopy__()
            self.variable_anytime = self.best_global_token.variables[self.id_][0]

    # compute #################################################################################################

    def compute_start_algorithm(self):
        self.select_next_value()
        self.create_local_token_root()
        self.root_of_tree_start_algorithm = False
        self.status = BNB_Status.hold_token_send_down
        if debug_DFS_draw_tree:
            globals_.draw_dfs_tree_flag = True

    def select_next_value(self):
        self.domain_index = self.domain_index + 1
        self.reset_tokens_from_children()


        while self.domain_index < len(self.domain):
            self.variable = self.domain[self.domain_index]
            if debug_BNB:
                print(self, "variable changed to", self.variable)
            if self.dfs_father is None:
                return
            else:
                current_context = self.token.get_variable_dict(self.above_me)
                local_cost = self.calc_local_price(current_context)
                try:
                    self.token.add_agent_to_token_variables(id_=self.id_, value=self.variable,
                                                            local_cost=local_cost)
                    return True
                except ShouldPruneException:
                    winner = BranchAndBoundToken(  LB = self.token.UB[0], variables=self.token.UB[1], heights=None)
                    self.records.append((self.token.__deepcopy__(), winner.__deepcopy__()))
                    del self.token.variables[self.id_]
                    self.token.LB = self.token.LB - local_cost

                    self.domain_index = self.domain_index + 1

                    #raise Exception("TODO need to record it")


        else:
            self.status = BNB_Status.finished_going_over_domain
            self.domain_index = -1
            if debug_BNB:
                print(self, "finished going over domain", self.variable)

    def reset_tokens_from_children(self):
        self.tokens_from_children = {}
        for n_id in self.dfs_children:
            self.tokens_from_children[n_id] = None



    def compute_receive_token_from_father_mid(self):
        self.select_next_value()
        if self.token.agent_include_in_variables(self.id_):
            self.status = BNB_Status.send_token_to_children
        else:
            #self.status = BNB_Status.send_empty_to_father
            raise Exception("TODO send_empty_to_father cause did not add self to token")

    def compute_receive_token_from_father_leaf(self):
        potential_value_and_cost = self.get_potential_values_dict()
        min_cost = min(potential_value_and_cost.values())
        if self.best_global_token is not None:
            if self.best_global_token.UB[0]<=min_cost:
               raise Exception("TODO need to complete")
        else:
            self.variable = min(potential_value_and_cost, key=lambda k: potential_value_and_cost[k])
            try:
                self.token.add_agent_to_token_variables(id_=self.id_, value=self.variable,local_cost=min_cost)
                self.record_other_domains_of_leaf(potential_value_and_cost)
                self.status = BNB_Status.send_token_to_father
            except ShouldPruneException:
                self.record_all_domains(potential_value_and_cost)
                #self.status = BNB_Status.send_empty_to_father
                raise Exception("TODO send_empty_to_father cause did not add self to token")





        return potential_value_and_cost[self.variable]

    def get_potential_values_dict(self):
        ans = {}
        current_context = self.token.get_variable_dict(self.above_me)
        for potential_domain in self.domain:
            potential_cost = self.calc_potential_cost(potential_domain, current_context)
            ans[potential_domain] = potential_cost
        return ans

    def record_other_domains_of_leaf(self,potential_value_and_cost):
        for domain, cost in potential_value_and_cost.items():
            if domain!= self.variable:
                token_winner = self.token.__deepcopy__()
                token_other = self.token.__deepcopy__()
                token_other.variables[self.id_] = (domain, cost)
                try:
                    token_other.update_cost()
                except ShouldPruneException:
                    if debug_BNB:
                        print("for record... check it")
                self.records.append((token_other, token_winner))

    # send msgs #################################################################################################

    def create_local_token_root(self):
        if self.status != BNB_Status.finished_going_over_domain:
            self.token = BranchAndBoundToken()
            self.token.add_agent_to_token_variables(id_=self.id_, value=self.variable, local_cost=0)
            self.reset_tokens_from_children()



    def sends_msgs_token_down_the_tree(self):
        sender = self.id_
        msgs = []
        for receiver in self.dfs_children:
            temp_token = self.token.__deepcopy__()
            msg = Msg(sender=sender, receiver=receiver, information=temp_token,
                      msg_type=BNB_msg_type.token_from_father)
            msgs.append(msg)
        self.outbox.insert(msgs)
        if debug_BNB:
            print(self.__str__(), "sends messages to its children:",self.dfs_children)

    def sends_msgs_token_up_the_tree(self):
        msg = Msg(sender=self.id_, receiver=self.dfs_father, information=self.token.__deepcopy__(),
                  msg_type=BNB_msg_type.token_from_child)
        self.outbox.insert([msg])
        self.domain_index = -1
        if len(self.dfs_children) != 0:
            raise Exception("only leaf should be in this status")

    def is_receive_from_all_children(self):
        for info in self.tokens_from_children.values():
            if info is None:
                return False
        return True

    def is_receive_tokens_from_all(self):
        for info in self.tokens_from_children.values():
            if not isinstance(info,BranchAndBoundToken):
                return False
        return True

    def compute_receive_all_tokens_from_children(self):
        self.aggregate_tokens()
        did_change_token,previous_local_token = self.check_to_change_best_local_token()
        self.record_best_token_if_needed(did_change_token, previous_local_token)

        if self.dfs_father is None:
            raise Exception("TODO need to update best token as root")
        else:
            try:
                self.token = self.token.create_reseted_token(self.id_)
                self.select_next_value()
                if self.status == BNB_Status.finished_going_over_domain:
                    if self.id_ not in self.token.variables.keys():
                        if self.best_local_token is None:
                            #self.status = BNB_Status.send_empty_to_father
                            raise Exception("TODO send_empty_to_father cause did not add self to token")

                            self.reset_tokens_from_children()
                        else:
                            self.status = BNB_Status.send_best_local_token_to_father
                        return
                    else:
                        self.status = BNB_Status.send_best_local_token_to_father
                else:
                    self.status = BNB_Status.send_token_to_children
            except ShouldPruneException:
                self.status = BNB_Status.send_best_local_token_to_father
                if debug_BNB:
                    print(self.__str__(),"currently found combination where all below are zero without selecting next value")


    def aggregate_tokens(self):
        local_token_temp = None
        for child_token in self.tokens_from_children.values():
            if local_token_temp is None:
                local_token_temp = child_token
            else:
                try:
                    local_token_temp = local_token_temp + child_token
                except ShouldPruneException:
                    raise Exception ("when adding tokens from children the best token found is better")
        self.token = local_token_temp

    def check_to_change_best_local_token(self):
        cost_of_current_token = self.token.LB


        if self.best_local_token is not None:
            cost_of_current_best_local_token = self.best_local_token.LB
            if cost_of_current_token < cost_of_current_best_local_token:
                prev_token = self.best_local_token.__deepcopy__()
                self.best_local_token = self.token.__deepcopy__()
                var_to_send = {}
                for k,v in self.token.variables.items():
                    var_to_send[k]=v
                self.best_local_token.UB = (self.token.LB, var_to_send)
                return True,prev_token
            else: return False, None

        else:
            self.best_local_token = self.token.__deepcopy__()
            self.best_local_token.UB = self.token.LB

        return False, None

    def record_best_token_if_needed(self, did_change_token, previous_local_token):
        if did_change_token:
            winner_token = self.best_local_token.__deepcopy__()
            loser_token = previous_local_token
            self.records.append((loser_token, winner_token))
            #raise Exception("need to see that this is working")

    def send_msgs_empty_up_the_tree(self):
        msg = Msg(sender=self.id_, receiver=self.dfs_father, information=object(),
                  msg_type=BNB_msg_type.token_empty)
        self.outbox.insert([msg])
        self.domain_index = -1

    def sends_msgs_best_token_up_the_tree(self):
        msg = Msg(sender=self.id_, receiver=self.dfs_father, information=self.best_local_token.__deepcopy__(),
                  msg_type=BNB_msg_type.token_from_child)
        self.outbox.insert([msg])
        self.domain_index = -1
        self.best_local_token = None

    def get_best_token_from_records(self):
        second_elements = []
        for t in self.records:
            second_elements.append(t[1])
        min_object = min(second_elements, key=lambda x: x.UB)
        return min_object

    def record_all_domains(self,potential_value_and_cost):
        for domain, cost in potential_value_and_cost.items():

            temp_var = {  }
            for k,v in self.token.UB[1].items():
                temp_var[k] = v

            token_winner = BranchAndBoundToken(LB=self.token.UB[0] ,variables=temp_var)
            token_other = self.token.__deepcopy__()
            token_other.variables[self.id_] = (domain, cost)
            try:
                token_other.update_cost()
            except ShouldPruneException:
                if debug_BNB:
                    print("for record... check it")
            self.records.append((token_other, token_winner))























