import math
from enum import Enum

import globals_
import problems
from Trees import *
from agents import *
from globals_ import *

class BNB_msg_type(Enum):
    token_from_father = 1


class BNB_Status(Enum):
    hold_token_need_to_send_down = 1
    wait_for_tokens_from_children = 2
    receive_token_from_father_continue_to_send_down = 3
    receive_token_from_father_find_best_value = 4

class ShouldPruneException(Exception):
    def __init__(self, message=""):
        Exception.__init__(message)

class BranchAndBoundToken:
    def __init__(self,UB = math.inf,LB = 0, variables = {}):
        self.UB= UB
        self.LB = LB
        self.variables = variables
        self.sender = None


    def agent_include_in_variables(self,id_):
        if id_ in self.variables.keys():
            return True
        else:
            return False


    def add_agent_to_token_variables(self,id_,value,local_cost):
        if self.agent_include_in_variables(id_):
            raise ShouldPruneException("used it when agent is already in token")
        self.variables[id_] = {value:local_cost}
        self.update_cost()

    def update_cost(self):
        costs = [cost for id_, dict_ in self.variables.items() for value, cost in dict_.items()]
        self.LB = sum(costs)
        if self.LB>self.UB:
            raise ShouldPruneException("LB>UB move to the next domain")

    def get_variable_dict(self,agent_list_id):
        ans = {}
        for n_id in agent_list_id:
            ans[n_id] = next(iter(self.variables[n_id]))

            #ans[n_id] = self.variables[n_id][0]
        return ans
    def __str__(self):
        return "UB:"+str(self.UB)+", LB:"+str(self.LB)+", context:"+str(self.variables)

    def __deepcopy__(self, memodict={}):
        return BranchAndBoundToken(self.UB,self.LB,self.variables)



class BranchAndBound(DFS,CompleteAlgorithm):
    def __init__(self, id_, D):
        DFS.__init__(self, id_, D)
        self.domain_index = -1
        self.bnb_token = None
        self.tokens_from_children = {}
        self.reset_tokens_from_children()



    def compute_select_value_for_variable(self):
        self.domain_index = self.domain_index + 1
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

        else:
            print(self.__str__(),"finished moving over all domain - TODO")
            return False

#################
#### Main methods ####
#################

    def is_algorithm_complete(self):
        return False


    def update_msgs_in_context_tree(self,msgs):
        if msgs[0].msg_type == BNB_msg_type.token_from_father :
            self.update_msgs_in_context_tree_receive_token_from_father(msgs)




    def change_status_after_update_msgs_in_context_tree(self, msgs):
        if BNB_msg_type.token_from_father:
            if len(self.dfs_children)==0:
                self.status = BNB_Status.receive_token_from_father_find_best_value
            else:
                self.status = BNB_Status.receive_token_from_father_continue_to_send_down

        if debug_BNB:
            print(self.__str__(),"status is:", self.status)

    def is_compute_in_this_iteration_tree(self):
        if  self.status == BNB_Status.receive_token_from_father_find_best_value\
                or self.status == BNB_Status.receive_token_from_father_continue_to_send_down:
            return True
        else:
            return False

    def compute_tree(self):
        if self.root_of_tree_start_algorithm:
            self.compute_root_starts_the_algorithm()
        if self.status == BNB_Status.receive_token_from_father_continue_to_send_down:
            if not self.compute_select_value_for_variable():
                print("we went through all domain, need to send up")


        if self.status == BNB_Status.receive_token_from_father_find_best_value:
            self.compute_select_value_with_min_cost()
            self.update_token()

            print("TODO- need to check that update token works, i think need to update UB")

    def send_msgs_tree(self):
        if self.status == BNB_Status.hold_token_need_to_send_down or \
                self.status == BNB_Status.receive_token_from_father_continue_to_send_down:
            self.sends_msgs_token_down_the_tree()
        if self.status == BNB_Status.receive_token_from_father_find_best_value:
            self.sends_msgs_token_up_the_tree()
            print("TODO FROM MSG DELIEVERY")





    def change_status_after_send_msgs_tree(self):
        if self.status == BNB_Status.hold_token_need_to_send_down or \
                self.status == BNB_Status.receive_token_from_father_continue_to_send_down:
            self.status = BNB_Status.wait_for_tokens_from_children
        self.bnb_token = None

    def should_record_this_iteration(self): pass

    def record(self): pass

    #################
    #### update in context ####
    #################

    def update_msgs_in_context_tree_receive_token_from_father(self, msgs):
        if len(msgs) > 1:
            raise Exception("should receive a single msg")
        self.bnb_token = msgs[0].information
        #self.bnb_token_local =self.bnb_token.__deepcopy__()



    #################
    #### COMPUTE ####
    #################

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


    def calc_local_price(self, current_context):
        local_cost = 0
        for n_id,current_value in current_context.items():
            neighbor_obj = self.get_n_obj(n_id)
            local_cost = local_cost + neighbor_obj.get_cost(self.id_, self.variable, n_id, current_value)
        return local_cost

    def get_n_obj(self, n_id):
        for ans in self.neighbors_obj:
            if ans.is_agent_in_obj(agent_id_input = n_id):
                return ans

        if ans is None:
            raise Exception("n_id is not correct")

    def calc_potential_cost(self, potential_domain,current_context):
        local_cost = 0
        for n_id, current_value in current_context.items():
            neighbor_obj = self.get_n_obj(n_id)
            local_cost = local_cost + neighbor_obj.get_cost(self.id_, potential_domain, n_id, current_value)
        return local_cost

    def compute_select_value_with_min_cost(self):
        current_context = self.bnb_token.get_variable_dict(self.above_me)
        potential_value_and_cost = {}
        for potential_domain in self.domain:
            potential_cost = self.calc_potential_cost(potential_domain, current_context)
            potential_value_and_cost[potential_domain] = potential_cost
        self.variable = min(potential_value_and_cost, key=lambda k: potential_value_and_cost[k])

    def update_token(self,local_cost):

        try:
            self.bnb_token.add_agent_to_token_variables(id_=self.id_, value=self.variable, local_cost=local_cost)
            return True

        except ShouldPruneException:
            if debug_BNB:
                print(self.__str__(), "pruned", self.domain_index)
            self.domain_index = self.domain_index + 1






