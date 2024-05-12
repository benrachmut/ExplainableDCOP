import math
from enum import Enum

from Scripts._testmultiphase import Example

import globals_
import problems
from Trees import *
from agents import *
from globals_ import *


def copy_dict(dict):
    ans = {}
    for k,v in dict.items():
        ans[k]=v
    return ans

class BNB_msg_type(Enum):
    token_from_father = 1
    token_from_child = 2
    token_empty = 3
    finish_algorithm = 4


class BNB_Status(Enum):
    hold_token_send_down = 1
    #finished_going_over_domain = 2
    finished_temp_role_in_tree = 3

    wait_tokens_from_children = 4

    receive_token_from_father_mid = 5
    receive_token_from_father_leaf = 6
    receive_token_from_all_children = 7
    receive_all_tokens_from_children_with_empty = 8

    send_token_to_children = 9
    send_empty_to_father = 10
    send_token_to_father = 11
    send_best_local_token_to_father = 12

    receive_all_tokens_from_children = 13
    receive_all_tokens_from_children_root = 14

    finished_algorithm = 15
    ####

class LocalUBPruneException(Exception):
    def __init__(self, message=""):
        Exception.__init__(self)
        print("\033[91m"+message+"\033[0m")


class GlobalUBPruneException(Exception):
    def __init__(self, message=""):
        Exception.__init__(self)
        print("\033[91m" + message + "\033[0m")






class BranchAndBoundToken:
    def __init__(self,heights = None, best_UB:SingleInformation = None, UB:SingleInformation = None, LB:SingleInformation = None,):
        self.best_UB= best_UB
        self.UB = UB
        self.LB = LB
        self.heights = heights

    def __deepcopy__(self, memodict={}):
        best_UB_input = None
        UB_input = None
        LB_input = None

        if self.best_UB is not None:
            best_UB_input = self.best_UB.__deepcopy__()
        if self.UB is not None:
            UB_input = self.UB.__deepcopy__()
        if self.LB is not None:
            LB_input = self.LB.__deepcopy__()

        heights_input = None
        if self.heights is not None:
            heights_input = copy_dict(self.heights)
        return BranchAndBoundToken(best_UB= best_UB_input,UB = UB_input,LB = LB_input, heights = heights_input)

    def get_lb_copy(self):
        return self.LB.__deepcopy__()

    def get_ub_copy(self):
        if self.UB is not None:
            return self.UB.__deepcopy__()
        else:
            return None

    def get_best_ub_copy(self):
        if self.UB is not None:
            return self.best_UB.__deepcopy__()
        else:
            return None
    # def __add__(self, other):
    #
    #     best_UB = self.check_for_best_UB(other)
    #
    #
    #     new_variables = self.merge_variables(other)
    #     new_heights = self.merge_heights(other)
    #
    #     ans = BranchAndBoundToken(best_UB= best_UB, variables=new_variables, heights=new_heights)
    #     ans.update_cost()
    #
    #     variables_to_send = {}
    #     for k, v in self.variables.items():
    #         variables_to_send[k] = v
    #
    #     #ans.UB= (ans.LB,variables_to_send)
    #
    #     # todo check if best variables is the same if not there is a bug raise exp
    #     return ans
    #
    # def create_reseted_token(self,id_):
    #     new_variables = self.reset_variables(id_)
    #     ans = BranchAndBoundToken(best_UB= self.best_UB, UB= self.UB, LB = 0, variables = new_variables, heights = self.heights)
    #     ans.update_cost()
    #     return ans
    #
    # def agent_include_in_variables(self,id_):
    #     if id_ in self.variables.keys():
    #         return True
    #     else:
    #         return False
    #
    # def add_agent_to_token_variables(self,id_,value,local_cost,constraint_list):
    #     if self.agent_include_in_variables(id_):
    #         raise Exception("used it when agent is already in token")
    #     #stopped here
    #     self.variables[id_] = BranchAndBoundInformation()(value,local_cost)
    #
    #     if  id_ not in self.heights.keys():
    #         if len(self.heights)==0:
    #             self.heights[id_] = 1
    #         else:
    #             self.heights[id_] = max(self.heights.values())+1
    #
    #     self.update_cost()
    #
    # def update_cost(self,flag = True):
    #     costs = []
    #     for n_id, tuple_ in self.variables.items():
    #         costs.append(tuple_[1])
    #     #costs =  {key: sum(value) for key, value in self.variables.items()}.values()
    #
    #     self.LB = sum(costs)
    #
    #     best_UB = self.best_UB
    #     if best_UB is not None and self.LB>=best_UB[0]:
    #         if flag and debug_BNB:
    #             raise GlobalUBPruneException("LB>UB_global move to the next domain LB=" + str(self.LB) + " UB_global=" + str(best_UB[0]))
    #         else:
    #             raise GlobalUBPruneException()
    #
    #     if self.UB is not None and self.LB>=self.UB[0]:
    #         if flag and debug_BNB:
    #             raise LocalUBPruneException("LB>UB_local move to the next domain LB=" + str(self.LB) + " UB_local=" + str(self.UB))
    #         else:
    #             raise LocalUBPruneException()
    #
    # def copy_variables(self):
    #     ans = {}
    #     for k,v in self.variables.items():
    #         ans[k] = v
    #     return ans
    #
    # def get_variable_dict(self,agent_list_id):
    #     ans = {}
    #     for n_id in agent_list_id:
    #         ans[n_id] = next(iter(self.variables[n_id]))
    #
    #         #ans[n_id] = self.variables[n_id][0]
    #     return ans
    #
    # def __str__(self):
    #     return "UB:" + str(self.UB) + ", LB:" + str(self.LB) + ", context:" + str(self.variables)
    #
    # def __deepcopy__(self, memodict={},flag = False):
    #     variables_to_send = {}
    #     for k,v in self.variables.items():
    #         variables_to_send[k] = v
    #
    #     heights_to_send = {}
    #     for k, v in self.heights.items():
    #         heights_to_send[k] = v
    #
    #     best_token = None
    #     if self.best_UB is not None and not flag:
    #         dict_dup = copy_dict(self.best_UB[1])
    #         best_token = (self.best_UB[0],dict_dup)
    #
    #     return BranchAndBoundToken(best_UB= best_token, UB= self.UB, LB = self.LB, variables = variables_to_send, heights = heights_to_send)
    #
    # def merge_heights(self, other):
    #     merged_dict = {}
    #     # Merge keys from both dictionaries
    #     all_keys = set(self.variables.keys()) | set(other.variables.keys())
    #
    #     for key in all_keys:
    #
    #
    #
    #         value_dict1 = self.heights.get(key)
    #         value_dict2 = other.heights.get(key)
    #
    #         if value_dict1 is not None and value_dict2 is not None:
    #             if value_dict1 != value_dict2:
    #                 raise ValueError(f"Conflict for key {key}: {value_dict1} != {value_dict2}")
    #             else:
    #                 merged_dict[key] = value_dict1
    #         elif value_dict1 is not None:
    #             merged_dict[key] = value_dict1
    #         elif value_dict2 is not None:
    #             merged_dict[key] = value_dict2
    #
    #     return merged_dict
    #
    # def merge_variables(self, other):
    #     merged_dict = {}
    #     # Merge keys from both dictionaries
    #     all_keys = set(self.variables.keys()) | set(other.variables.keys())
    #
    #     for key in all_keys:
    #         value_dict1 = self.variables.get(key)
    #         value_dict2 = other.variables.get(key)
    #
    #         if value_dict1 is not None and value_dict2 is not None:
    #             if value_dict1 != value_dict2:
    #                 raise ValueError(f"Conflict for key {key}: {value_dict1} != {value_dict2}")
    #             else:
    #                 merged_dict[key] = value_dict1
    #         elif value_dict1 is not None:
    #             merged_dict[key] = value_dict1
    #         elif value_dict2 is not None:
    #             merged_dict[key] = value_dict2
    #
    #     return merged_dict
    #
    # def reset_variables(self,id_):
    #     ans = {}
    #
    #     height_of_id = self.heights[id_]
    #
    #     for n_id, dict_ in self.variables.items():
    #         height_of_neighbor = self.heights[n_id]
    #         if height_of_id > height_of_neighbor:
    #             ans[n_id] = dict_
    #     return ans
    #
    # def check_for_best_UB(self,other):
    #     if other.best_UB is not None and self.best_UB is not None and other.best_UB[0] != self.best_UB[0]:
    #         raise Exception("not logical")
    #
    #     if other.best_UB is None and self.best_UB is not None:
    #         raise Exception("not logical")
    #
    #     if other.best_UB is not None and self.best_UB is None:
    #         raise Exception("not logical")
    #     best_UB = None
    #
    #     if other.best_UB is not None and self.best_UB is not None:
    #         dict_dup = copy_dict(self.best_UB[1])
    #         best_UB = (self.best_UB[0],dict_dup)
    #     return  best_UB

class BranchAndBound(DFS,CompleteAlgorithm):
    def __init__(self, id_, D):
        DFS.__init__(self, id_, D)
        self.domain_index = -1
        self.best_global_token = None
        self.token = None
        self.tokens_from_children = {}
        self.receive_empty_msg_flag = False
        self.my_height = None
        self.above_me = []

    def is_algorithm_complete(self):
        return self.status == BNB_Status.finished_algorithm

    def update_msgs_in_context_after_tree(self, msgs):
        for msg in msgs:
            if msg.msg_type == BNB_msg_type.token_from_father:
                self.update_msgs_in_context_receive_token_from_father(msgs)
            if msg.msg_type == BNB_msg_type.token_from_child:
                self.tokens_from_children[msg.sender] = msg.information.__deepcopy__()
            if msg.msg_type == BNB_msg_type.token_empty:
                self.tokens_from_children[msg.sender] = msg.information.__deepcopy__()
                self.receive_empty_msg_flag = True
                #raise Exception ("need to move to next in domain, because children could not find anything good with current domain")

            if msg.msg_type == BNB_msg_type.finish_algorithm:

                self.token = msg.information.__deepcopy__()
                self.variable_anytime = self.token.best_UB[1][self.id_][0]

            if debug_BNB:
                print(self.__str__(), "receive", msg.msg_type,"from A_",msg.sender,"info:", msg.information)

    def change_status_after_update_msgs_in_context_after_tree(self, msgs):
        if debug_BNB:
            print(self.__str__(), "status WAS:", self.status)

        if msgs[0].msg_type == BNB_msg_type.token_from_father:
            self.check_to_update_anytime_variable()
            if len(self.dfs_children) == 0:
                self.status = BNB_Status.receive_token_from_father_leaf
            else:
                self.status = BNB_Status.receive_token_from_father_mid

        if msgs[0].msg_type == BNB_msg_type.token_from_child or msgs[0].msg_type == BNB_msg_type.token_empty:
            if self.is_receive_from_all_children():
                self.update_status_if_receive_from_all_children()
            else:
                self.status = BNB_Status.wait_tokens_from_children

        if msgs[0].msg_type == BNB_msg_type.finish_algorithm:
            self.status = BNB_Status.finished_algorithm


        if debug_BNB:
            print(self.__str__(), "status IS:", self.status)

    def is_compute_in_this_iteration_after_tree(self):
        return self.root_of_tree_start_algorithm or \
               self.status == BNB_Status.receive_token_from_father_mid or\
               self.status == BNB_Status.receive_token_from_father_leaf or \
               self.status == BNB_Status.receive_all_tokens_from_children or \
               self.status == BNB_Status.receive_all_tokens_from_children_with_empty or \
               self.status == BNB_Status.receive_all_tokens_from_children_root or \
               self.status == BNB_Status.finished_algorithm

    def compute_after_tree(self):
        if self.root_of_tree_start_algorithm:
            self.compute_start_algorithm() # done
        elif self.status == BNB_Status.receive_token_from_father_mid:
            self.compute_receive_token_from_father_mid()
        elif self.status == BNB_Status.receive_token_from_father_leaf:
            self.compute_receive_token_from_father_leaf() # TODO
        elif self.status == BNB_Status.receive_all_tokens_from_children:
            self.compute_receive_all_tokens_from_children() #TODO
        elif self.status == BNB_Status.receive_all_tokens_from_children_with_empty:
            self.compute_receive_all_tokens_from_children_with_empty() #TODO
        elif self.status == BNB_Status.receive_all_tokens_from_children_root:
            self.compute_receive_all_tokens_from_children_root() #TODO

        if debug_BNB:
            print(self.__str__(), "status IS:", self.status)

    def send_msgs_after_tree(self):
        if self.status == BNB_Status.hold_token_send_down or self.status == BNB_Status.send_token_to_children:
            self.sends_msgs_token_down_the_tree()

        if self.status == BNB_Status.send_token_to_father:
            self.sends_msgs_token_up_the_tree()

        if self.status == BNB_Status.send_best_local_token_to_father:
            self.sends_msgs_best_token_up_the_tree()

        if self.status == BNB_Status.send_empty_to_father:
            self.send_msgs_empty_up_the_tree()

        if self.status == BNB_Status.finished_algorithm:
            self.send_msgs_finished_algorithm()


    def change_status_after_send_msgs_tree(self):
        if self.status == BNB_Status.hold_token_send_down or self.status == BNB_Status.send_token_to_children:
            self.status = BNB_Status.wait_tokens_from_children

        if self.status == BNB_Status.send_token_to_father or self.status == BNB_Status.send_empty_to_father or self.status == BNB_Status.send_best_local_token_to_father:
            self.status = BNB_Status.finished_temp_role_in_tree

        if debug_BNB:
            print(self.__str__(), "status IS:", self.status)

        self.token = None

    def update_status_if_receive_from_all_children(self):
        if self.receive_empty_msg_flag:
            self.receive_empty_msg_flag = False
            if self.is_root():
                raise Exception("did not create this status yet")
                self.status = BNB_Status.receive_all_tokens_from_children_with_empty_root
            else:
                self.status = BNB_Status.receive_all_tokens_from_children_with_empty

        else:
            if self.is_root():
                self.status = BNB_Status.receive_all_tokens_from_children_root
            else:
                self.status = BNB_Status.receive_all_tokens_from_children



    # update msgs #################################################################################################

    def update_msgs_in_context_receive_token_from_father(self, msgs):
        if len(msgs) > 1:
            raise Exception("should receive a single msg")
        self.token = msgs[0].information.__deepcopy__()


    # compute #################################################################################################

    def compute_start_algorithm(self):
        self.my_height = 1
        self.select_next_value()
        si = SingleInformation(context={self.id_:self.variable},constraints={self.id_:{}})
        self.create_local_token_root(si)
        self.root_of_tree_start_algorithm = False
        self.status = BNB_Status.hold_token_send_down
        if debug_DFS_draw_tree:
            globals_.draw_dfs_tree_flag = True

    def select_next_value(self):
        self.domain_index = self.domain_index + 1
        self.reset_tokens_from_children()
        if self.root_of_tree_start_algorithm:
            self.variable = self.domain[self.domain_index]
            return
        while self.domain_index < len(self.domain):
            self.variable = self.domain[self.domain_index]
            lb_to_update = self.get_lb_to_update()
            did_update = self.try_to_update_lb(lb_to_update)
            if did_update:
                return True

            self.domain_index = -1
            if debug_BNB:
                print(self, "finished going over domain", self.variable)
            return False

    def try_to_update_lb(self,lb_to_update):
        if self.is_need_to_update_lb(lb_to_update):
            self.token.lb = lb_to_update
            if debug_BNB:
                print(self, "variable changed to", self.variable)
            return True
        else:
            raise Exception("need to check this")
            is_better_then_UB, is_better_then_best_UB = self.get_the_reason_for_failure()
            text = "Adding value " + str(
                self.variable) + " by A_" + self.id_ + " with cost " + self.lb_to_update + ", is larger than "
            pe = self.get_explanation(is_better_then_UB, is_better_then_best_UB, text)  # TODO
            self.add_prune_explanation(pe)  # TODO
            if debug_BNB:
                print(self, "variable did not change to", self.variable, text)
            return False

    def get_the_reason_for_failure(self,lb_to_update):
        return self.check_specific_ub(lb_to_update, self.token.UB),\
               self.check_specific_ub(lb_to_update, self.token.best_UB)

    def reset_tokens_from_children(self):
        self.tokens_from_children = {}
        for n_id in self.dfs_children:
            self.tokens_from_children[n_id] = None

    def compute_receive_token_from_father_mid(self):
        self.update_height_and_above_me()
        is_managed_to_select_value = self.select_next_value()
        if is_managed_to_select_value:
            self.status = BNB_Status.send_token_to_children
        else:
            self.status = BNB_Status.send_empty_to_father
            raise Exception("need to check this")


    def compute_receive_token_from_father_leaf(self):

        self.update_height_and_above_me()
        current_UB = self.token.UB
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
            except LocalUBPruneException:
                self.record_all_domains(potential_value_and_cost,winner_vars=copy_dict(self.token.UB[1]),winner_LB_input=self.token.UB[0])
                self.status = BNB_Status.send_empty_to_father
            except GlobalUBPruneException:
                self.record_all_domains(potential_value_and_cost, winner_vars=copy_dict(self.token.best_UB[1]),
                                        winner_LB_input=self.token.best_UB[0])
                self.status = BNB_Status.send_empty_to_father



        return potential_value_and_cost[self.variable]

    def compute_receive_all_tokens_from_children_with_empty(self):
        current_token = self.sanity_check_all_tokens_identical_from_my_height()
        self.token = BranchAndBoundToken(variables=current_token.variables,heights=current_token.heights)
        self.token.update_cost()
        if self.local_UB is not None:
            dict_dup = copy_dict(self.local_UB[1])
            self.token.UB = (self.local_UB[0], dict_dup)
        if self.dfs_father is None:
            raise Exception("TODO need to update best token as root")
        self.select_next_value()
        self.change_statues_after_value_change()

    def compute_receive_all_tokens_from_children_root(self):
        self.create_token_from_children()
        dict_dup = copy_dict(self.local_UB[1])
        self.token.best_UB = (self.local_UB[0], dict_dup)
        self.variable_anytime = self.token.variables[self.id_][0]
        self.token.variables = {}
        self.token.LB = 0
        self.select_next_value()
        if self.status == BNB_Status.finished_going_over_domain:
            self.status = BNB_Status.finished_algorithm
        else:
            self.status = BNB_Status.send_token_to_children
            raise Exception("did not complete this")

    def get_potential_values_dict(self):


        ans = {}
        current_context = self.token.get_variable_dict(self.above_me)
        for potential_domain in self.domain:
            potential_cost = self.calc_potential_cost(potential_domain, current_context)
            ans[potential_domain] = potential_cost
        return ans



    # select_next_value #################################################################################################

    def get_lb_to_update(self):


        constraints = self.get_constraints(current_context = self.token.get_lb_copy().context)
        token_lb = self.token.get_lb_copy()
        token_lb.update_constraints(self.id_, constraints)
        token_lb.update_context(self.id_, self.variable)  # TODO
        return token_lb

    def check_specific_ub(self, lb_to_update: SingleInformation, ub: SingleInformation):
        if ub is None:
            return True
        elif lb_to_update < ub:
            return True
        return False

    def is_need_to_update_lb(self, lb_to_update):
        is_better_then_UB = self.check_specific_ub(lb_to_update, self.token.UB)
        is_better_then_best_UB = self.check_specific_ub(lb_to_update, self.token.best_UB)
        return is_better_then_UB or is_better_then_best_UB

    def get_explanation(self, is_better_then_UB, is_better_then_best_UB, text):
        pe = None
        if not is_better_then_UB:
            text = text + " UB with cost " + self.token.UB.total_cost
            pe = PruneExplanation(winner=self.token.UB__deepcopy__(), loser=self.token.LB__deepcopy__(), text=text)

        if not is_better_then_best_UB:
            text = text + " global UB with cost " + self.token.best_UB.total_cost
            pe = PruneExplanation(winner=self.token.best_UB__deepcopy__(), loser=self.token.LB__deepcopy__(),
                                  text=text)
        if pe is None:
            raise Exception("must have a reason")

        return pe



    def get_n_obj(self,n_id):
        for n in self.neighbors_obj:
            if n.is_ids_this_object(self.id_,n_id):
                return n
    # send msgs #################################################################################################

    def send_msgs_finished_algorithm(self):
        sender = self.id_
        msgs = []
        for receiver in self.dfs_children:
            msg = Msg(sender=sender, receiver=receiver, information=self.token.__deepcopy__(),
                      msg_type=BNB_msg_type.finish_algorithm)

            msgs.append(msg)
        self.outbox.insert(msgs)
        if debug_BNB:
            print(self.__str__(), "sends messages to its children:", self.dfs_children)


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

    def send_msgs_empty_up_the_tree(self):
        msg = Msg(sender=self.id_, receiver=self.dfs_father, information=self.token.__deepcopy__(),
                  msg_type=BNB_msg_type.token_empty)
        self.outbox.insert([msg])
        self.domain_index = -1

    def sends_msgs_best_token_up_the_tree(self):

        info = BranchAndBoundToken(variables=copy_dict(self.local_UB[1]), LB=self.local_UB[0],
                                   UB=(self.local_UB[0], copy_dict(self.local_UB[1])), heights=self.token.heights)
        msg = Msg(sender=self.id_, receiver=self.dfs_father, information=info,
                  msg_type=BNB_msg_type.token_from_child)
        self.outbox.insert([msg])
        self.domain_index = -1
        self.local_UB = None

##################################################################


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
        self.create_token_from_children()

        self.check_if_continue_down_or_up()

    def aggregate_tokens(self):
        local_token_temp = None
        for child_token in self.tokens_from_children.values():
            if local_token_temp is None:
                local_token_temp = child_token
            else:
                try:
                    local_token_temp = local_token_temp + child_token
                except LocalUBPruneException:
                    raise Exception ("when adding tokens from children the best token found is better")
        self.token = local_token_temp

    def check_to_change_best_local_token(self):
        cost_of_current_token = self.token.LB
        if self.local_UB is not None:
            cost_of_current_best_local_token = self.local_UB[0]
            if cost_of_current_token < cost_of_current_best_local_token:
                dict_dup = copy_dict(self.local_UB[1])
                prev_token = (self.local_UB[0], dict_dup)#self.best_local_token.__deepcopy__()
                self.local_UB = (self.token.LB, self.token.copy_variables())
                return True,prev_token
            else:
                return False, None

        else:
            self.local_UB = (self.token.LB, self.token.copy_variables())
            #self.best_local_token.UB = self.token.UB
            return True, None

    def check_if_continue_down_or_up(self):
        if self.is_root():
            raise Exception("TODO need to update best token as root")
        else:
            try:
                self.token = self.token.create_reseted_token(self.id_)
            except LocalUBPruneException:
                self.status = BNB_Status.send_best_local_token_to_father
                self.add_to_records_from_current_token(winner_variables=copy_dict(self.token.UB[1]),winner_LB=self.token.UB[0])
                if debug_BNB:
                    print(self.__str__(),"currently found combination where all below are zero without selecting next value")
                return
            except GlobalUBPruneException:
                self.status = BNB_Status.send_best_local_token_to_father
                self.add_to_records_from_current_token(winner_variables=copy_dict(self.token.best_UB[1]),
                                                       winner_LB=self.token.best_UB[0])
                if debug_BNB:
                    print(self.__str__(),
                          "currently found combination where all below are zero without selecting next value")
                return


            self.select_next_value()
            self.change_statues_after_value_change()

    def sanity_check_all_tokens_identical_from_my_height(self):
        variables = []
        for child_token in self.tokens_from_children.values():
            variables.append(child_token.reset_variables(self.id_))
        all_equal = all(item == variables[0] for item in variables)
        if all_equal:
            child_token.create_reseted_token(self.id_)
            del child_token.variables[self.id_]
            child_token.UB = None
            child_token.update_cost()

            return child_token
        else:
            raise Exception("check is wrong")

    def is_root(self):
        return self.dfs_father is None

    def change_statues_after_value_change(self):
        if self.status == BNB_Status.finished_going_over_domain:
            if self.id_ not in self.token.variables.keys():
                if self.local_UB is None:
                    self.status = BNB_Status.send_empty_to_father
                    self.reset_tokens_from_children()
                else:
                    self.status = BNB_Status.send_best_local_token_to_father
                return
            else:
                if self.local_UB is None:
                    self.status = BNB_Status.send_empty_to_father
                    print("_______check if need to record here_______")
                else:
                    self.status = BNB_Status.send_best_local_token_to_father
        else:
            self.status = BNB_Status.send_token_to_children

    def create_token_from_children(self):
        self.aggregate_tokens()
        did_change_token, previous_local_token = self.check_to_change_best_local_token()
        if did_change_token:
            dict_dup = copy_dict(self.local_UB[1])
            self.token.UB = (self.local_UB[0], dict_dup)
        if previous_local_token is not None:
            self.record_best_token_if_needed(did_change_token, previous_local_token)

    def check_to_update_anytime_variable(self):
        if self.token.best_UB is not None:
            self.token.best_UB[1][self.id_][0]
            raise Exception("stopped here")

    def create_local_token_root(self, si:SingleInformation):
        self.token = BranchAndBoundToken(LB=si,heights={self.id_:self.my_height})
        self.reset_tokens_from_children()



# RECORDS #################---------------------------------


    def record_other_domains_of_leaf(self,potential_value_and_cost):
        for domain, cost in potential_value_and_cost.items():
            if domain!= self.variable:
                token_winner = self.token.__deepcopy__()
                token_other = self.token.__deepcopy__()
                token_other.variables[self.id_] = (domain, cost)
                try:
                    token_other.update_cost()
                except LocalUBPruneException:
                    pass
                except GlobalUBPruneException:
                    pass


                self.add_to_records(other_variables=token_other.variables,other_LB=token_other.LB,
                                    winner_variables=token_winner.variables,winner_LB=token_winner.LB)



    def record_best_token_if_needed(self, did_change_token, previous_local_token):
        if did_change_token:
            winner_token = (self.local_UB[0],self.local_UB[1])
            loser_token = previous_local_token

            self.add_to_records(other_variables=copy_dict(loser_token[1]),other_LB=loser_token[0],winner_variables= copy_dict(winner_token[1]),winner_LB=winner_token[0])

    def record_all_domains(self,potential_value_and_cost, winner_vars,winner_LB_input):
        for domain, cost in potential_value_and_cost.items():
            token_other = self.token.__deepcopy__()
            token_other.variables[self.id_] = (domain, cost)
            try:
                token_other.update_cost(False)
            except LocalUBPruneException:
                pass
            except GlobalUBPruneException:
                pass
            other_variables = token_other.variables
            other_LB = token_other.LB
            self.add_to_records(other_variables=other_variables, other_LB=other_LB, winner_variables=winner_vars,
                                winner_LB=winner_LB_input)

    #
    # def add_to_records_from_current_token(self, winner_variables, winner_LB):
    #     other_variables = copy_dict(self.token.__deepcopy__().variables)
    #     other_LB = self.token.__deepcopy__().LB
    #     self.add_to_records(other_variables=other_variables, other_LB=other_LB, winner_variables=winner_variables,
    #                         winner_LB=winner_LB)

    def add_to_records(self, other_variables,other_LB, winner_variables, winner_LB):
        if "Agent_id" not in self.records:
            self.records["Agent_id"] = []
        self.records["Agent_id"].append(self.id_)

        if "local_clock" not in self.records:
            self.records["local_clock"] = []
        self.records["local_clock"].append(self.local_clock)

        if "global_clock" not in self.records:
            self.records["global_clock"] = []
        self.records["global_clock"].append(self.global_clock)

        if "context_loser" not in self.records:
            self.records["context_loser"] = []
        self.records["context_loser"].append(other_variables)

        if "LB_loser" not in self.records:
            self.records["LB_loser"] = []
        self.records["LB_loser"].append(other_LB)

        if "context_winner" not in self.records:
            self.records["context_winner"] = []
        self.records["context_winner"].append(winner_variables)

        if "LB_winner" not in self.records:
            self.records["LB_winner"] = []
        self.records["LB_winner"].append(winner_LB)

    def update_height_and_above_me(self):
        if len(self.above_me) == 0 and not self.is_root():
            father_height = self.token.heights[self.dfs_father]
            self.my_height = father_height+1
            for k in self.token.heights.keys():
                self.above_me.append(k)
            self.token.heights[self.id_] = self.my_height





















