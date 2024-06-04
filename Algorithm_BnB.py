import math
from enum import Enum

from Scripts._testmultiphase import Example

import Globals_
from Trees import *
from Agents import *
from Globals_ import *
from General_Entities import *


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
    finished_going_over_domain = 2
    finished_temp_role_in_tree = 3

    wait_tokens_from_children = 4

    receive_token_from_father_mid = 5
    receive_token_from_father_leaf = 6
    receive_token_from_all_children = 7
    receive_all_tokens_from_children_with_empty = 8

    send_token_to_children = 9
    send_empty_to_father = 10
    send_token_to_leaf_to_father = 11
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
    def __init__(self,heights = None, best_UB:SingleInformation = None, UB:SingleInformation = None, LB:SingleInformation = None):
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

    def add_height_dicts(self,other):
        ans = {}
        for id_,height in self.heights.items():
            ans[id_]=height
        for id_,height in other.heights.items():
            ans[id_]=height
        return ans

    def __add__(self, other):
        heights = self.add_height_dicts(other)#copy_dict(other.heights)
        best_UB = None
        if other.best_UB is not None:
            best_UB = other.best_UB.__deepcopy__()
        LB = self.LB + other.LB
        UB = LB.__deepcopy__()
        return BranchAndBoundToken (heights = heights, best_UB=best_UB, UB=UB , LB = LB)



    def reset_LB_given_id(self, id_):

        heights_to_include = []
        for id_of_height,height in self.heights.items():
            if height <= self.heights[id_] and id_!=id_of_height:
                heights_to_include.append(id_of_height)
        self.LB = self.LB.reset_given_id(heights_to_include)
        return self.LB.__deepcopy__()

    def __str__(self):
        return str(self.LB.context)



class BranchAndBound(DFS,CompleteAlgorithm):
    def __init__(self, id_, D):
        DFS.__init__(self, id_, D)
        self.domain_index = -1
        self.best_global_UB = None
        self.token = None
        self.tokens_from_children = {}
        self.receive_empty_msg_flag = False
        self.my_height = None
        self.heights = {}
        self.above_me = []
        #self.records_dict = {}
        self.local_UB = None
        self.anytime_variable=None
        self.anytime_context=None
        self.anytime_constraints=None

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
            if msg.msg_type == BNB_msg_type.finish_algorithm:
                self.token = msg.information.__deepcopy__()
                self.anytime_variable, self.anytime_context, self.anytime_constraints = self.token.best_UB.get_anytime_info(
                    self.id_, self.neighbors_agents_id)


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
            self.compute_receive_token_from_father_leaf()
        elif self.status == BNB_Status.receive_all_tokens_from_children:
            self.compute_receive_all_tokens_from_children()
        elif self.status == BNB_Status.receive_all_tokens_from_children_with_empty:
            self.compute_receive_all_tokens_from_children_with_empty()
        elif self.status == BNB_Status.receive_all_tokens_from_children_root:
            self.compute_receive_all_tokens_from_children_root()

        if debug_BNB:
            print(self.__str__(), "status IS:", self.status)

    def send_msgs_after_tree(self):
        if self.status == BNB_Status.hold_token_send_down or self.status == BNB_Status.send_token_to_children:
            self.sends_msgs_token_down_the_tree()

        if self.status == BNB_Status.send_token_to_leaf_to_father:
            self.sends_msgs_token_up_the_tree_leaf_to_father()

        if self.status == BNB_Status.send_best_local_token_to_father:
            self.sends_msgs_UB_up_the_tree()

        if self.status == BNB_Status.send_empty_to_father:
            self.send_msgs_empty_up_the_tree()

        if self.status == BNB_Status.finished_algorithm:
            self.send_msgs_finished_algorithm()

    def change_status_after_send_msgs_tree(self):
        if self.status == BNB_Status.hold_token_send_down or self.status == BNB_Status.send_token_to_children:
            self.status = BNB_Status.wait_tokens_from_children

        if self.status == BNB_Status.send_token_to_leaf_to_father or self.status == BNB_Status.send_empty_to_father or self.status == BNB_Status.send_best_local_token_to_father:
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
            Globals_.draw_dfs_tree_flag = True

    def select_next_value(self):
        self.domain_index = self.domain_index + 1
        self.reset_tokens_from_children()
        if self.root_of_tree_start_algorithm:
            self.variable = self.domain[self.domain_index]
            return
        while self.domain_index < len(self.domain):
            self.variable = self.domain[self.domain_index]
            lb_to_update = self.get_lb_to_update(self.variable)
            did_update = self.try_to_update_lb(lb_to_update)
            if did_update:
                return True
            else:
                self.domain_index = self.domain_index + 1
        self.actions_for_finished_going_over_domain()
        return False

    def actions_for_finished_going_over_domain(self):
        self.status = BNB_Status.finished_going_over_domain
        self.domain_index = -1
        if debug_BNB:
            print(self, "finished going over domain", self.variable)

    def try_to_update_lb(self,lb_to_update):
        if self.is_need_to_update_lb(lb_to_update):
            self.token.LB = lb_to_update
            if debug_BNB:
                print(self, "variable changed to", self.variable)
            return True
        else:
            #is_better_then_UB, is_better_then_best_UB = self.get_the_reason_for_failure(lb_to_update)
            #pe = self.get_explanation(is_better_then_UB, is_better_then_best_UB)
            #self.records_dict[pe.winner] = pe

            self.records.append(self.token.LB.__deepcopy__())
            if debug_BNB:
                print(self, "variable did not change to", self.variable)
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
        potential_value_and_information = self.get_potential_values_dict()
        min_variable, min_lb = self.find_min_lb(potential_value_and_information)
        lbs = potential_value_and_information.values()
        self.add_to_records(losers=lbs)
        should_update_token = self.get_should_update_token(min_lb)
        if should_update_token:
            self.token.LB = min_lb
            self.status = BNB_Status.send_token_to_leaf_to_father
        else:
            self.status = BNB_Status.send_empty_to_father


    def find_min_lb(self, info_dict):
        min_key = None
        min_value = None
        min_cost = float('inf')

        for key, value in info_dict.items():
            if value.cost < min_cost:
                min_cost = value.cost
                min_key = key
                min_value = value

        return min_key, min_value

    def add_to_records(self,  losers):
        for lb in losers:
            self.records.append(lb)
        return

    def get_should_update_token(self, min_lb):

        if self.token.best_UB is not None and self.token.best_UB.cost <= min_lb.cost:
            raise Exception("need to check that it works")
            return False
        elif self.token.UB is not None and self.token.UB.cost <= min_lb.cost:
            return False
        else:
            return True

    def compute_receive_all_tokens_from_children_with_empty(self):
        self.reset_token_all_tokens_from_children_with_empty()
        if self.is_root():
            return Exception("TODO need to update best token as root")
        self.select_next_value()
        self.change_statues_after_value_change()

    def compute_receive_all_tokens_from_children_root(self):
        self.create_token_from_children()
        self.reset_token_after_add_from_all_children()
        self.token.best_UB = self.local_UB.__deepcopy__()
        self.best_global_UB = self.local_UB.__deepcopy__()
        self.anytime_variable, self.anytime_context, self.anytime_constraints = self.best_global_UB.get_anytime_info(self.id_, self.neighbors_agents_id)


        self.select_next_value()
        if self.status == BNB_Status.finished_going_over_domain:
            self.status = BNB_Status.finished_algorithm
        else:
            self.status = BNB_Status.send_token_to_children

    def get_potential_values_dict(self):
        ans = {}
        for potential_domain in self.domain:
            lb_to_update = self.get_lb_to_update(potential_domain)
            ans[potential_domain] = lb_to_update
        return ans




    # select_next_value #################################################################################################

    def get_lb_to_update(self,variable_input):
        current_context = self.token.get_lb_copy().context
        constraints = self.get_constraints(current_context = current_context,my_current_value=variable_input)
        token_lb = self.token.get_lb_copy()
        token_lb.update_constraints(self.id_, constraints)
        token_lb.update_context(self.id_, variable_input)
        return token_lb

    def check_specific_ub(self, lb_to_update: SingleInformation, ub: SingleInformation):
        if ub is None:
            return True
        elif lb_to_update < ub:
            return True
        return False

    def is_need_to_update_lb(self, lb_to_update):
        is_better_then_UB = self.check_specific_ub(lb_to_update, self.local_UB)
        is_better_then_best_UB = self.check_specific_ub(lb_to_update, self.token.best_UB)
        return is_better_then_UB and is_better_then_best_UB

    def get_explanation(self, is_better_then_UB, is_better_then_best_UB):
        pe = None
        text = "try to reset token but LB is larger then"
        if not is_better_then_UB:
            text = text + " local UB"
            pe = PruneExplanation(winner=self.local_UB.__deepcopy__(), loser=self.token.LB.__deepcopy__(), text=text,agent_id = self.id_,local_clock =self.local_clock,global_clock =self.global_clock)

        if not is_better_then_best_UB:
            text = text + " global UB"
            pe = PruneExplanation(winner=self.token.best_UB.__deepcopy__(), loser=self.token.LB.__deepcopy__(),
                                  text=text,agent_id = self.id_,local_clock =self.local_clock,global_clock =self.global_clock)
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

    def sends_msgs_token_up_the_tree_leaf_to_father(self):
        self.token.UB = None
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

    def sends_msgs_UB_up_the_tree(self):
        self.token.LB =  self.local_UB.__deepcopy__()
        info = self.token.__deepcopy__()
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

    def compute_receive_all_tokens_from_children(self):
        self.create_token_from_children()
        self.reset_token_after_add_from_all_children()
        self.select_next_value()
        self.change_statues_after_value_change()

    def get_reseted_LB(self,first_value):
        heights_to_include = []
        for id_of_height, height in first_value.heights.items():
            if height <= first_value.heights[self.id_] and self.id_ != id_of_height:
                heights_to_include.append(id_of_height)
        LB = first_value.LB.reset_given_id(heights_to_include)
        return LB.__deepcopy__()

    def reset_token_after_add_from_all_children(self):
        first_value = next(iter(self.tokens_from_children.values()), None)
        LB = self.get_reseted_LB(first_value)
        UB = self.local_UB.__deepcopy__()
        heights = first_value.heights
        self.token = BranchAndBoundToken(LB=LB, UB=UB, heights=heights)


    def check_if_cumulative_token_survived(self,local_token_temp):
        if self.best_global_UB is not None and self.token.best_UB < local_token_temp.LB:
            raise Exception("need to check that it works")
            return False
        if self.local_UB is not None and self.local_UB < local_token_temp.LB:
            return False
        return True

    def update_local_UB(self, aggregated_token):
        if self.local_UB is not None:
            prev_local_UB = self.local_UB.__deepcopy__()
            self.local_UB = aggregated_token.LB.__deepcopy__()
            text = "local UB is not valid any more, children found a lower UB"
            self.add_to_records( losers=[prev_local_UB.__deepcopy__()])
        else:
            if self.best_global_UB is None or (self.best_global_UB is not None and self.local_UB<self.best_global_UB):
                self.local_UB = aggregated_token.LB.__deepcopy__()

    def sanity_check_all_tokens_identical_from_my_height(self):
        variables = []
        for child_token in self.tokens_from_children.values():
            variables.append(child_token.reset_LB_given_id(self.id_))
        all_equal = all(item == variables[0] for item in variables)
        if not all_equal:
            raise Exception("check is wrong")

    def reset_token_all_tokens_from_children_with_empty(self):
        self.sanity_check_all_tokens_identical_from_my_height()
        tokens =  self.tokens_from_children.values()
        first_value = next(iter(tokens), None)
        LB =first_value.reset_LB_given_id(self.id_)
        heights  = first_value.heights
        UB = None
        if self.local_UB is not None:
            UB = self.local_UB.__deepcopy__()
        self.token=BranchAndBoundToken(LB = LB,heights=heights, UB = UB)

    def is_root(self):
        return self.dfs_father is None

    def change_statues_after_value_change(self):
        if self.status == BNB_Status.finished_going_over_domain:
            if self.local_UB is None:
                self.status = BNB_Status.send_empty_to_father
                raise Exception("need to check everything in if  self.local_UB is None")
            else:
                self.token.UB = self.local_UB.__deepcopy__()
                self.token.LB = self.local_UB.__deepcopy__()
                self.status = BNB_Status.send_best_local_token_to_father
            return
        else:
            self.status = BNB_Status.send_token_to_children

    def create_token_from_children(self):
        local_token_temp = None
        for child_token in self.tokens_from_children.values():
            if local_token_temp is None:
                local_token_temp = child_token
            else:
                local_token_temp = local_token_temp + child_token
                self.add_to_records(losers=[local_token_temp.LB])
                did_survive = self.check_if_cumulative_token_survived(local_token_temp)
                if not did_survive:
                    return False
        self.update_local_UB(local_token_temp)
        return True



    def check_to_update_anytime_variable(self):
        if self.token.best_UB is not None:
            self.token.best_UB[1][self.id_][0]
            raise Exception("stopped here")

    def create_local_token_root(self, si:SingleInformation):
        self.token = BranchAndBoundToken(LB=si,heights={self.id_:self.my_height})
        self.reset_tokens_from_children()

    def update_height_and_above_me(self):
        if len(self.above_me) == 0 and not self.is_root():
            father_height = self.token.heights[self.dfs_father]
            self.my_height = father_height+1
            for k in self.token.heights.keys():
                self.above_me.append(k)
            self.token.heights[self.id_] = self.my_height

        for k,v in self.token.heights.items():
            self.heights[k] = v

        self.token.heights = copy_dict(self.heights)































