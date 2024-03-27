from abc import ABC
from enum import Enum
from globals import Msg
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

        # dfs variables
        self.context_amount_of_neighbors = {}
        self.dfs_tree_token = None
        self.dfs_children = [ ]
        self.dfs_father = None



    def initialize(self):
        msgs = []
        for a_id in self.neighbors_agents_id:
            sender = self.id_
            receiver = a_id
            information = len(self.neighbors_agents_id)
            msg = Msg(sender=sender,receiver=receiver,information=information,msg_type = BranchAndBound_MSG.neighbors_amount)
            msgs.append(msg)
        self.outbox.insert(msgs)



    def update_msgs_in_context(self, msgs):
        if self.status == BranchAndBound_Status.wait_for_amount_of_neighbors:
            if len(msgs) != len(self.neighbors_obj):
                raise Exception ("not a synchronous iteration")

        for msg in msgs:
            if msg.msg_type==BranchAndBound_MSG.neighbors_amount:
                self.update_msgs_in_context_neighbors_amount(msg)

    def change_status_after_update_msgs_in_context(self,msgs):
        if self.status == BranchAndBound_Status.wait_for_amount_of_neighbors:
            self.status = BranchAndBound_Status.create_dfs


    def is_compute_in_this_iteration(self):
        if self.status == BranchAndBound_Status.create_dfs:
            if self.is_root or self.is_holding_tree_token():
                return True
            else:
                return False



    def compute(self):
        if self.status == BranchAndBound_Status.create_dfs:
            if self.is_root:
                self.dfs_tree_token = [self.id_]
                max_id = max(self.context_amount_of_neighbors, key=lambda id_: (self.context_amount_of_neighbors[id_], id_))
                self.dfs_children.append(max_id)
                del self.context_amount_of_neighbors[max_id]
                self.dfs_father = None
                stop here
                self.is_root = False




    def should_record_this_iteration(self):
        pass

    def record(self):
        pass

    def send_msgs(self):
        pass

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


