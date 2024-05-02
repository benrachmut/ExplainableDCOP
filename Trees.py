import math
from abc import ABC, abstractmethod
from enum import Enum
from globals_ import *
from agents import  Agent
import main



class DFS_Status(Enum):
    wait_for_amount_of_neighbors = 1
    create_dfs = 2

class DFS_MSG(Enum):
    neighbors_amount = 1
    tree_token = 2





class DFS(Agent,ABC):

    def __init__(self, id_, D):
        Agent.__init__(self,id_,D,)
        self.status = DFS_Status.wait_for_amount_of_neighbors

        ### DFS
        self.context_amount_of_neighbors = {}
        self.dfs_children = [ ]
        self.dfs_father = None
        self.root_of_tree_start_algorithm = False

        self.above_me = []
        self.below_me = []

    def initialize(self):
        msgs = []
        for a_id in self.neighbors_agents_id:
            sender = self.id_
            receiver = a_id
            information = len(self.neighbors_agents_id)
            msgs.append(Msg(sender=sender, receiver=receiver, information=information, msg_type = DFS_MSG.neighbors_amount))
        self.outbox.insert(msgs)

    def update_msgs_in_context(self, msgs):
        if self.status == DFS_Status.wait_for_amount_of_neighbors:
            if len(msgs) != len(self.neighbors_obj):
                raise Exception ("not a synchronous iteration")

        flag = False
        for msg in msgs:
            if msg.msg_type == DFS_MSG.neighbors_amount:
                self.update_msgs_in_context_neighbors_amount(msg)
                flag = True
            if msg.msg_type == DFS_MSG.tree_token:
                self.dfs_tree_token = msg.information
                if self.is_first_action_in_tree():
                    self.dfs_father = msg.sender
                flag = True

        if not flag:
            self.update_msgs_in_context_tree(msgs)

    def change_status_after_update_msgs_in_context(self,msgs):
        if self.status == DFS_Status.wait_for_amount_of_neighbors or not self.all_neighbors_are_in_tree():
            self.status = DFS_Status.create_dfs

        else:
            self.change_status_after_update_msgs_in_context_tree(msgs)

    def is_compute_in_this_iteration(self):
        if self.status == DFS_Status.create_dfs:
            if  self.is_holding_tree_token():
                return True
            else:
                return False
        else:
            return self.is_compute_in_this_iteration_tree()

    def compute(self):
        if self.status == DFS_Status.create_dfs:
            self.remove_all_agents_in_token()
            if len(self.context_amount_of_neighbors) != 0:
                self.token_goes_down()
            elif (self.dfs_father is not None):
                self.token_goes_up()
            else:
                self.root_of_tree_start_algorithm = True
                self.below_me = self.neighbors_agents_id
                self.compute_tree()
        else: self.compute_tree()




    def send_msgs(self):
        if self.status == DFS_Status.create_dfs:
            if self.can_pick_a_child():
                info = self.dfs_tree_token[0]
                msgs = [Msg(sender=self.id_, receiver=self.dfs_tree_token[1], information=info, msg_type=DFS_MSG.tree_token)]
                self.outbox.insert(msgs)
                self.dfs_tree_token = None
        else:
            self.send_msgs_tree()

    def change_status_after_send_msgs(self):
        self.change_status_after_send_msgs_tree()

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

    ##################
    #### compute
    ##################

    def remove_all_agents_in_token(self):
        for a_id in self.dfs_tree_token:
            if a_id in self.context_amount_of_neighbors:
                del self.context_amount_of_neighbors[a_id]

    def token_goes_down(self):
        max_id = max(self.context_amount_of_neighbors,
                     key=lambda id_: (self.context_amount_of_neighbors[id_], id_))
        self.dfs_children.append(max_id)
        del self.context_amount_of_neighbors[max_id]

        if debug_DFS_tree:
            index_to_print = len(self.dfs_children)-1
            print("A_", str(self.id_), "sends token down to", "A_" + str(self.dfs_children[index_to_print]))
        if len(self.above_me) == 0:
            self.create_above_me()
        else:
            self.below_me.append(max_id)


        self.dfs_tree_token.append(self.id_)
        self.dfs_tree_token = (self.dfs_tree_token, max_id)

    def token_goes_up(self):
        if self.id_ not in self.dfs_tree_token:
            self.dfs_tree_token.append(self.id_)

        if len(self.dfs_children) == 0:
            self.create_above_me()
        else:
            self.create_below_me()


        self.dfs_tree_token = (self.dfs_tree_token, self.dfs_father)


        if debug_DFS_tree:
            print("A_", str(self.id_), "sends token up to", "A_" + str(self.dfs_father))
            print("A_", str(self.id_), "above", self.above_me)
            print("A_", str(self.id_), "below", self.below_me)


    @abstractmethod
    def update_msgs_in_context_tree(self,msgs):pass

    @abstractmethod
    def change_status_after_update_msgs_in_context_tree(self, msgs): pass

    @abstractmethod
    def is_compute_in_this_iteration_tree(self):pass

    @abstractmethod
    def compute_tree(self):pass

    @abstractmethod
    def send_msgs_tree(self):pass


    def create_below_me(self):

        for n_id in self.dfs_tree_token:
            if n_id not in self.above_me and n_id in self.neighbors_agents_id and n_id not in self.below_me:
                self.below_me.append(n_id)

    def create_above_me(self):
        for n_id in self.dfs_tree_token:
            if n_id in self.neighbors_agents_id and n_id not in self.above_me:
                self.above_me.append(n_id)

    def all_neighbors_are_in_tree(self):
        agents_in_tree = self.above_me + self.below_me
        for n_id in self.neighbors_agents_id:
            if n_id not in agents_in_tree:
                return False
        return True



