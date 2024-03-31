from abc import ABC
from enum import Enum
from globals import *
from agents import CompleteAlgorithm, Agent


class BranchAndBound_Status(Enum):
    wait_for_amount_of_neighbors = 1
    create_dfs = 2

class BranchAndBound_MSG(Enum):
    neighbors_amount = 1
    tree_token = 2





class BranchAndBound(CompleteAlgorithm):

    def __init__(self, id_, D):
        CompleteAlgorithm.__init__(self,id_,D,)
        self.status = BranchAndBound_Status.wait_for_amount_of_neighbors
        self.context_amount_of_neighbors = {}
        self.dfs_children = [ ]
        self.dfs_father = None

    def initialize(self):
        msgs = []
        for a_id in self.neighbors_agents_id:
            sender = self.id_
            receiver = a_id
            information = len(self.neighbors_agents_id)
            msgs.append(Msg(sender=sender,receiver=receiver,information=information,msg_type = BranchAndBound_MSG.neighbors_amount))
        self.outbox.insert(msgs)

    def update_msgs_in_context(self, msgs):
        if self.status == BranchAndBound_Status.wait_for_amount_of_neighbors:
            if len(msgs) != len(self.neighbors_obj):
                raise Exception ("not a synchronous iteration")

        for msg in msgs:
            if msg.msg_type == BranchAndBound_MSG.neighbors_amount:
                self.update_msgs_in_context_neighbors_amount(msg)

            if msg.msg_type == BranchAndBound_MSG.tree_token:
                self.dfs_tree_token = msg.information
                if self.is_first_action_in_tree():
                    self.dfs_father = msg.sender

    def change_status_after_update_msgs_in_context(self,msgs):
        if self.status == BranchAndBound_Status.wait_for_amount_of_neighbors:
            self.status = BranchAndBound_Status.create_dfs


    def is_compute_in_this_iteration(self):
        if self.status == BranchAndBound_Status.create_dfs:
            if  self.is_holding_tree_token():
                return True
            else:
                return False




    def compute(self):
        if self.status == BranchAndBound_Status.create_dfs:
            self.remove_all_agents_in_token()
            if len(self.context_amount_of_neighbors) != 0:
                self.token_goes_down()
            elif (self.dfs_father is not  None):
                self.token_goes_up()
            else:
                self.status = BranchAndBound_Status.





    def should_record_this_iteration(self):
        return False

    def record(self):
        pass

    def send_msgs(self):
        if self.status == BranchAndBound_Status.create_dfs:
            if self.can_pick_a_child():
                info = self.dfs_tree_token[0]
                msgs = [Msg(sender=self.id_,receiver=self.dfs_tree_token[1],information=info,msg_type=BranchAndBound_MSG.tree_token)]
                self.outbox.insert(msgs)
                self.dfs_tree_token = None

            elif self.did_not_select_child_and_has_no_father() :
                pass # move to next statues

    def did_not_select_child_and_has_no_father(self):
        return self.dfs_tree_token[1] is None and self.dfs_father is None

    def can_pick_a_child(self):
        return self.dfs_tree_token[1] is not None

    def is_algorithm_complete(self):
        return False

#### update_msgs_in_context
    def update_msgs_in_context_neighbors_amount(self, msg):
        receiver = msg.receiver
        if receiver != self.id_:
            raise Exception("mistake in mailer")
        sender = msg.sender
        amount_of_neighbors = msg.information
        self.context_amount_of_neighbors[sender] = amount_of_neighbors

    def is_holding_tree_token(self):
        return self.dfs_tree_token is not None

    def is_first_action_in_tree(self):
        return self.dfs_father is None and len(self.dfs_children) == 0
    #### compute


    def remove_all_agents_in_token(self):
        for a_id in self.dfs_tree_token:
            if a_id in self.context_amount_of_neighbors:
                del self.context_amount_of_neighbors[a_id]

    def token_goes_down(self):
        max_id = max(self.context_amount_of_neighbors,
                     key=lambda id_: (self.context_amount_of_neighbors[id_], id_))
        self.dfs_children.append(max_id)
        del self.context_amount_of_neighbors[max_id]

        if bnb_tree_debug:
            print("A_", str(self.id_), "sends token down to", "A_" + str(self.dfs_children[0]))

        self.dfs_tree_token.append(self.id_)
        self.dfs_tree_token = (self.dfs_tree_token, max_id)

    def token_goes_up(self):
        if self.id_ not in self.dfs_tree_token:
            self.dfs_tree_token.append(self.id_)
        self.dfs_tree_token = (self.dfs_tree_token, self.dfs_father)

        if bnb_tree_debug:
            print("A_", str(self.id_), "sends token up to", "A_" + str(self.dfs_father))







