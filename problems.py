import random
import threading
from operator import truediv
from itertools import combinations

from Algorithm_BnB import BranchAndBound
from Agents import *
from Algorithm_BnB_Central import Bnb_central
from Globals_ import *

from enums import *
from abc import ABC, abstractmethod
from collections import defaultdict



class Neighbors():
    def __init__(self, a1:Agent, a2:Agent, cost_generator,dcop_id):

        if a1.id_<a2.id_:
            self.a1 = a1
            self.a2 = a2
        else:
            self.a1 = a2
            self.a2 = a1

        self.dcop_id = dcop_id
        self.rnd_cost = random.Random((((dcop_id+1)+100)+((a1.id_+1)*1710)+((a2.id_*281)*13))*17)
        for _ in range(5):
            self.rnd_cost.random()
        self.cost_table = {}
        self.create_dictionary_of_costs(cost_generator)

    def __str__(self):
        return self.a1.__str__()+":"+self.a2.__str__()


    def is_ids_this_object(self,id_1,id_2):
        if (self.a1.id_==id_1 and self.a2.id_ == id_2) or (self.a1.id_==id_2 and self.a2.id_ == id_1):
            return True
        else:
            return False

    def get_cost(self, first_agent_id_input, first_agent_variable, second_agent_id_input, second_agent_variable):
        if isinstance(first_agent_id_input,int):
            return self.get_cost_given_id_int(first_agent_id_input, first_agent_variable, second_agent_id_input, second_agent_variable)
        if first_agent_id_input<second_agent_id_input:
            ap =(first_agent_id_input,first_agent_variable,second_agent_id_input,second_agent_variable)
        else:
            ap =(second_agent_id_input, second_agent_variable, first_agent_id_input,first_agent_variable)
        ans = self.cost_table[ap]
        return ans

    def get_cost_given_id_int(self, first_agent_id_input, first_agent_variable, second_agent_id_input, second_agent_variable):

        if first_agent_id_input < second_agent_id_input:
            ap = (("A_"+str(first_agent_id_input), first_agent_variable), ("A_"+str(second_agent_id_input), second_agent_variable))
        else:
            ap = (("A_"+str(second_agent_id_input), second_agent_variable), ("A_"+str(first_agent_id_input), first_agent_variable))
        ans = self.cost_table[ap]
        return ans

    def get_ap_and_cost(self, first_agent_id_input, first_agent_variable, second_agent_id_input, second_agent_variable):

        if first_agent_id_input < second_agent_id_input:
            ap = (("A_"+str(first_agent_id_input), first_agent_variable), ("A_"+str(second_agent_id_input), second_agent_variable))
        else:
            ap = (("A_"+str(second_agent_id_input), second_agent_variable), ("A_"+str(first_agent_id_input), first_agent_variable))
        cost = self.cost_table[ap]
        return ap,cost
    def create_dictionary_of_costs(self,cost_generator):
        for d_a1 in self.a1.domain:
            for d_a2 in self.a2.domain:
                first_tuple = ("A_"+str(self.a1.id_),d_a1)
                second_tuple = ("A_"+str(self.a2.id_),d_a2)
                ap = (first_tuple,second_tuple)
                cost = cost_generator(self.rnd_cost,self.a1,self.a2,d_a1,d_a2)
                self.cost_table[ap] = cost



    def get_constraint(self,first_tuple,second_tuple):
        if first_tuple[0]<second_tuple[0]:
            k = (("A_"+str(first_tuple[0]),first_tuple[1]),("A_"+str(second_tuple[0]),second_tuple[1]))
        else:
            k = (("A_"+str(second_tuple[0]),second_tuple[1]),("A_"+str(first_tuple[0]),first_tuple[1]))
        return k,self.cost_table[k]


    def is_agent_in_obj(self,agent_id_input):
        if agent_id_input == self.a1.id_  or agent_id_input == self.a2.id_ :
            return True
        return False



    def get_other_agent(self,agent_input):
        if agent_input.id_ == self.a1.id_:
            return self.a2.id_
        else:
            return self.a1.id_

class UnboundedBuffer():

    def __init__(self):
        self.buffer = []

    def insert(self, list_of_msgs):
        for msg in list_of_msgs:
            self.buffer.append(msg)

    def extract(self):

        ans = []
        for msg in self.buffer:
            if msg is None:
                return None
            else:
                ans.append(msg)
        self.buffer = []
        return ans

    def is_buffer_empty(self):

        return len(self.buffer) == 0

class Mailer():
    def __init__(self,agents):
        self.inbox = UnboundedBuffer()
        self.agents_outbox = {}
        for a in agents:
            outbox = UnboundedBuffer()
            self.agents_outbox[a.id_] = outbox
            a.inbox = outbox
            a.outbox = self.inbox

    def place_messages_in_agents_inbox(self):
        msgs_to_send = self.inbox.extract()
        if len(msgs_to_send) == 0: return True
        msgs_by_receiver_dict = self.create_msgs_by_receiver_dict(msgs_to_send)
        for receiver,msgs_list in msgs_by_receiver_dict.items():
            self.agents_outbox[receiver].insert(msgs_list)

    def create_msgs_by_receiver_dict(self,msgs_to_send):
        msgs_by_receiver_dict = {}
        for msg in msgs_to_send:
            receiver = msg.receiver
            if receiver not in msgs_by_receiver_dict.keys():
                msgs_by_receiver_dict[receiver] = []
            msgs_by_receiver_dict[receiver].append(msg)
        return msgs_by_receiver_dict

class DCOP(ABC):
    def __init__(self,id_,A,D,dcop_name,algorithm):
        self.dcop_id = id_
        self.A = A
        self.D = D
        self.algorithm = algorithm

        self.dcop_name = dcop_name
        self.agents = []
        self.create_agents()
        self.neighbors = []
        self.rnd_neighbors = random.Random((id_+5)*17)
        self.rnd_cost= random.Random((id_+7)*177)
        self.create_neighbors()
        self.connect_agents_to_neighbors()
        self.mailer = Mailer(self.agents)
        self.global_clock = 0
        self.inform_root()
        self.agents_dict = {}
        self.complete_assignment = {}
        for a in self.agents: self.agents_dict[a.id_] = a


    def create_agents(self):
        for i in range(self.A):
            self.create_agent(i)


    def get_random_agents(self, rnd, without, amount_of_variables):
        # Filter out the agent specified in 'without'
        filtered_agents = [agent for agent in self.agents if agent != without]
        # Ensure the filtered list is large enough
        if len(filtered_agents) < amount_of_variables:
            raise ValueError("Not enough agents available to select the requested number.")

        # Use the provided random generator to select a sublist
        return rnd.sample(filtered_agents, amount_of_variables)


    def create_agent_dict(self):
        self.agents_dict = {}
        for agent in self.agents:
            self.agents_dict[agent.id_]=agent


    def get_complete_assignment(self):
        self.complete_assignment = {}
        for agent in self.agents:
            self.complete_assignment[agent.id_] = agent.variable
        return self.complete_assignment





    def most_dense_agent(self):
        sorted_agents = sorted(self.agents, key=lambda x: (-len(x.neighbors_obj), x.id_))
        return sorted_agents[0]


    def connect_agents_to_neighbors(self):
        for a in self.agents:
            neighbors_of_a = self.get_all_neighbors_obj_of_agent(a)
            a.set_neighbors(neighbors_of_a)


    def get_all_neighbors_obj_of_agent(self, agent:Agent):
        ans = []
        for n in self.neighbors:
            if n.is_agent_in_obj(agent.id_):
                ans.append(n)
        return ans



    def execute_center(self):
        if central_bnb_problem_details_debug:
            for a in self.agents:
                print("variable:",a,"domain:",a.domain)
            for n in self.neighbors:
                print(n.cost_table)
        bnb = Bnb_central(self.agents)
        UB = bnb.UB
        for agent in self.agents:
            agent.variable = UB[0][agent.id_]
            for n_id in agent.neighbors_agents_id:
                agent.neighbors_values[n_id] = UB[0][n_id]



    def execute_distributed(self):
        self.draw_global_things()

        self.global_clock = 0
        self.agents_init()
        while not self.all_agents_complete():
            self.global_clock = self.global_clock + 1
            is_empty = self.mailer.place_messages_in_agents_inbox()
            if is_empty:
                print("DCOP:",str(self.dcop_id),"global clock:",str(self.global_clock), "is over because there are no messages in system ")
                break
            self.agents_perform_iteration(self.global_clock)
            #self.draw_global_things()
        #self.collect_records()

    def __str__(self):
        return self.dcop_name+",id_"+str(self.dcop_id)+",A_"+str(self.A)+",D_"+str(self.D)



    def agents_init(self):
        for a in self.agents:
            a.initialize()

    @abstractmethod
    def create_neighbors(self):
        pass


    def all_agents_complete(self):
        for a in self.agents:
            if not a.is_algorithm_complete():
                return False
        return True

    def inform_root(self):
        if self.algorithm == Algorithm.branch_and_bound:
            root_agent = self.most_dense_agent()
            for a in self.agents:
                if root_agent.id_ ==a.id_:
                    root_agent.dfs_tree_token = []
                    root_agent.dfs_height_dict = {}
                else:
                    a.dfs_tree_token = None

    def agents_perform_iteration(self,global_clock):
        for a in self.agents:
            a.execute_iteration(global_clock)



    def collect_records(self):
        ans = {}
        for a in self.agents:
            records_list = a.records
            dict_1 = {"dcop_id":self.dcop_id,"problem":self.__str__()} #self.add_more_records()
            for record in records_list:
                dict_2 = record.get_explanation_as_dict()
                dict_2.update(dict_1)
                for k,v in dict_2.items():
                    if k not in ans:
                        ans[k]=[]
                    ans[k].append(v)
        return ans

    def create_agent(self,i):
        if self.algorithm == Algorithm.branch_and_bound:
            self.agents.append(BranchAndBound(i + 1, self.D))


class DCOP_RandomUniform(DCOP):
    def __init__(self, id_,A,D,dcop_name,algorithm,p1):
        self.p1 = p1
        DCOP.__init__(self,id_,A,D,dcop_name,algorithm)

    def create_neighbors(self):
        for i in range(self.A):
            a1 = self.agents[i]
            for j in range(i+1,self.A):
                a2 = self.agents[j]
                rnd_number = self.rnd_neighbors.random()
                if rnd_number<self.p1:
                    self.neighbors.append(Neighbors(a1, a2, sparse_random_uniform_cost_function, self.dcop_id))

class DCOP_GraphColoring(DCOP):

    def __init__(self, id_,A,D,dcop_name,algorithm):
        DCOP.__init__(self,id_,A,D,dcop_name,algorithm)

    def create_neighbors(self):
        for i in range(self.A):
            a1 = self.agents[i]
            for j in range(i+1,self.A):
                a2 = self.agents[j]
                rnd_number = self.rnd_neighbors.random()
                if rnd_number<graph_coloring_p1:
                    self.neighbors.append(Neighbors(a1, a2, graph_coloring_cost_function, self.dcop_id))





class DCOP_MeetingSchedualing(DCOP):
    def __init__(self,id_, A, meetings,meetings_per_agent,time_slots_D, dcop_name, algorithm):
        DCOP.__init__(self, id_, A*meetings_per_agent, time_slots_D, dcop_name, algorithm)

        if A*meetings_per_agent<meetings*2  :
            raise ValueError("A*meetings_per_agent<meetings*2")
        if meetings_per_agent>meetings:
            raise ValueError("meetings_per_agent>meetings")

        self.rnd_agents_per_meet = random.Random((id_ + 782) * 17)
        self.rnd_meeting_per_agent = random.Random((id_+412)*17)

        for a in self.agents:
            a.create_unary_costs(self.dcop_id)


        for _ in range(5):
            self.rnd_meeting_per_agent.random()
            self.rnd_agents_per_meet.random()

        #----------
        self.meetings_per_agent_dict = self.divide_agents_to_groups(meetings_per_agent)


        #----------
        self.agents_assigned_to_meetings_dict = self.get_agents_assigned_to_meetings_dict(meetings)

        self.agent_id_meetings_ids_dict = self.get_agent_id_meetings_ids_dict()
        self.check_problem_correctness()
        self.create_neighbors2()
        #sparse_random_uniform_cost_function()
    def create_neighbors(self):
        pass

    def create_neighbors2(self):

        self.create_inequality_neighbors()
        self.create_equality_neighbors()
        #self.create_unary_constraint()


        #meeting_scheduling_must_be_non_equal_cost_function(rnd_cost: Random, a1, a2, d_a1, d_a2)

        #meeting_scheduling_must_be_equal_cost_function(rnd_cost: Random, a1, a2, d_a1, d_a2)
    def check_problem_correctness(self):
        for agent_id,meetings_ids in self.agent_id_meetings_ids_dict.items():
            if len(meetings_ids) != len(set(meetings_ids)):
                raise Exception("Allocation of tasks is incorrect:"+str(meetings_ids))

    def get_agent_id_meetings_ids_dict(self):
        ans = {}
        for agent_id,meetings_agents in self.meetings_per_agent_dict.items():
            ans[agent_id] = []
            for meeting_agent in meetings_agents:
                meeting_id = self.get_id_of_meeting(meeting_agent)
                ans[agent_id].append(meeting_id)
        return ans

    def get_agents_assigned_to_meetings_dict(self,meetings):
        """
        Allocate each variable in a group to a different meeting.

        Returns:
            dict: A dictionary with keys as meeting indices (running integers) and values as lists of agents.
        """

        meetings_per_agent_dict_copy = {}
        for i, agents in self.meetings_per_agent_dict.items():
            meetings_per_agent_dict_copy[i] = agents[:]

        agents_in_meeting_dict = {}  # Dictionary to store the result
        for meet_id in range(meetings):agents_in_meeting_dict[meet_id] = []
        self.allocate_min_amount_per_meet(2,meetings_per_agent_dict_copy,agents_in_meeting_dict)
        self.allocate_the_rest_of_meetings(meetings_per_agent_dict_copy,agents_in_meeting_dict)
        return agents_in_meeting_dict




    def divide_agents_to_groups(self, k):
        # Shuffle the agents list
        shuffled_agents = self.agents[:]
        self.rnd_meeting_per_agent.shuffle(shuffled_agents)

        # Divide the shuffled list into groups of size k
        groups = [shuffled_agents[i:i + k] for i in range(0, len(shuffled_agents), k)]

        agents_dict = {}  # Dictionary to store the result
        agents_index = 0  # Running integer for meeting indices
        for group in groups:
            agents_dict[agents_index] = group
            agents_index+=1
        return agents_dict







    def allocate_min_amount_per_meet(self,min_amount_per_meet,meetings_per_agent_dict_copy,agents_in_meeting_dict):
        indexes_to_delete = []
        for index_meeting, meetings_of_agents in meetings_per_agent_dict_copy.items():
            meeting_indexes=[]
            while len(meetings_of_agents)>0:
                if self.there_is_min_amount_per_meet(min_amount_per_meet,agents_in_meeting_dict):
                    break
                meeting = meetings_of_agents.pop(0)
                if len(meetings_of_agents) == 0:
                    indexes_to_delete.append(index_meeting)

                # Find the list with the minimum size in agents_in_meeting_dict
                min_size = min(len(v) for v in agents_in_meeting_dict.values())
                min_keys = [k for k, v in agents_in_meeting_dict.items() if len(v) == min_size]

                # Randomly allocate the agent to one of the smallest lists
                while True:
                    chosen_meeting = self.rnd_agents_per_meet.choice(min_keys)
                    if chosen_meeting not in meeting_indexes:
                        meeting_indexes.append(chosen_meeting)
                        break
                agents_in_meeting_dict[chosen_meeting].append(meeting)
        for index_to_delete in indexes_to_delete:
            del meetings_per_agent_dict_copy[index_to_delete]

    def there_is_min_amount_per_meet(self, min_amount_per_meet, agents_in_meeting_dict):
        for agents in agents_in_meeting_dict.values():
            if len(agents) < min_amount_per_meet:
                return False
        return True

    def allocate_the_rest_of_meetings(self, meetings_per_agent_dict_copy,agents_in_meeting_dict):
        for agent_index,meeting_agents in meetings_per_agent_dict_copy.items():
            amount_to_allocate= len(meeting_agents)
            random_indexes = self.rnd_meeting_per_agent.sample(list(agents_in_meeting_dict.keys()), amount_to_allocate)
            for i in range (amount_to_allocate):
                agents_in_meeting_dict[random_indexes[i]].append(meeting_agents[i])

    def get_id_of_meeting(self, meeting_agent_input):
        for meeting_id,meeting_agents in self.agents_assigned_to_meetings_dict.items():
            for meeting_agent in meeting_agents:
                if meeting_agent.id_ == meeting_agent_input.id_:
                    return meeting_id

    def create_inequality_neighbors(self):
        for meeting_id,meeting_agents in self.meetings_per_agent_dict.items():
            all_pairs = list(combinations(meeting_agents, 2))
            for pair in all_pairs:
                a1,a2 = [pair[0], pair[1]]
                self.neighbors.append(Neighbors(a1, a2, meeting_scheduling_must_be_non_equal_cost_function, self.dcop_id))


    def create_equality_neighbors(self):
        for meeting_id, meeting_agents in self.agents_assigned_to_meetings_dict.items():
            all_pairs = list(combinations(meeting_agents, 2))
            for pair in all_pairs:
                a1, a2 = [pair[0], pair[1]]
                self.neighbors.append(
                    Neighbors(a1, a2, meeting_scheduling_must_be_equal_cost_function, self.dcop_id))




