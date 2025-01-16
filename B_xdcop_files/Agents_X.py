from abc import ABC, abstractmethod
from functools import cmp_to_key

from B_xdcop_files.Queries import *


class MsgTypeX(Enum):
    solution_value_request = 1
    solution_request = 2
    AgentXQTerminate = 3
    solution_constraint_request = 4
    solution_value_information = 5
    solution_constraints_information = 6
    alternative_constraints_request = 7
    alternative_constraints_information = 8

class AgentXStatues(Enum):
    wait_for_solution_value = 1
    wait_for_solution_constraints = 2
    #idle = 3
    request_solution_constraints = 4
    request_self_solution_and_alternatives = 5
    request_solution_values = 6
    send_solution_value = 7
    wait_for_solution_value_then_send_solution_constraints = 8
    send_solution_constraints_to_a_q = 9
    request_alternative_constraints = 10
    wait_for_alternative_constraints =11
    send_alternative_constraints_to_a_q = 12
    check_if_explanation_is_complete = 13

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
        return "[<A_"+str(self.first_id)+"="+str(self.first_value)+",A_"+str(self.second_id)+"="+str(self.second_value)+">,cost=",str(self.cost)+"]"

    def __eq__(self, other):
        first_cond = other.first_id == self.first_id
        second_cond = other.first_value == self.first_value
        third_cond = other.second_id == self.second_id
        forth_cond = other.second_value == self.second_value
        return first_cond and second_cond and third_cond and forth_cond


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
        self.statues = []
        self.is_done = False

        self.solution_constraints = {}
        self.alternative_constraints = {}

        self.who_asked_for_solution_value=[]
        self.a_q = None
        self.delta_nclo = 0
    def get_general_info_for_records(self):
        return {"Agent_id":self.id_,"local_clock":self.local_clock,"global_clock":self.global_clock}


    def execute_iteration(self):

        msgs = self.inbox.extract()

        if len(msgs)!=0:
            self.prev_status = copy.deepcopy(self.statues)
            self.update_local_clock(msgs)
            self.update_msgs_in_context(msgs)
            self.change_status_after_update_msgs_in_context(msgs)
            self.print_after_statues_after_receive_msgs()
            if self.is_compute_in_this_iteration():
                self.atomic_operations = self.compute()
                self.local_clock += self.atomic_operations
                self.print_after_compute()

                if self.atomic_operations is None: raise Exception("compute must return NCLO count")

            self.send_msgs()
            self.prev_status = copy.deepcopy(self.statues)
            self.change_status_after_send_msgs()
            self.print_after_send_msgs()
            self.atomic_operations = 0

    def __str__(self):
        return "A_"+str(self.id_)


    ########## UPDATE INFO FROM MESSAGE
    def update_solution_value_infrormation_in_local_view(self, msg):
        if msg.msg_type == MsgTypeX.solution_value_information:
            sender = msg.sender
            info = msg.information
            self.local_view[sender] = info

    def update_solution_value_request_data(self,msg):
        if msg.msg_type == MsgTypeX.solution_value_request:
            self.who_asked_for_solution_value.append(msg.sender)

    ######### send msgs
    def send_solution_value_information(self, msgs_to_send):
        if AgentXStatues.send_solution_value in self.statues:
            for n_id in self.who_asked_for_solution_value:
                msgs_to_send.append(Msg(sender = self.id_, receiver=n_id, information=self.variable, msg_type = MsgTypeX.solution_value_information, bandwidth=1, NCLO = self.local_clock))
            self.who_asked_for_solution_value = []

    def local_view_has_nones(self):
        for v in self.local_view.values():
            if v is None:
                return True
        return False

    def solution_constraints_has_none(self):
        for v in self.solution_constraints.values():
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

        self.solution_constraints[self.id_] = constraints
        return total_cost



    def get_self_alternative_constraints(self):
        constraints = []
        total_cost = 0
        flag_all = False
        if self.id_ in self.alternative_partial_assignment.keys():
            my_val = self.alternative_partial_assignment[self.id_]
            flag_all = True
        else:
            my_val = self.variable

        if isinstance(my_val, list):
            my_val = my_val[0]

        flag_other = False
        for n_id, n_obj in self.neighbors_obj_dict.items():
            if n_id in self.alternative_partial_assignment.keys():
                n_val = self.alternative_partial_assignment[n_id]
                flag_other = True
            else:
                n_val = self.local_view[n_id]

            if isinstance(n_val, list):
                n_val = n_val[0]

            if flag_other or flag_all:
                cost = n_obj.get_cost(self.id_, my_val,n_id,n_val)
                if cost>0:
                    total_cost+=total_cost
                    constraints.append(Constraint(self.id_,my_val,n_id,n_val,cost))
            flag_other  =False
        self.alternative_constraints[self.id_] = constraints
        return total_cost

    @abstractmethod
    def initialize(self):
       pass


    @abstractmethod
    def update_msgs_in_context(self,msgs): pass

    def is_compute_in_this_iteration(self):
        if AgentXStatues.request_solution_constraints in self.statues:
            return True
        if AgentXStatues.request_self_solution_and_alternatives in self.statues:
            return True
        if AgentXStatues.send_solution_value in self.statues:
            return True
        if AgentXStatues.send_solution_constraints_to_a_q in self.statues:
            return True
        if AgentXStatues.request_alternative_constraints in self.statues:
            return True
        if AgentXStatues.send_alternative_constraints_to_a_q in self.statues:
            return True
        if AgentXStatues.check_if_explanation_is_complete in self.statues:
            return True
        else:
            False

    @abstractmethod
    def compute(self): pass

    @abstractmethod
    def send_msgs(self): pass

    @abstractmethod
    def change_status_after_update_msgs_in_context(self, msgs): pass

    @abstractmethod
    def change_status_after_send_msgs(self):pass

    def send_solution_value_request(self,msgs):
        if AgentXStatues.request_solution_values in self.statues:
            sender = self.id_
            # information = self.variable
            msg_type = MsgTypeX.solution_value_request
            for n_id in self.neighbors_agents_id:
                receiver = n_id
                bandwidth = 1
                msg = Msg(sender, receiver, None, msg_type, bandwidth, NCLO=self.atomic_operations)
                msgs.append(msg)


    #def compute_request_alternative_constraints(self):
    #        total_cost,constraints_list = self.get_self_alternative_constraints()
    #        self.alternative_constraints[self.id_] = constraints_list
    #        NCLO_count = len(constraints_list)
    #        return NCLO_count



    def print_after_statues_after_receive_msgs(self):
        prev_status = self.get_statues_from_list(self.prev_status)
        current_status = self.get_statues_from_list(self.statues)
        if distributed_explanation_debug:
            print("A_"+str(self.id_),"statues was",prev_status,"and now is", current_status)

    def print_after_compute(self):
        if distributed_explanation_debug:
            print("A_" + str(self.id_), "compute took",  self.atomic_operations, "oporations, local time is:",self.local_clock)

    def print_after_send_msgs(self):
        prev_status = self.get_statues_from_list(self.prev_status)
        current_status = self.get_statues_from_list(self.statues)
        if distributed_explanation_debug:
            print("A_" + str(self.id_), "statues was", prev_status, "and now is",current_status+",local time is:",self.local_clock)

    def get_statues_from_list(self, stat_list):
        ans = ""
        for i in stat_list:
            if len(ans)==0:
                ans += i.name
            else:
                ans+=(","+i.name)
        if ans == "":
            ans = "idle"
        return ans

    def update_local_clock(self, msgs):
        max_nclo = max(msgs,key= lambda x: x.NCLO).NCLO

        if max_nclo> self.local_clock:
            self.delta_nclo = max_nclo - self.local_clock
            self.local_clock = max_nclo


class AgentX_Query(AgentX,ABC):
    def __init__(self, id_, variable, domain, neighbors_agents_id, neighbors_obj_dict,query):
        AgentX.__init__(self, id_, variable, domain, neighbors_agents_id,neighbors_obj_dict)
        self.alternative_constraints_cost_single_addition = []
        self.alternative_delta_constraints_cost_per_addition = []
        #self.alternative_delta_constraints_cost_per_NCLO = {}
        self.query = query
        #if isinstance(query,QueryMeetingScheduling):
        #    self.alternative_partial_assignment= query.alternative_partial_assignments[0]
        #else:
        self.alternative_partial_assignment= query.alternative_values
        self.solution_cost = 0
        self.alternative_cost = 0
        self.NCLO_for_valid_solution = 0

        self.alternative_constraints_for_explanations = []
        self.alternative_constraints_inbox = []
        #self.statues.append(AgentXStatues.wait_for_solution_value)
        for v_q in self.query.variables_in_query:
            self.solution_constraints[v_q] = None
            #self.alternative_constraints[v_q] = None
    def is_termination_condition_met(self): return self.is_done
    def calc_sum_of_solution_cost(self):
        NCLO = 0
        const_list = []
        self.solution_cost = 0
        for id_,const_list_of_id in self.solution_constraints.items():
            for const in const_list_of_id:
                if const not in const_list:
                    const_list.append(const)


        for const in const_list:
            NCLO+=1
            self.solution_cost+=const.cost
        return NCLO

    def get_msgs_to_send_solution_request(self):
        msgs = []
        for n_id in self.query.variables_in_query:
            if n_id!= self.id_:
                msgs.append(
                    Msg(sender=self.id_, receiver=n_id, information=None, msg_type=MsgTypeX.solution_request, bandwidth=1,NCLO=self.local_clock))
        return msgs

    def get_alternative_cost(self):
        ans = 0
        for const in self.alternative_constraints_for_explanations:
            ans+=const.cost
        return ans

    def is_finish_going_for_alternatives(self,who_you_took_from):
        return True
    def initialize(self):
        self.statues.append(AgentXStatues.request_solution_values)
        msgs = []
        self.send_solution_value_request(msgs)
        self.outbox.insert(msgs)

        self.statues.remove(AgentXStatues.request_solution_values)
        self.statues.append(AgentXStatues.wait_for_solution_value)

    def add_dummy_to_front_alternative_constraints_cost_single_addition(self):
        if len(self.alternative_delta_constraints_cost_per_addition)!=0:
            list_size = len(self.alternative_delta_constraints_cost_per_addition)
            what_to_add = self.alternative_delta_constraints_cost_per_addition[list_size-1]
            how_many_time = self.delta_nclo
            list_to_add = [what_to_add]*how_many_time
            self.alternative_delta_constraints_cost_per_addition.extend(list_to_add)

    def add_dummy_to_back_alternative_constraints_cost_single_addition(self,what_to_add,how_many_time):
        if len(self.alternative_delta_constraints_cost_per_addition)==0:
            self.calc_sum_of_solution_cost()
            list_to_add = [what_to_add - self.solution_cost]*how_many_time
            self.alternative_delta_constraints_cost_per_addition.extend(list_to_add)
class AgentX_Query_BroadcastCentral(AgentX_Query):
    def __init__(self,id_,variable,domain,neighbors_agents_id,neighbors_obj_dict,query):
        AgentX_Query.__init__(self,id_,variable,domain,neighbors_agents_id,neighbors_obj_dict,query)
        self.alternative_constraints_min_valid_cost = 0
        self.alternative_constraints_max_measure = 0
        for agent_in_query in self.query.variables_in_query:
            if agent_in_query not in self.neighbors_agents_id and agent_in_query!=self.id_:
                self.neighbors_agents_id.append(agent_in_query)






    def update_solution_constraints(self,msg):
        if msg.msg_type == MsgTypeX.solution_constraints_information:
            sender = msg.sender
            info = msg.information
            self.solution_constraints[sender] = info

    def update_alternative_constraints(self,msg):
        if msg.msg_type == MsgTypeX.alternative_constraints_information:
            sender = msg.sender
            info = msg.information
            self.alternative_constraints[sender] = copy.deepcopy(info)
            self.alternative_constraints_inbox.extend(copy.deepcopy(info))
            temp_list = []
            for const in self.alternative_constraints_inbox:
                if const not in temp_list:
                    temp_list.append(const)
            self.alternative_constraints_inbox = temp_list


    def update_msgs_in_context(self,msgs):
        for msg in msgs:
            self.update_solution_value_request_data(msg)
            self.update_solution_value_infrormation_in_local_view(msg)
            self.update_solution_constraints(msg)
            self.update_alternative_constraints(msg)


    def change_status_after_update_msgs_in_context(self, msgs):
        if AgentXStatues.wait_for_solution_value in self.statues and self.local_view_has_nones()==False and self.query_only_ask_self() == False:
            self.statues.remove(AgentXStatues.wait_for_solution_value)
            self.statues.append(AgentXStatues.request_solution_constraints)
        if AgentXStatues.wait_for_solution_value in self.statues and self.local_view_has_nones() == False \
                and self.query_only_ask_self()  :
            self.statues.remove(AgentXStatues.wait_for_solution_value)
            self.statues.append(AgentXStatues.request_self_solution_and_alternatives)
        if len(self.who_asked_for_solution_value)!=0:
            self.statues.append(AgentXStatues.send_solution_value)
        if AgentXStatues.wait_for_solution_constraints in self.statues and self.solution_constraints_has_none() == False:
            self.statues.remove(AgentXStatues.wait_for_solution_constraints)
            self.statues.append(AgentXStatues.request_alternative_constraints)
        if AgentXStatues.wait_for_alternative_constraints in self.statues:
            self.statues.remove(AgentXStatues.wait_for_alternative_constraints)
            self.statues.append(AgentXStatues.check_if_explanation_is_complete)



    def get_all_alternative_constraints_list(self):
        constraints_alternative_list = []
        for v in self.alternative_constraints.values():
            constraints_alternative_list.extend(v)

        counter = CostComparisonCounter()
        sorted_constraints = sorted(constraints_alternative_list, key=cmp_to_key(counter.comparator))
        sorted_counter = counter.count
        return sorted_constraints,sorted_counter

    def compose_alternative_constraints_for_explanations(self,sorted_constraints,total_cost_solution):
        counter_of_alt_constraint_valid = 0
        counter_of_alt_constraint_all = 0

        for constraint in sorted_constraints:
            if not self.is_done:
                self.alternative_constraints_for_explanations.append(constraint)
                self.alternative_constraints_cost_single_addition.append(self.alternative_cost+constraint.cost)
                self.alternative_delta_constraints_cost_per_addition.append((self.alternative_cost+constraint.cost) - self.solution_cost)
                self.alternative_cost = self.alternative_cost + constraint.cost
            counter_of_alt_constraint_all=  counter_of_alt_constraint_all+1

            if self.alternative_cost>= total_cost_solution and not self.is_done:
                counter_of_alt_constraint_valid = counter_of_alt_constraint_valid + 1

                self.alternative_constraints_min_valid_cost = self.alternative_cost
                self.is_done = True
                #break
        self.is_done = True

        self.alternative_constraints_max_measure = self.alternative_cost
        if not self.is_done:
            self.alternative_constraints_min_valid_cost = self.alternative_cost
        return counter_of_alt_constraint_valid, counter_of_alt_constraint_all

    def compute_request_self_solution_and_alternatives(self):
        if AgentXStatues.request_self_solution_and_alternatives in self.statues:

            ####----------
            total_cost_solution = self.get_self_solution_constraints()
            self.solution_cost = total_cost_solution
            NCLO_self_solution = len(self.solution_constraints[self.id_])  # * because of the sum
            self.get_self_alternative_constraints()
            NCLO_alternative_solution = len(self.alternative_constraints[self.id_])

            ###----------
            sorted_constraints, sorted_counter = self.get_all_alternative_constraints_list()
            ###----------
            counter_of_alt_constraint_valid, counter_of_alt_constraint_all = self.compose_alternative_constraints_for_explanations(
                sorted_constraints, total_cost_solution)
            self.NCLO_for_valid_solution = NCLO_self_solution + NCLO_alternative_solution + sorted_counter + counter_of_alt_constraint_valid
            total_NCLO = NCLO_self_solution + NCLO_alternative_solution + sorted_counter + counter_of_alt_constraint_all

            return total_NCLO
        else:
            return 0

    def compute_request_solution_constraints(self):
        NCLO = 0
        if AgentXStatues.request_solution_constraints in self.statues:
            if self.am_i_in_query():
                total_cost = self.get_self_solution_constraints()
                NCLO += len(self.solution_constraints[self.id_])
            else:
                pass
        return NCLO

    def compute_request_alternative_constraints(self):
        NCLO = 0

        if AgentXStatues.request_alternative_constraints in self.statues:
            NCLO += self.calc_sum_of_solution_cost()
            self.get_self_alternative_constraints()
            self.alternative_constraints_inbox.extend(copy.deepcopy(self.alternative_constraints[self.id_]))
            NCLO +=len(self.alternative_constraints[self.id_])

        return NCLO

        # stop here, need to compute: create local alternative, and then a mechanism that sends requests until get a valid blah blah

    def compute_check_if_explanation_is_complete(self):
        NCLO = 0
        if AgentXStatues.check_if_explanation_is_complete in self.statues:
            counter = CostComparisonCounter()
            self.alternative_constraints_inbox = sorted(self.alternative_constraints_inbox, key=cmp_to_key(counter.comparator))
            NCLO=NCLO+counter.count
            who_you_took_from = list(self.alternative_constraints.keys())


            self.add_dummy_to_front_alternative_constraints_cost_single_addition()
            flag = False
            while len(self.alternative_constraints_inbox)!=0:
                NCLO =NCLO+1
                const = self.alternative_constraints_inbox.pop(0)
                if not self.is_done and const not in self.alternative_constraints_for_explanations:

                    if not flag:
                        flag = True
                        self.add_dummy_to_back_alternative_constraints_cost_single_addition(const.cost,self.local_clock+NCLO)

                    self.alternative_cost += const.cost
                    self.calc_sum_of_solution_cost()
                    self.alternative_constraints_for_explanations.append(const)
                    self.alternative_constraints_cost_single_addition.append(self.alternative_cost)
                    self.alternative_delta_constraints_cost_per_addition.append(self.alternative_cost - self.solution_cost)


                if self.alternative_cost>=self.solution_cost and not self.is_done:
                    self.is_done=True
                    self.alternative_constraints_min_valid_cost = self.alternative_cost
                    self.NCLO_for_valid_solution = self.local_clock+NCLO
            self.alternative_constraints_max_measure = self.alternative_cost
            if self.is_done == False:
                self.alternative_constraints_min_valid_cost = self.alternative_cost
            if self.is_finish_going_for_alternatives(who_you_took_from):
                self.is_done = True
        return NCLO





    def compute(self):
        NCLO = 0
        NCLO += self.compute_request_solution_constraints()
        NCLO += self.compute_request_self_solution_and_alternatives()
        NCLO += self.compute_request_alternative_constraints()
        NCLO += self.compute_check_if_explanation_is_complete()
        if AgentXStatues.check_if_explanation_is_complete in self.statues and self.is_done==False:
            self.statues.append(AgentXStatues.request_alternative_constraints)
            self.statues.remove(AgentXStatues.check_if_explanation_is_complete)
        return NCLO

    def send_msgs(self):
        msgs_to_send = []
        self.send_solution_value_information(msgs_to_send)
        self.send_solution_constraint_request(msgs_to_send)
        self.send_termination_message(msgs_to_send)
        self.send_alternative_constraint_request(msgs_to_send)
        if  len(msgs_to_send)!=0:
            self.outbox.insert(msgs_to_send)



    def change_status_after_send_msgs(self):
        if AgentXStatues.request_solution_constraints in self.statues:
            self.statues.remove(AgentXStatues.request_solution_constraints)
            self.statues.append(AgentXStatues.wait_for_solution_constraints)
        if AgentXStatues.send_solution_value in self.statues:
            self.statues.remove(AgentXStatues.send_solution_value)
        if AgentXStatues.request_alternative_constraints in self.statues:
            self.statues.remove(AgentXStatues.request_alternative_constraints)
            self.statues.append(AgentXStatues.wait_for_alternative_constraints)
    def query_only_ask_self(self):
        first_cond= len(self.query.variables_in_query) == 1
        second_cond = list(self.query.variables_in_query)[0]==self.id_
        return first_cond and second_cond

    def am_i_in_query(self):
        return self.id_ in self.query.variables_in_query

    def send_termination_message(self, msgs_to_send):
        if self.is_done:
            msgs_to_send.append(Msg(sender=self.id_, receiver=None, information=None,msg_type =MsgTypeX.AgentXQTerminate,bandwidth=0,NCLO = self.local_clock))

    def send_solution_constraint_request(self, msgs_to_send):
        if AgentXStatues.request_solution_constraints in self.statues:
            for n_id in self.query.variables_in_query:
                if n_id!=self.id_:
                    msgs_to_send.append(Msg(sender=self.id_, receiver=n_id, information=None,msg_type=MsgTypeX.solution_constraint_request,bandwidth=0,NCLO = self.local_clock))

    def send_alternative_constraint_request(self,msgs_to_send):
        if AgentXStatues.request_alternative_constraints in self.statues:
            n_ids_to_send= self.get_n_ids_to_send()
            for n_id in n_ids_to_send:
                msgs_to_send.append(Msg(sender=self.id_, receiver=n_id, information = self.alternative_partial_assignment, msg_type=MsgTypeX.alternative_constraints_request, bandwidth=len(self.alternative_partial_assignment), NCLO = self.local_clock))

    def get_n_ids_to_send(self):
        ans = list(self.alternative_partial_assignment.keys())
        if self.id_ in ans:
            ans.remove(self.id_)
        return ans

class AgentX_Query_BroadcastCentral_NoSort(AgentX_Query_BroadcastCentral):
    def __init__(self,id_,variable,domain,neighbors_agents_id,neighbors_obj_dict,query):
        AgentX_Query_BroadcastCentral.__init__(self,id_,variable,domain,neighbors_agents_id,neighbors_obj_dict,query)

    def compute_check_if_explanation_is_complete(self):
        NCLO = 0
        if AgentXStatues.check_if_explanation_is_complete in self.statues:

            who_you_took_from = list(self.alternative_constraints.keys())
            self.add_dummy_to_front_alternative_constraints_cost_single_addition()
            flag = False
            while len(self.alternative_constraints_inbox)!=0:
                NCLO =NCLO+1
                rnd_ = random.Random(NCLO + self.id_*17)
                rnd_.shuffle(self.alternative_constraints_inbox)
                const = self.alternative_constraints_inbox.pop(0)

                if not flag:
                    flag = True
                    self.add_dummy_to_back_alternative_constraints_cost_single_addition(const.cost,
                                                                                        self.local_clock + NCLO)

                if self.is_done == False and const not in self.alternative_constraints_for_explanations:
                    self.alternative_cost += const.cost
                    self.calc_sum_of_solution_cost()

                    self.alternative_constraints_for_explanations.append(const)
                    self.alternative_constraints_cost_single_addition.append(self.alternative_cost)
                    self.alternative_delta_constraints_cost_per_addition.append(
                    self.alternative_cost - self.solution_cost)
                if self.alternative_cost>=self.solution_cost and not self.is_done:
                    self.is_done=True
                    self.alternative_constraints_min_valid_cost = self.alternative_cost
                    self.NCLO_for_valid_solution = self.local_clock+NCLO
            self.alternative_constraints_max_measure = self.alternative_cost
            if self.is_done == False:
                self.alternative_constraints_min_valid_cost = self.alternative_cost

            if self.is_finish_going_for_alternatives(who_you_took_from):
                self.is_done = True
        return NCLO

class AgentX_BroadcastCentral(AgentX):
    def __init__(self,id_,variable,domain,neighbors_agents_id,neighbors_obj_dict):
        AgentX.__init__(self,id_,variable,domain,neighbors_agents_id,neighbors_obj_dict)
    def initialize(self):
        pass  # do nothing, wait for solution request

    def update_alternative_partial_assignment(self,msg):
        if msg.msg_type == MsgTypeX.alternative_constraints_request:
            info = msg.information
            self.alternative_partial_assignment = copy.deepcopy(info)

    def update_msgs_in_context(self, msgs):
        for msg in msgs:
            self.update_solution_value_infrormation_in_local_view(msg)
            self.update_solution_value_request_data(msg)
            self.update_alternative_partial_assignment(msg)


    def change_status_after_update_msgs_in_context(self, msgs):
        if len(self.who_asked_for_solution_value)!=0:
            self.statues.append(AgentXStatues.send_solution_value)

            #if AgentXStatues.idle in self.statues:
            #    self.statues.remove(AgentXStatues.idle)

        if msgs[0].msg_type == MsgTypeX.solution_constraint_request:
            self.a_q=msgs[0].sender
            #if AgentXStatues.idle in self.statues:
            #    self.statues.remove(AgentXStatues.idle)
            self.statues.append(AgentXStatues.request_solution_values)

        if msgs[0].msg_type == MsgTypeX.alternative_constraints_request:
            self.a_q=msgs[0].sender
            self.statues.append(AgentXStatues.send_alternative_constraints_to_a_q)
        if AgentXStatues.wait_for_solution_value_then_send_solution_constraints in self.statues and self.local_view_has_nones() == False:
            self.statues.remove(AgentXStatues.wait_for_solution_value_then_send_solution_constraints)
            self.statues.append(AgentXStatues.send_solution_constraints_to_a_q)

    def compute_send_solution_constraints_to_a_q(self):
        if AgentXStatues.send_solution_constraints_to_a_q in self.statues:
            total_cost_solution = self.get_self_solution_constraints()
            return len(self.solution_constraints[self.id_])
        return 0

    def compute(self):
        NCLO = 0
        if AgentXStatues.send_solution_value in self.statues:
            NCLO+= len(self.who_asked_for_solution_value)
        NCLO+=self.compute_send_solution_constraints_to_a_q()
        NCLO+=self.compute_send_alternative_constraints_to_a_q()
        return NCLO

    def send_msgs(self):
        msgs_to_send = []
        self.send_solution_value_information(msgs_to_send)
        self.send_solution_value_request(msgs_to_send)
        self.send_solution_constraints(msgs_to_send)
        self.send_alternative_constraints(msgs_to_send)
        if len(msgs_to_send)!=0:
            self.outbox.insert(msgs_to_send)

    def send_solution_constraints(self,msgs_to_send):
       if AgentXStatues.send_solution_constraints_to_a_q in self.statues:
           bandwidth = len(self.solution_constraints[self.id_])
           msg = Msg( sender=self.id_, receiver=self.a_q, information=self.solution_constraints[self.id_],msg_type = MsgTypeX.solution_constraints_information,bandwidth=bandwidth,NCLO = self.local_clock)
           msgs_to_send.append(msg)

    def change_status_after_send_msgs(self):
        if AgentXStatues.send_solution_value in self.statues:
            self.statues.remove(AgentXStatues.send_solution_value)
            #self.statues.append(AgentXStatues.idle)
        if AgentXStatues.request_solution_values in self.statues:
            self.statues.remove(AgentXStatues.request_solution_values)
            self.statues.append(AgentXStatues.wait_for_solution_value_then_send_solution_constraints)
        if AgentXStatues.send_solution_constraints_to_a_q in self.statues:
            self.statues.remove(AgentXStatues.send_solution_constraints_to_a_q)
        if AgentXStatues.send_alternative_constraints_to_a_q in self.statues:
            self.statues.remove(AgentXStatues.send_alternative_constraints_to_a_q)


    def compute_send_alternative_constraints_to_a_q(self):
        NCLO = 0
        if AgentXStatues.send_alternative_constraints_to_a_q in self.statues:
            self.get_self_alternative_constraints()
            NCLO = len(self.alternative_constraints[self.id_])

        return NCLO

    def send_alternative_constraints(self, msgs_to_send):
        if AgentXStatues.send_alternative_constraints_to_a_q in self.statues:
            msg = Msg(sender= self.id_, receiver=self.a_q, information=self.alternative_constraints[self.id_],
            msg_type= MsgTypeX.alternative_constraints_information,bandwidth=len(self.alternative_constraints[self.id_]),NCLO = self.local_clock)
            msgs_to_send.append(msg)


class AgentX_Query_BroadcastDistributed(AgentX_Query_BroadcastCentral):
    def __init__(self,id_,variable,domain,neighbors_agents_id,neighbors_obj_dict,query):
        AgentX_Query_BroadcastCentral.__init__(self,id_,variable,domain,neighbors_agents_id,neighbors_obj_dict,query)
        self.solution_total_cost_per_q_n = {}


    def update_solution_constraints(self, msg):
        if msg.msg_type == MsgTypeX.solution_constraints_information:
            sender = msg.sender
            info = msg.information
            self.solution_constraints[sender] = info[0]
            self.solution_total_cost_per_q_n[sender] = info[1]



    def compute_request_alternative_constraints(self):
        NCLO = 0

        if AgentXStatues.request_alternative_constraints in self.statues:
            NCLO += self.calc_sum_of_solution_cost()
            self.get_self_alternative_constraints()
            counter = CostComparisonCounter()
            self.alternative_constraints[self.id_] = sorted(self.alternative_constraints[self.id_], key=cmp_to_key(counter.comparator))
            NCLO += counter.count
            #self.alternative_constraints_dict_inbox[self.id_] = copy.deepcopy(sorted_constraints)
            #self.alternative_constraints_inbox.extend(copy.deepcopy(self.alternative_constraints[self.id_]))
            NCLO += len(self.alternative_constraints[self.id_])
            return NCLO
        return 0

    def calc_sum_of_solution_cost(self):
        NCLO = 0

        solution_total_cost = 0
        for constraint in self.solution_constraints[self.id_]:
            NCLO+=1
            solution_total_cost += constraint.cost

        for id_, solution_cost_local in self.solution_total_cost_per_q_n.items():
            NCLO += 1
            solution_total_cost+=solution_cost_local



        const_set = []
        const_list=[]
        for id_,const_list_of_id in self.solution_constraints.items():
            for const in const_list_of_id:
                const_list.append(const)
                if const not in const_set:
                    const_set.append(const)
        cost_of_diff = 0
        for const in const_set:
            cost_of_diff+=const.cost

        cost_of_same = solution_total_cost-cost_of_diff
        self.solution_cost=solution_total_cost-cost_of_same
        NCLO = NCLO - (len(const_list)-len(const_set))


        return NCLO

    def extract_max_constraint(self):

        constraints_to_check = []
        for constraints_list in self.alternative_constraints.values():
            constraints_to_check.append(constraints_list[0])

        max_constraint = max(constraints_to_check,key= lambda x:x.cost)
        for id_, constraints_list in self.alternative_constraints.items():
            if max_constraint in constraints_list:
                constraints_list.remove(max_constraint)

        ids_to_remove = []
        for id_, constraints_list in self.alternative_constraints.items():
            if len(constraints_list)==0:
                ids_to_remove.append(id_)
        for id_ in ids_to_remove:
            del self.alternative_constraints[id_]

        return max_constraint

    def compute_check_if_explanation_is_complete(self):
        NCLO = 0

        if AgentXStatues.check_if_explanation_is_complete in self.statues:
            who_you_took_from = list(self.alternative_constraints.keys())
            self.add_dummy_to_front_alternative_constraints_cost_single_addition()
            flag = False
            while len(self.alternative_constraints) > 0:
                NCLO = NCLO + len(self.alternative_constraints)
                constraints_max = self.extract_max_constraint()
                if not self.is_done and constraints_max not in self.alternative_constraints_for_explanations:
                    self.alternative_cost += constraints_max.cost
                    if not flag:
                        flag = True
                        self.add_dummy_to_back_alternative_constraints_cost_single_addition(constraints_max.cost,
                                                                                            self.local_clock + NCLO)
                    self.calc_sum_of_solution_cost()

                    self.alternative_constraints_for_explanations.append(constraints_max)
                    self.alternative_constraints_cost_single_addition.append(self.alternative_cost)
                    self.alternative_delta_constraints_cost_per_addition.append(
                    self.alternative_cost - self.solution_cost)
                if self.alternative_cost >= self.solution_cost and not self.is_done:
                    self.is_done = True
                    self.alternative_constraints_min_valid_cost = self.alternative_cost
                    self.NCLO_for_valid_solution = self.local_clock+NCLO

            self.alternative_constraints_max_measure = self.alternative_cost
            if self.is_done ==False:
                self.alternative_constraints_min_valid_cost = self.alternative_cost
            if self.is_finish_going_for_alternatives(who_you_took_from):
                self.is_done = True

        return NCLO

class MaxHeap:
    def __init__(self, key=lambda x: x):
        self.data = []
        self.key = key

    def is_empty(self):
        return len(self.data) == 0

    def insert(self, value):

        comparisons = 0
        self.data.append(value)
        comparisons += self._sift_up(len(self.data) - 1)
        return comparisons

    def extract_max(self):
        if len(self.data) == 0:
            raise IndexError("Extracting from an empty heap")
        comparisons = 0
        self._swap(0, len(self.data) - 1)
        max_value = self.data.pop()
        comparisons += self._sift_down(0)
        return max_value, comparisons

    def _sift_up(self, index):
        comparisons = 0
        parent = (index - 1) // 2
        while index > 0 and self.key(self.data[index]) > self.key(self.data[parent]):
            comparisons += 1
            self._swap(index, parent)
            index = parent
            parent = (index - 1) // 2
        if index > 0:
            comparisons += 1
        return comparisons

    def _sift_down(self, index):
        comparisons = 0
        size = len(self.data)
        while index < size:
            left = 2 * index + 1
            right = 2 * index + 2
            largest = index

            if left < size:
                comparisons += 1
                if self.key(self.data[left]) > self.key(self.data[largest]):
                    largest = left

            if right < size:
                comparisons += 1
                if self.key(self.data[right]) > self.key(self.data[largest]):
                    largest = right

            if largest != index:
                self._swap(index, largest)
                index = largest
            else:
                break
        return comparisons

    def _swap(self, i, j):
        self.data[i], self.data[j] = self.data[j], self.data[i]


class AgentX_Query_BroadcastDistributedV2(AgentX_Query_BroadcastDistributed):
    def __init__(self,id_,variable,domain,neighbors_agents_id,neighbors_obj_dict,query):
        AgentX_Query_BroadcastDistributed.__init__(self,id_,variable,domain,neighbors_agents_id,neighbors_obj_dict,query)


    def get_queue_of_constraints(self):
        queue_of_constraints = []
        NCLO = 0

        while len(self.alternative_constraints) != 0:

            keys_list = list(self.alternative_constraints.keys())
            for i in keys_list:
                #selected_var = self.alternative_constraints[i]
                constraint = self.alternative_constraints[i].pop(0)
                if constraint not in queue_of_constraints:
                    queue_of_constraints.append(constraint)
                    NCLO = NCLO + 1

            vars_to_delete = []
            for var_name, list_of_constraints in self.alternative_constraints.items():
                if len(list_of_constraints) == 0:
                    vars_to_delete.append(var_name)
            for var_name in vars_to_delete:
                del self.alternative_constraints[var_name]
        return queue_of_constraints,NCLO

    def create_max_heap(self):
        NCLO = 0
        mh = MaxHeap(key=lambda x: x.cost)
        for k, v in self.alternative_constraints.items():
            if len(v)!=0:
                constraint = v.pop(0)
                constraint.who_created = k
                if constraint not in self.alternative_constraints_for_explanations:
                    NCLO = NCLO + mh.insert(constraint)
        return NCLO,mh

    def compute_check_if_explanation_is_complete(self):

        NCLO = 0
        if AgentXStatues.check_if_explanation_is_complete in self.statues:
            who_you_took_from = list(self.alternative_constraints.keys())

            NCLO,max_heap = self.create_max_heap()

            self.add_dummy_to_front_alternative_constraints_cost_single_addition()
            flag = False

            while not max_heap.is_empty() :
                const,max_heap_NCLO = max_heap.extract_max()
                if not flag:
                    flag = True
                    self.add_dummy_to_back_alternative_constraints_cost_single_addition(const.cost,
                                                                                        self.local_clock + NCLO)
                if not self.is_done and const not in self.alternative_constraints_for_explanations:
                    NCLO = NCLO+max_heap_NCLO
                    self.alternative_cost += const.cost
                    self.calc_sum_of_solution_cost()

                    self.alternative_constraints_for_explanations.append(const)
                    self.alternative_constraints_cost_single_addition.append(self.alternative_cost)
                    self.alternative_delta_constraints_cost_per_addition.append(
                        self.alternative_cost - self.solution_cost)

                who_created = const.who_created
                if len(self.alternative_constraints[who_created]) == 0:
                    del self.alternative_constraints[who_created]
                else:
                    constraint_to_add_heap = self.alternative_constraints[who_created].pop(0)
                    constraint_to_add_heap.who_created = who_created
                    NCLO = NCLO + max_heap.insert(constraint_to_add_heap)

                if self.alternative_cost >= self.solution_cost and not self.is_done:
                    self.is_done = True
                    self.alternative_constraints_min_valid_cost = self.alternative_cost
                    self.NCLO_for_valid_solution = self.local_clock + NCLO



            self.alternative_constraints_max_measure = self.alternative_cost
            if self.is_done == False:
                self.alternative_constraints_min_valid_cost = self.alternative_cost
            if self.is_finish_going_for_alternatives(who_you_took_from):
                self.is_done = True

        return NCLO




class AgentX_Query_BroadcastDistributedV3(AgentX_Query_BroadcastDistributedV2):
    def __init__(self, id_, variable, domain, neighbors_agents_id, neighbors_obj_dict, query):
        AgentX_Query_BroadcastDistributedV2.__init__(self, id_, variable, domain, neighbors_agents_id, neighbors_obj_dict,
                                                   query)

    def compute_check_if_explanation_is_complete(self):


        NCLO = 0
        if AgentXStatues.check_if_explanation_is_complete in self.statues:
            who_you_took_from = list(self.alternative_constraints.keys())




            queue_of_constraints,NCLO = self.get_queue_of_constraints()
            self.add_dummy_to_front_alternative_constraints_cost_single_addition()

            flag=False
            while len(queue_of_constraints) != 0:
                NCLO = NCLO + 1
                const = queue_of_constraints.pop(0)
                if not flag:
                    flag = True
                    self.add_dummy_to_back_alternative_constraints_cost_single_addition(const.cost,
                                                                                        self.local_clock + NCLO)
                if not self.is_done and const not in self.alternative_constraints_for_explanations:
                    self.alternative_cost += const.cost
                    self.calc_sum_of_solution_cost()

                    self.alternative_constraints_for_explanations.append(const)
                    self.alternative_constraints_cost_single_addition.append(self.alternative_cost)
                    self.alternative_delta_constraints_cost_per_addition.append(self.alternative_cost - self.solution_cost)
                if self.alternative_cost >= self.solution_cost and not self.is_done:
                    self.is_done = True
                    self.alternative_constraints_min_valid_cost = self.alternative_cost
                    self.NCLO_for_valid_solution = self.local_clock + NCLO
            self.alternative_constraints_max_measure = self.alternative_cost
            if self.is_done == False:
                self.alternative_constraints_min_valid_cost = self.alternative_cost
            if self.is_finish_going_for_alternatives(who_you_took_from):
                self.is_done = True


        return NCLO

class AgentX_BroadcastDistributed(AgentX_BroadcastCentral ):
    def __init__(self,id_,variable,domain,neighbors_agents_id,neighbors_obj_dict):
        AgentX_BroadcastCentral.__init__(self,id_,variable,domain,neighbors_agents_id,neighbors_obj_dict)
        self.total_local_cost_solution = 0

    def compute_send_solution_constraints_to_a_q(self):
        if AgentXStatues.send_solution_constraints_to_a_q in self.statues:
            self.total_local_cost_solution = self.get_self_solution_constraints()
            return len(self.solution_constraints[self.id_])
        return 0
    def send_solution_constraints(self,msgs_to_send):
        if AgentXStatues.send_solution_constraints_to_a_q in self.statues:
            bandwidth = len(self.solution_constraints[self.id_])
            msg = Msg(sender=self.id_, receiver=self.a_q, information=(self.solution_constraints[self.id_],self.total_local_cost_solution),
                      msg_type=MsgTypeX.solution_constraints_information, bandwidth=bandwidth+1, NCLO=self.local_clock)
            msgs_to_send.append(msg)



    def compute_send_alternative_constraints_to_a_q(self):
        NCLO = 0
        if AgentXStatues.send_alternative_constraints_to_a_q in self.statues:
            self.get_self_alternative_constraints()
            counter = CostComparisonCounter()
            self.alternative_constraints[self.id_] = sorted(self.alternative_constraints[self.id_],
                                                            key=cmp_to_key(counter.comparator))
            NCLO += counter.count
        return NCLO
from abc import ABC, abstractmethod


class AgentX_Query_BroadcastDistributed_communication_heurtsic(AgentX_Query_BroadcastDistributedV3,ABC):
    def __init__(self, id_, variable, domain, neighbors_agents_id, neighbors_obj_dict, query):
        AgentX_Query_BroadcastDistributedV3.__init__(self, id_, variable, domain, neighbors_agents_id, neighbors_obj_dict,
                                                     query)
        self.mean_constraints = self.calc_mean_constraints_of_agents_in_query()
        self.max_constraints = self.calc_max_constraints_of_agents_in_query()
        self.degree_of_query_agents_dict = self.get_degree_of_query_agents_dict()
        self.query_agents_to_send_alternative_request =sorted(self.degree_of_query_agents_dict, key=lambda k: self.degree_of_query_agents_dict[k], reverse=True)
        self.query_agents_to_send_alternative_request.remove(self.id_)



    def compute_request_alternative_constraints(self):
        NCLO = 0

        if AgentXStatues.request_alternative_constraints in self.statues:
            NCLO += self.calc_sum_of_solution_cost()
            self.get_self_alternative_constraints()
            counter = CostComparisonCounter()
            self.alternative_constraints[self.id_] = sorted(self.alternative_constraints[self.id_], key=cmp_to_key(counter.comparator))
            NCLO += counter.count
            #self.alternative_constraints_dict_inbox[self.id_] = copy.deepcopy(sorted_constraints)
            #self.alternative_constraints_inbox.extend(copy.deepcopy(self.alternative_constraints[self.id_]))
            NCLO += len(self.alternative_constraints[self.id_])

            self.statues.append(AgentXStatues.check_if_explanation_is_complete)

            self.compute_check_if_explanation_is_complete()

            if self.is_done:
                self.statues.remove(AgentXStatues.request_alternative_constraints)

            if not self.is_done:
                self.statues.remove(AgentXStatues.check_if_explanation_is_complete)


            return NCLO
        return 0

    def get_list_of_all_costs_agents_in_query(self):
        ans=[]
        agents_in_query = self.query.variables_in_query.values()
        for a in agents_in_query:
            constraints = []
            for n in a.neighbors_obj:
                constraints.append(n.cost_table)
            for val_assignment_cost_dict in constraints:
                for val_assignment,cost in val_assignment_cost_dict.items():
                    if cost != my_inf:
                        ans.append(cost)
            return ans
    def calc_mean_constraints_of_agents_in_query(self):
        all_costs_agents_in_query = self.get_list_of_all_costs_agents_in_query()
        ans = sum(all_costs_agents_in_query)/len(all_costs_agents_in_query)
        return ans

    def calc_max_constraints_of_agents_in_query(self):
        all_costs_agents_in_query = self.get_list_of_all_costs_agents_in_query()
        ans = max(all_costs_agents_in_query)
        return ans
    def get_degree_of_query_agents_dict(self):
        ans = {}
        agents_in_query = self.query.variables_in_query.values()
        for agent in agents_in_query:
            k = agent.id_
            v = len(agent.neighbors_agents_id)
            ans[k] = v
        return ans

    def is_finish_going_for_alternatives(self,who_you_took_from):
        if self.is_done:
            return True
        n_ids_to_send = self.get_n_ids_to_send()
        ttt = copy.deepcopy(self.query_agents_to_send_alternative_request)
        for a_id in who_you_took_from:
            if a_id in ttt:
                ttt.remove(a_id)
        if len(ttt)==0:
            return True
        return False


    def get_amount_of_constraints_potential_cost_in_ans(self,ans):
        total_amount = 0
        for id_ in ans:
            amount_of_constraints = self.degree_of_query_agents_dict[id_]
            heuristic_estimation_of_single_constraint_cost  = self.get_heuristic_estimation_of_cost()
            total_amount = total_amount+heuristic_estimation_of_single_constraint_cost*amount_of_constraints
        return total_amount




    def get_n_ids_to_send(self):
        if len(self.query_agents_to_send_alternative_request)==1:
            return [self.query_agents_to_send_alternative_request[0]]


        ans = []
        for a_id in self.query_agents_to_send_alternative_request:
            amount_of_constraint = self.degree_of_query_agents_dict[a_id]
            heuristic_estimation_of_single_constraint_cost  = self.get_heuristic_estimation_of_cost()
            amount_of_potential_costs_in_ans = self.get_amount_of_constraints_potential_cost_in_ans(ans)
            cost_missing = self.solution_cost-(self.alternative_cost+amount_of_potential_costs_in_ans)
            ans.append(a_id)
            iteration_contribution = amount_of_constraint*heuristic_estimation_of_single_constraint_cost
            if cost_missing < iteration_contribution:
                return ans
        return ans
    @abstractmethod
    def get_heuristic_estimation_of_cost(self):pass

    def send_alternative_constraint_request(self,msgs_to_send):
        if AgentXStatues.request_alternative_constraints in self.statues:

            n_ids_to_send = self.get_n_ids_to_send()
            for n_id in n_ids_to_send:
                msgs_to_send.append(
                    Msg(sender=self.id_, receiver=n_id, information=self.alternative_partial_assignment,
                        msg_type=MsgTypeX.alternative_constraints_request,
                        bandwidth=len(self.alternative_partial_assignment), NCLO=self.local_clock))

            for a_id in n_ids_to_send:
                self.query_agents_to_send_alternative_request.remove(a_id)




class AgentX_Query_BroadcastDistributed_communication_heurtsic_max(AgentX_Query_BroadcastDistributed_communication_heurtsic):
    def __init__(self, id_, variable, domain, neighbors_agents_id, neighbors_obj_dict, query):
        AgentX_Query_BroadcastDistributed_communication_heurtsic.__init__(self, id_, variable, domain, neighbors_agents_id, neighbors_obj_dict,
                                               query)

    def get_heuristic_estimation_of_cost(self):
        return self.max_constraints
class AgentX_Query_BroadcastDistributed_communication_heurtsic_mean(AgentX_Query_BroadcastDistributed_communication_heurtsic):
    def __init__(self, id_, variable, domain, neighbors_agents_id, neighbors_obj_dict, query):
        AgentX_Query_BroadcastDistributed_communication_heurtsic.__init__(self, id_, variable, domain, neighbors_agents_id, neighbors_obj_dict,
                                               query)

    def get_heuristic_estimation_of_cost(self):
        return self.mean_constraints

