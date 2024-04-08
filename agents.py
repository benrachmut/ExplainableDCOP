

from abc import ABC, abstractmethod

from globals_ import *




class Agent(ABC):

    def __init__(self,id_,D):
        self.variable = None
        self.id_ = id_
        self.domain = []
        for i in range(D): self.domain.append(i)
        self.neighbors_obj = None
        self.neighbors_agents_id = []
        self.inbox = None
        self.outbox = None
        self.local_clock = 0

    def set_neighbors(self,neighbors):
        self.neighbors_obj = neighbors
        for n in neighbors:
            a_other = n.get_other_agent(self)
            self.neighbors_agents_id.append(a_other)

    def get_neighbors_tuples(self):
        ans = []
        for n_id in self.neighbors_agents_id:
            ans.append((self.id_,n_id))
        return ans

    def execute_iteration(self):
        msgs = self.inbox.extract()
        if len(msgs)!=0:
            self.update_msgs_in_context(msgs)
            self.change_status_after_update_msgs_in_context(msgs)
            if self.is_compute_in_this_iteration():
                self.local_clock = self.local_clock + 1
                self.compute()
                if self.should_record_this_iteration():
                    self.record()
                self.send_msgs()
                self.change_status_after_send_msgs()

    def __str__(self):
        return "A_"+str(self.id_)

    @abstractmethod
    def initialize(self): pass

    @abstractmethod
    def update_msgs_in_context(self,msgs): pass

    @abstractmethod
    def is_compute_in_this_iteration(self): pass

    @abstractmethod
    def compute(self): pass

    @abstractmethod
    def should_record_this_iteration(self): pass

    @abstractmethod
    def record(self): pass

    @abstractmethod
    def send_msgs(self): pass



    @abstractmethod
    def change_status_after_update_msgs_in_context(self, msgs): pass


    @abstractmethod
    def change_status_after_send_msgs(self):pass


class Completeness(ABC):

    @abstractmethod
    def is_algorithm_complete(self): pass

class CompleteAlgorithm(Completeness,ABC):

    def is_algorithm_complete(self): pass


class IncompleteAlgorithm(Completeness,ABC):
    def is_algorithm_complete(self):
        if self.local_clock == incomplete_iterations:
            return True
        else:
            return False


