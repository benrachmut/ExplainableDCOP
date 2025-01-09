import copy
import random
import threading
from operator import truediv
from itertools import combinations

from matplotlib.pyplot import connect

#from Algorithm_BnB import BranchAndBound
from Agents import *
from Algorithm_BnB_Central import Bnb_central, Bnb_Central_Agent
from Algorithm_MGM import MGM
from Globals_ import *

from enums import *
from abc import ABC, abstractmethod
from collections import defaultdict



class Neighbors():
    def __init__(self, a1:Agent, a2:Agent, cost_generator,dcop_id):


        if a2 is None:
            self.a1 = a1
            self.a2 = a1
        else:
            if a1.id_<a2.id_:
                self.a1 = a1
                self.a2 = a2
            else:
                self.a1 = a2
                self.a2 = a1

        self.dcop_id = dcop_id

        if a2 is not None:
            self.rnd_cost = random.Random((((dcop_id+1)+100)+((a1.id_+1)*1710)+((a2.id_*281)*13))*17)
        else:
            self.rnd_cost = random.Random(((dcop_id+1)+100)+((a1.id_+1)*1710))

        for _ in range(5):self.rnd_cost.random()
        self.cost_table = {}
        self.create_dictionary_of_costs(cost_generator)

    def __str__(self):
        return self.a1.__str__()+":"+self.a2.__str__()


    def is_ids_this_object(self,id_1,id_2):
        if (self.a1.id_==id_1 and self.a2.id_ == id_2) or (self.a1.id_==id_2 and self.a2.id_ == id_1):
            return True
        else:
            return False

    def get_cost(self, first_agent_id_input, first_agent_value, second_agent_id_input, second_agent_value):
        if isinstance(first_agent_id_input,int):
            return self.get_cost_given_id_int(first_agent_id_input, first_agent_value, second_agent_id_input, second_agent_value)
        if first_agent_id_input<second_agent_id_input:
            ap =(first_agent_id_input, first_agent_value, second_agent_id_input, second_agent_value)
        else:
            ap =(second_agent_id_input, second_agent_value, first_agent_id_input, first_agent_value)
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
            if self.a2.id_== self.a1.id_:
                first_tuple = ("A_" + str(self.a1.id_), d_a1)
                second_tuple = ("A_" + str(self.a1.id_), d_a1)
                ap = (first_tuple, second_tuple)
                cost = cost_generator(self.rnd_cost, self.a1, None, d_a1, None)
                self.cost_table[ap] = cost
            else:
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

        self.global_clock = 0
        self.agents_init()
        while not self.all_agents_complete():
            self.global_clock = self.global_clock + 1
            is_empty = self.mailer.place_messages_in_agents_inbox()
            if is_empty:
                print("DCOP:",str(self.dcop_id),"global clock:",str(self.global_clock), "is over because there are no messages in system ")
                break
            self.agents_perform_iteration(self.global_clock)

    def __str__(self):
        return self.dcop_name+",id_"+str(self.dcop_id)+",A_"+str(self.A)+",D_"+str(self.D)



    def agents_init(self):
        for a in self.agents:
            a.initialize()

    @abstractmethod
    def create_neighbors(self):
        pass

    @abstractmethod
    def create_summary(self): pass

    def all_agents_complete(self):
        for a in self.agents:
            if not a.is_algorithm_complete():
                return False
        return True

    def inform_root(self):
        if self.algorithm == Algorithm.bnb:
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

        if self.algorithm == Algorithm.bnb:
            a = Bnb_Central_Agent(i + 1, self.D)
        if self.algorithm == Algorithm.mgm:
            a = MGM(i + 1, self.D,self.dcop_id)
        self.agents.append(a)


class DCOP_RandomUniform(DCOP):
    def __init__(self, id_,A,D,dcop_name,algorithm,p1):
        self.p1 = p1
        DCOP.__init__(self,id_,A,D,dcop_name,algorithm)

    def create_summary(self):
        return self.dcop_name+"_A_"+str(self.A)+"_p1_"+str(self.p1)

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

    def create_summary(self):
        return self.dcop_name+"_A_"+str(self.A)+"_p1_"+str(graph_coloring_p1)

    def create_neighbors(self):
        for i in range(self.A):
            a1 = self.agents[i]
            for j in range(i+1,self.A):
                a2 = self.agents[j]
                rnd_number = self.rnd_neighbors.random()
                if rnd_number<graph_coloring_p1:
                    self.neighbors.append(Neighbors(a1, a2, graph_coloring_cost_function, self.dcop_id))




class DCOP_MeetingSchedualingV2(DCOP):
    def __init__(self,id_, A, dcop_name, algorithm):
        DCOP.__init__(self, id_, A, time_slots_D, dcop_name, algorithm)
        self.users_amount = user_amount
        self.meetings = A
        self.meetings_per_user_amount = meetings_per_user
        self.min_users_per_meeting = min_users_per_meeting
        self.check_input()


        self.rnd_users_per_meet_distribution = random.Random((id_ + 782) * 17)
        #self.rnd_meeting_per_agent = random.Random((id_ + 412) * 17)
        for _ in range(5):
            #self.rnd_meeting_per_agent.random()
            self.rnd_users_per_meet_distribution.random()

        self.users_perfs_dict = {}
        self.user_allocation_left = {}
        for user in range(self.users_amount ):
            self.users_perfs_dict[user] = self.create_rnd_pref(user)
            self.user_allocation_left[user] = self.meetings_per_user_amount
        #----------
        self.meetings_per_user_dict = {}
        self.get_meeting_per_agent_dict()
        #----------
        self.meeting_perf_per_time_slot_dict = {}
        self.get_meeting_perf_per_time_slot_dict()
        self.update_perf_per_time_slot_attribute_for_meetings()
        #----------
        self.user_meetings_dict = {}
        self.get_user_meetings_dict()
        #----------
        self.neighbors_tuples = []
        self.get_neighbors_tuples()

        self.create_neighbors2()
        self.connect_agents_to_neighbors()

    def update_perf_per_time_slot_attribute_for_meetings(self):
        for meeting_id, meeting_obj in self.agents_dict.items():
            perf_per_time_slot = self.meeting_perf_per_time_slot_dict[meeting_id]
            meeting_obj.perf_per_time_slot = perf_per_time_slot
    def get_all_pref_of_users_per_time_slot_dict(self,users_list):
        ans = {}
        for time_slot in range(time_slots_D):
            ans[time_slot] = []
        for user in users_list:
            user_pref = self.users_perfs_dict[user]
            for time_slot, pref in user_pref.items():
                ans[time_slot].append(pref)
        return ans
    def get_meeting_perf_per_time_slot_dict(self):
        for meeting_id,users_list in self.meetings_per_user_dict.items():
            total_per_time_slot = self.get_all_pref_of_users_per_time_slot_dict(users_list)
            sum_per_time_slot = {}
            for time_slot, prefs_list in total_per_time_slot.items():
                sum_per_time_slot[time_slot] = sum(prefs_list)
            self.meeting_perf_per_time_slot_dict[meeting_id] = sum_per_time_slot
    def create_copy_and_remove_meetings_that_user_is_there(self,user):
        temp_dict = copy.deepcopy(self.meetings_per_user_dict)
        for m_id, list_of_users in self.meetings_per_user_dict.items():
            if user in list_of_users:
                del temp_dict[m_id]
        return temp_dict
    def get_meeting_per_agent_dict(self):
        self.meetings_per_user_dict = {}

        for m_id in self.agents_dict.keys(): self.meetings_per_user_dict[m_id] = []
        self.allocate_min_amount_of_users_to_meetings()
        self.finish_allocation()






    def meetings_per_agent_dict_have_required_min_per_meet(self):
        for users_in_meet in self.meetings_per_user_dict.values():
            if len(users_in_meet) < self.min_users_per_meeting:
                return False
        return True


    def create_rnd_pref(self,a):
        ans = {}
        rnd_pref_time = random.Random((a+23)*17+(self.dcop_id)*97)
        for _ in range(5): rnd_pref_time.randint(1,5)
        domain = []
        for d in range(self.D): domain.append(d)
        pref_domain = rnd_pref_time.choice(domain)
        for d in domain:
            mu = abs(d - pref_domain)

            #std = meeting_schedul_std
            #cost = round(rnd_pref_time.gauss(mu, std))
            #if cost<meeting_schedul_min_cost:
            #    cost = meeting_schedul_min_cost
            #if cost>meeting_schedul_max_cost:
            #    cost = meeting_schedul_max_cost

            ans[d] = mu
        return ans

    def create_summary(self):
        return  self.dcop_name +"_meetings_" + str(self.meetings) +  "_users_" + str(
            self.users_amount) + "_per_agent_" + str(meetings_per_user) + "_time_slots_" + str(time_slots_D)

    def create_neighbors(self):
        pass

    def create_neighbors2(self):
        for meeting_id_1, meeting_id_2 in self.neighbors_tuples:
            meet_obj_1 = self.agents_dict[meeting_id_1]
            meet_obj_2 = self.agents_dict[meeting_id_2]
            n = Neighbors(meet_obj_1, meet_obj_2, meeting_scheduling_v2_cost_function, self.dcop_id)
            self.neighbors.append(n)

    def check_input(self):
        agents_attending_meetings = self.users_amount * self.meetings_per_user_amount
        if agents_attending_meetings < self.min_users_per_meeting * self.meetings:
            raise ValueError("need min amount of agents in a meeting to be 2")
        if self.meetings_per_user_amount > self.meetings:
            raise ValueError("meetings_per_agent>meetings")

    def allocate_min_amount_of_users_to_meetings(self):

        while not self.meetings_per_agent_dict_have_required_min_per_meet():
            for user in range(self.users_amount):
                if self.meetings_per_agent_dict_have_required_min_per_meet():
                    break
                temp_dict = self.create_copy_and_remove_meetings_that_user_is_there(user)
                min_length = min(len(v) for v in temp_dict.values())
                keys_with_shortest_length = [k for k, v in temp_dict.items() if len(v) == min_length]
                m_id = self.rnd_users_per_meet_distribution.choice(keys_with_shortest_length)
                self.meetings_per_user_dict[m_id].append(user)
                self.user_allocation_left[user] = self.user_allocation_left[user] - 1

        for user_id, meetings_allocated_left in self.user_allocation_left.items():
            if meetings_allocated_left<0:
                raise Exception("dont have enought users attending meetings to allocate")

    def clear_user_allocation_left(self):
        users_that_are_done = []
        for user_id, meetings_allocated_left in self.user_allocation_left.items():
            if meetings_allocated_left == 0:
                users_that_are_done.append(user_id)
        for user_id in users_that_are_done:
            del self.user_allocation_left[user_id]

    def get_meetings_that_user_is_not_allocated_to(self,user_id):
        ans = []
        for m_id, users_allocated in self.meetings_per_user_dict.items():
            if user_id in users_allocated:
                ans.append(m_id)
        return ans


    def finish_allocation(self):
        self.clear_user_allocation_left()

        for user_id, meetings_allocated_left in self.user_allocation_left.items():
            meetings_that_user_is_not_allocated_to = self.get_meetings_that_user_is_not_allocated_to(user_id)
            possible_meetings_to_allocate = copy.deepcopy(list(self.meetings_per_user_dict.keys()))
            possible_meetings_to_allocate = [item for item in possible_meetings_to_allocate if item not in meetings_that_user_is_not_allocated_to]
            random_selection = self.rnd_users_per_meet_distribution.sample(possible_meetings_to_allocate, meetings_allocated_left)
            for meeting_id in random_selection:
                self.meetings_per_user_dict[meeting_id].append(user_id)

    def get_user_meetings_dict(self):

        for meeting_id, users_list in self.meetings_per_user_dict.items():
            for user_id in users_list:
                if user_id not in self.user_meetings_dict.keys():
                    self.user_meetings_dict[user_id] = []
                self.user_meetings_dict[user_id].append(meeting_id)

    def get_neighbors_tuples(self):
        self.neighbors_tuples = []
        for user_id, meetings_of_users_list in self.user_meetings_dict.items():
            meetings_of_users_list = sorted(meetings_of_users_list)
            for i in range(len(meetings_of_users_list)):
                for j in range(i + 1, len(meetings_of_users_list)):
                    tup = (meetings_of_users_list[i], meetings_of_users_list[j])
                    if tup not in self.neighbors_tuples:
                        self.neighbors_tuples.append(tup)



class DCOP_MeetingSchedualing(DCOP):
    def __init__(self,id_, A, meetings,meetings_per_agent,time_slots_D, dcop_name, algorithm):
        DCOP.__init__(self, id_, A*meetings_per_agent, time_slots_D, dcop_name, algorithm)
        self.users_amount = A
        self.meetings = meetings
        self.meetings_per_agent = meetings_per_agent
        #if A*meetings_per_agent<meetings*2  :
            #raise ValueError("A*meetings_per_agent<meetings*2")
        if meetings_per_agent>meetings:
            raise ValueError("meetings_per_agent>meetings")

        self.rnd_agents_per_meet = random.Random((id_ + 782) * 17)
        self.rnd_meeting_per_agent = random.Random((id_+412)*17)

        for a in self.agents:
            a.create_unary_costs(self.dcop_id)



        self.rnd_agents_per_meet = random.Random((id_ + 782) * 17)
        self.rnd_meeting_per_agent = random.Random((id_+412)*17)

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
        self.connect_agents_to_neighbors()
        #unary_constraints =
        #self.connect_unary_to_self(unary_constraints)

        #sparse_random_uniform_cost_function()

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
            agents_index += 1
        return agents_dict

    def create_summary(self):
        return "A_" + str(self.users_amount) +"_" + self.dcop_name +"_meetings_" + str(self.meetings) +"_per_agent_" + str(meetings_per_user) + "_time_slots_" + str(time_slots_D)

    def get_same_time_slot_agents(self):
        same_time_slot_agents = {}
        for agent in self.agents:
            value = agent.variable
            if value not in same_time_slot_agents:
                same_time_slot_agents[value] = []
            same_time_slot_agents[value].append(agent)
        return same_time_slot_agents
    def get_complete_assignment(self):
        if special_generator_for_MeetingScheduling:
            self.complete_assignment = {}
            same_time_slot_agents = self.get_same_time_slot_agents()
            self.complete_assignment = self.map_meeting_to_time_slot(same_time_slot_agents)

        else:
            self.complete_assignment = DCOP.get_complete_assignment(self)


        return self.complete_assignment

    def map_meeting_to_time_slot(self,same_time_slot_agents):
        ans = {}
        for time_slot,meeting_agents in same_time_slot_agents.items():
            meeting_ids = []
            for agent in meeting_agents:
                meeting_ids.append(self.get_meeting_id_for_meet_agent(agent))
            #if not all(x == meeting_ids[0] for x in meeting_ids):
                #raise Exception("all meetings id should be the same")
            diff_meetings = []
            for meeting_id_slots in meeting_ids:
                if meeting_id_slots not in diff_meetings:
                    diff_meetings.append(diff_meetings)
            for m in diff_meetings:
                ans[m] = time_slot
            #get_meeting_index_given_meeting_agents()
        return ans

    def create_neighbors(self):
        pass

    def create_neighbors2(self):
        self.create_inequality_neighbors()
        self.create_equality_neighbors()
        self.create_unary_constraints()



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

    def get_meeting_id_of_agent(self,meeting_agent):
        for meeting_id, meeting_agents in self.agents_assigned_to_meetings_dict.items():
            if meeting_agent in meeting_agents:
                return meeting_id

    def get_meeting_id_of_agent_id(self,meeting_agent_id):
        for meeting_id, meeting_agents in self.agents_assigned_to_meetings_dict.items():
            for meeting_agent in meeting_agents:
                if meeting_agent.id_ == meeting_agent_id:
                    return meeting_id

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
                n = Neighbors(a1, a2, meeting_scheduling_must_be_non_equal_cost_function, self.dcop_id)
                self.neighbors.append(n)


    def create_equality_neighbors(self):
        for meeting_id, meeting_agents in self.agents_assigned_to_meetings_dict.items():
            all_pairs = list(combinations(meeting_agents, 2))
            for pair in all_pairs:
                a1, a2 = [pair[0], pair[1]]
                self.neighbors.append(Neighbors(a1, a2, meeting_scheduling_must_be_equal_cost_function, self.dcop_id))

    def create_unary_constraints(self):
        for a1 in self.agents:
            n = Neighbors(a1, None, meeting_scheduling_unary_constraint_cost_function, self.dcop_id)
            self.neighbors.append(n)




    def get_meeting_id_for_meet_agent(self, agent):
        for meeting_id,meeting_agents_in_meet in self.agents_assigned_to_meetings_dict.items():
            for other in meeting_agents_in_meet:
                if other.id_ ==  agent.id_:
                    return meeting_id

    def connect_unary_to_self(self, unary_constraints):
        for n in unary_constraints:
            n.a1.neighbors_obj.append(n)
            n.a1.neighbors_agents_id.append(n.a1.id_)
            n.a1.neighbors_obj_dict[n.a1.id_] = n





