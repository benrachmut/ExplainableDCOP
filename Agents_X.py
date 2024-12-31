import copy
from abc import ABC, abstractmethod
from functools import cmp_to_key

from Globals_ import *


class MsgTypeX(Enum):
    solution_value = 1
    solution_request = 2


class AgentXStatues(Enum):
    wait_for_solution_value = 1
    wait_for_solution_constraints = 2
    idle = 3
    request_solution_constraints = 4
    request_self_solution_and_alternatives = 5
    request_solution_values = 6

class CostComparisonCounter:
    def __init__(self):
        self.count = 0

    def comparator(self, a, b):
        self.count += 1
        return (b.cost > a.cost) - (b.cost < a.cost)  # Comparison logic for descending order


class Constraint:
    def __init__(self,first_id, first_value, second_id,second_value, cost):

        if first_id<second_id:
            self.first_id = first_id
            self.first_value = first_value
            self.second_id = second_id
            self.second_value = second_value
        else:
            self.first_id = second_id
            self.first_value = second_value
            self.second_id = first_id
            self.second_value = first_value
        self.cost = cost

    def __str__(self):
        return "[<A_"+str(self.first_id)+"="+str(self.first_value)+",A_"+str(self.second_id)+"="+str(self.second_value)+">,cost=",str(self.cost)+"]"


    def __repr__(self):
        return self.__str__()



class AgentX(ABC):

    def __init__(self,id_,variable,domain,neighbors_agents_id,neighbors_obj):
        self.alternative_partial_assignment =None
        self.global_clock = 0
        self.id_ = id_
        self.neighbors_obj_dict = neighbors_obj
        self.variable = variable
        self.domain = domain
        self.neighbors_agents_id = neighbors_agents_id
        self.local_view = {}
        for k in self.neighbors_agents_id:
            self.local_view[k]=None
        self.inbox = None
        self.outbox = None
        self.local_clock = 0
        self.atomic_operations = 0
        self.statues = AgentXStatues.wait_for_solution_value
        self.solution_constraints = {}
        self.alternative_constraints = {}

    def get_general_info_for_records(self):
        return {"Agent_id":self.id_,"local_clock":self.local_clock,"global_clock":self.global_clock}


    def execute_iteration(self):

        msgs = self.inbox.extract()

        if len(msgs)!=0:
            self.prev_status = copy.deepcopy(self.statues)
            self.update_msgs_in_context(msgs)
            self.change_status_after_update_msgs_in_context(msgs)
            self.print_after_statues_after_receive_msgs()
            if self.is_compute_in_this_iteration():
                self.atomic_operations = self.compute()
                self.print_after_compute()
                if self.atomic_operations is None: raise Exception("compute must return NCLO count")
                self.local_clock += self.atomic_operations
                self.send_msgs()
                self.prev_status = copy.deepcopy(self.statues)
                self.change_status_after_send_msgs()
                self.print_after_send_msgs()

            self.atomic_operations = 0

    def __str__(self):
        return "A_"+str(self.id_)



    def update_solution_value_in_local_view(self,msg):
        if msg.msg_type == MsgTypeX.solution_value:
            sender = msg.sender
            info = msg.information
            self.local_view[sender] = info

    def local_view_has_nones(self):
        for v in self.local_view.values():
            if v is None:
                return True
        return False

    def get_self_solution_constraints(self):
        constraints = []
        total_cost = 0
        for n_id,n_obj in self.neighbors_obj_dict.items():
            my_id = self.id_
            my_value = self.variable
            n_value = self.local_view[n_id]
            cost = n_obj.get_cost(my_id, my_value, n_id, n_value)
            total_cost += cost
            constraints.append(Constraint(my_id,my_value,n_id,n_value,cost))
        return total_cost,constraints

    def get_variables_in_alternative_partial_assignment(self):
        ans = []
        for dict_ in self.alternative_partial_assignment:
            ans.append(list(dict_.keys())[0])
        return ans

    def get_val_from_alternative_partial_assignment(self,input_id):
        for dict_ in self.alternative_partial_assignment:
            current_key = list(dict_.keys())[0]
            if current_key == input_id:
                return list(dict_.values())[0]
    def get_self_alternative_constraints(self):
        constraints = []
        total_cost = 0
        flag_all = False
        variables_in_alternative_partial_assignment = self.get_variables_in_alternative_partial_assignment()
        if self.id_ in variables_in_alternative_partial_assignment:
            my_val = self.get_val_from_alternative_partial_assignment(self.id_)
            flag_all = True
        else:
            my_val = self.variable

        flag_other = False
        for n_id, n_obj in self.neighbors_obj_dict.items():
            if n_id in variables_in_alternative_partial_assignment:
                n_val = self.get_val_from_alternative_partial_assignment(n_id)
                flag_other = True
            else:
                n_val = self.local_view[n_id]
            if flag_other or flag_all:
                cost = n_obj.get_cost(self.id_, my_val,n_id,n_val)
                total_cost+=total_cost
                constraints.append(Constraint(self.id_,my_val,n_id,n_val,cost))
            flag_other  =False
        return total_cost, constraints

    @abstractmethod
    def initialize(self):
       pass


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


    def compute_request_solution_constraints(self):
            total_cost,constraints_list = self.get_self_solution_constraints()
            self.solution_constraints[self.id_] = constraints_list
            NCLO_count = len(constraints_list)
            return total_cost,NCLO_count*2

    def compute_request_alternative_constraints(self):
            total_cost,constraints_list = self.get_self_alternative_constraints()
            self.alternative_constraints[self.id_] = constraints_list
            NCLO_count = len(constraints_list)
            return NCLO_count



    def print_after_statues_after_receive_msgs(self):
        if distributed_explanation_debug:
            print("A_"+str(self.id_),"statues was",self.statues.name,"and now is", self.statues.name)

    def print_after_compute(self):
        if distributed_explanation_debug:
            print("A_" + str(self.id_), "compute took",  self.atomic_operations, "oporations, local time is:",self.local_clock)

    def print_after_send_msgs(self):
        if distributed_explanation_debug:
            print("A_" + str(self.id_), "statues was", self.statues.name, "and now is", self.statues.name+",local time is:",self.local_clock)


class AgentX_Query(AgentX,ABC):
    def __init__(self, id_, variable, domain, neighbors_agents_id, neighbors_obj_dict,query):
        AgentX.__init__(self, id_, variable, domain, neighbors_agents_id,neighbors_obj_dict)
        self.query = query
        self.alternative_partial_assignment= query.alternative_partial_assignments
        self.solution_cost = 0
        self.is_done = False
        self.solution_constraints_for_explanations = []
        self.alternative_constraints_for_explanations = []

    def is_termination_condition_met(self): return self.is_done


    def get_msgs_to_send_solution_request(self):
        msgs = []
        for n_id in self.query.variables_in_query:
            if n_id!= self.id_:
                msgs.append(
                    Msg(sender=self.id_, receiver=n_id, information=None, msg_type=MsgTypeX.solution_request, bandwidth=1,NCLO=self.local_clock))
        return msgs

class AgentX_Query_BroadcastCentral(AgentX_Query):
    def __init__(self,id_,variable,domain,neighbors_agents_id,neighbors_obj_dict,query):
        AgentX_Query.__init__(self,id_,variable,domain,neighbors_agents_id,neighbors_obj_dict,query)
        for agent_in_query in self.query.variables_in_query:
            if agent_in_query not in self.neighbors_agents_id:
                self.neighbors_agents_id.append(agent_in_query)

    def initialize(self):
        sender = self.id_
        information = self.variable
        msg_type= MsgTypeX.solution_value
        msg_list = []
        for n_id in self.neighbors_agents_id:
            receiver = n_id
            bandwidth = 1

            msg = Msg(sender,receiver,information,msg_type,bandwidth,NCLO = self.atomic_operations )
            msg_list.append(msg)
        self.outbox.insert(msg_list)


    def update_msgs_in_context(self,msgs):
        for msg in msgs:
            self.update_solution_value_in_local_view(msg)

    def change_status_after_update_msgs_in_context(self, msgs):
        if self.statues == AgentXStatues.wait_for_solution_value and self.local_view_has_nones()==False and self.query_only_ask_self() == False:
            self.statues = AgentXStatues.request_solution_constraints
        if self.statues == AgentXStatues.wait_for_solution_value and self.local_view_has_nones() == False \
                and self.query_only_ask_self()  :
            self.statues = AgentXStatues.request_self_solution_and_alternatives


    def is_compute_in_this_iteration(self):
        if self.statues == AgentXStatues.request_solution_constraints:
            return True
        if self.statues == AgentXStatues.request_self_solution_and_alternatives:
            return True
        else:
            False

    def compute(self):
        if self.statues == AgentXStatues.request_solution_constraints:
            if self.am_i_in_query():
                return self.compute_request_solution_constraints()
            return 0
        if self.statues == AgentXStatues.request_self_solution_and_alternatives:
            total_cost_solution,constraints_solution_list = self.get_self_solution_constraints()
            total_cost_alternative,constraints_alternative_list = self.get_self_alternative_constraints()
            counter = CostComparisonCounter()
            sorted_constraints = sorted(constraints_alternative_list, key=cmp_to_key(counter.comparator),)
            sorted_counter = counter.count

            sum_of_alt_constraint_count = 0
            get only relavent constraints (in alternative_constraints_for_explanations) until exceed solution and add to NCLO COUNT

            alternative_constraints_for_explanations
            return NCLO_self_solution+NCLO_alternative_solution+sorted_counter+sum_of_alt_constraint_count

    def send_msgs(self):
        if self.statues == AgentXStatues.request_solution_constraints:
            msgs = self.get_msgs_to_send_solution_request()

        self.outbox.insert(msgs)

    def change_status_after_send_msgs(self):
        if self.statues == AgentXStatues.request_solution_constraints:
            self.statues = AgentXStatues.wait_for_solution_constraints

    def query_only_ask_self(self):
        first_cond= len(self.query.variables_in_query) == 1
        second_cond = list(self.query.variables_in_query)[0]==self.id_
        return first_cond and second_cond

    def am_i_in_query(self):
        return self.id_ in self.query.variables_in_query


class AgentX_BroadcastCentral(AgentX):
    def __init__(self,id_,variable,domain,neighbors_agents_id,neighbors_obj_dict):
        AgentX.__init__(self,id_,variable,domain,neighbors_agents_id,neighbors_obj_dict)


    def initialize(self):
        pass  # do nothing, wait for solution request

    def update_msgs_in_context(self, msgs):
        for msg in msgs:
            self.update_solution_value_in_local_view(msg)


    def change_status_after_update_msgs_in_context(self, msgs):
        if self.statues == AgentXStatues.wait_for_solution_value:
            self.statues = AgentXStatues.idle
        if (len(msgs)==1) and msgs[0].msg_type ==MsgTypeX.solution_request:
            self.statues = AgentXStatues.request_solution_values



    def is_compute_in_this_iteration(self):
        return False

    def compute(self): pass

    def send_msgs(self): pass

    def change_status_after_send_msgs(self):pass








class AgentX_Query_BroadcastDistributed(AgentX_Query_BroadcastCentral):
    def __init__(self,id_,variable,domain,neighbors_agents_id,neighbors_obj_dict,query):
        AgentX_Query_BroadcastCentral.__init__(self,id_,variable,domain,neighbors_agents_id,neighbors_obj_dict,query)


    def compute_request_solution_constraints(self):
        total_cost, constraints_list = self.get_self_solution_constraints()
        self.solution_constraints[self.id_] = constraints_list
        NCLO_count = len(constraints_list)
        self.solution_cost+=total_cost
        return NCLO_count*2

class AgentX_BroadcastDistributed(AgentX_BroadcastCentral):
    def __init__(self,id_,variable,domain,neighbors_agents_id):
        AgentX_BroadcastCentral.__init__(self,id_,variable,domain,neighbors_agents_id)



    def compute_request_solution_constraints(self):
        total_cost, constraints_list = self.get_self_solution_constraints()
        self.my_solution_constraints = constraints_list
        NCLO_count = len(constraints_list)
        self.solution_cost+=total_cost
        return NCLO_count*2


    def get_self_solution_constraints(self):
        pass