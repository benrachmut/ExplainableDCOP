

from abc import ABC, abstractmethod

from Globals_ import *
import pulp




class Agent(ABC):

    def __init__(self,id_,D):
        self.global_clock = 0
        self.variable = None
        self.anytime_variable = None
        self.anytime_context = None
        self.anytime_constraints = None
        self.id_ = id_
        self.domain = []
        for i in range(D): self.domain.append(i)
        self.neighbors_obj = None
        self.neighbors_obj_dict = {} #id, obj
        self.neighbors_values = {}
        self.neighbors_agents_id = []
        self.inbox = None
        self.outbox = None
        self.local_clock = 0
        self.records = []
        self.records_dict = {}
        self.unary_constraint = {}

    def create_unary_costs(self,dcop_id):
        rnd_pref_time = random.Random((self.id_+23)*17+(dcop_id)*97)
        for _ in range(5): rnd_pref_time.randint(1,5)
        pref_domain = rnd_pref_time.choice(self.domain)
        self.unary_constraint = {}
        for d in self.domain:
            mu = meeting_schedul_min_cost + meeting_schedul_mu_mult_cost * abs(d - pref_domain)
            std = meeting_schedul_std
            cost = round(random.gauss(mu, std))
            if cost<meeting_schedul_min_cost:
                cost = meeting_schedul_min_cost
            if cost>meeting_schedul_max_cost:
                cost = meeting_schedul_max_cost

            self.unary_constraint[d] = cost



    def set_neighbors(self,neighbors):
        self.neighbors_obj = neighbors
        for n in neighbors:
            a_other = n.get_other_agent(self)
            self.neighbors_agents_id.append(a_other)
            self.neighbors_obj_dict[a_other] = n

        for n_id in self.neighbors_agents_id:
            self.neighbors_values[n_id] = None

    def get_neighbors_tuples(self):
        ans = []
        for n_id in self.neighbors_agents_id:
            ans.append((self.id_,n_id))
        return ans


    def calc_local_price(self, current_context):
        local_cost = 0
        for n_id, current_value in current_context.items():
            neighbor_obj = self.get_n_obj(n_id)
            local_cost = local_cost + neighbor_obj.get_cost(self.id_, self.variable, n_id, current_value)
        return local_cost

    def get_general_info_for_records(self):
        return {"Agent_id":self.id_,"local_clock":self.local_clock,"global_clock":self.global_clock}


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


    def execute_iteration(self,global_clock):
        self.global_clock = global_clock
        msgs = self.inbox.extract()
        if len(msgs)!=0:
            self.update_msgs_in_context(msgs)
            self.change_status_after_update_msgs_in_context(msgs)
            if self.is_compute_in_this_iteration():
                self.local_clock = self.local_clock + 1
                self.compute()
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
    def send_msgs(self): pass



    @abstractmethod
    def change_status_after_update_msgs_in_context(self, msgs): pass


    @abstractmethod
    def change_status_after_send_msgs(self):pass


    def get_constraints(self,current_context, my_current_value):
        ans = {}
        for n_id,n_value in current_context.items():
            neighbor = self.get_n_obj(n_id)
            if neighbor is not None:
                first_tuple = (self.id_,my_current_value)
                second_tuple = (n_id,n_value)
                k, v = neighbor.get_constraint(first_tuple,second_tuple)
                ans[k] =v
        return ans


class Completeness(ABC):

    @abstractmethod
    def is_algorithm_complete(self): pass

class CompleteAlgorithm(Completeness,ABC):

    def is_algorithm_complete(self):
        pass


class IncompleteAlgorithm(Completeness,ABC):
    def is_algorithm_complete(self):
        if self.local_clock == incomplete_iterations:
            return True
        else:
            return False



class DSA_C(IncompleteAlgorithm):
    pass

class MGM(IncompleteAlgorithm):
    pass