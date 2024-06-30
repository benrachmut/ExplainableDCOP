import random
import threading

import Globals_
from Algorithm_BnB import BranchAndBound
from Agents import *
from Globals_ import *

from enums import *
from abc import ABC, abstractmethod


class AgentPair():
    def __init__(self, a1_id, a1_domain, a2_id, a2_domain):
        self.a1_id =a1_id
        self.a2_id =a2_id
        self.a1_domain = a1_domain
        self.a2_domain = a2_domain

        if a1_id < a2_id:
            self.agent_pair = (a1_id, a2_id)
            self.domain_pair = (a1_domain, a2_domain)
        else:
            self.agent_pair_identifier = (a2_id, a1_id)
            self.domain_pair = (a2_domain, a1_domain)

    def __str__(self):
        return "<"+self.a1_id+":"+self.a1_domain+"> <"+self.a2_id+":"+self.a2_domain+">"
    def __repr__(self):
        return self.__str__()


    def __hash__(self):
        return 0

    def __eq__(self, other):
        first = other.a1_id == self.a1_id
        second = other.a2_id == self.a2_id
        third = other.a1_domain == self.a1_domain
        forth = other.a2_domain == self.a2_domain
        return first and second and third and forth

class Neighbors():
    def __init__(self, a1:Agent, a2:Agent, cost_generator,dcop_id):

        if a1.id_<a2.id_:
            self.a1 = a1
            self.a2 = a2
        else:
            self.a1 = a2
            self.a2 = a1

        self.dcop_id = dcop_id
        self.rnd_cost = random.Random((((dcop_id+1)+100)+((a1.id_+1)+10)+((a2.id_+1)*1))*17)
        for _ in range(5):
            self.rnd_cost.random()
        self.cost_table = {}
        self.create_dictionary_of_costs(cost_generator)



    def is_ids_this_object(self,id_1,id_2):
        if (self.a1.id_==id_1 and self.a2.id_ == id_2) or (self.a1.id_==id_2 and self.a2.id_ == id_1):
            return True
        else:
            return False

    def get_cost(self, first_agent_id_input, first_agent_variable, second_agent_id_input, second_agent_variable):

        if first_agent_id_input<second_agent_id_input:
            ap =(first_agent_id_input,first_agent_variable,second_agent_id_input,second_agent_variable)
        else:
            ap =(second_agent_id_input, second_agent_variable, first_agent_id_input,first_agent_variable)
        ans = self.cost_table[ap]
        return ans


    def create_dictionary_of_costs(self,cost_generator):
        for d_a1 in self.a1.domain:
            for d_a2 in self.a2.domain:
                first_tuple = ("A_"+str(self.a1.id_),d_a1)
                second_tuple = ("A_"+str(self.a2.id_),d_a2)
                ap = (first_tuple,second_tuple)
                #ap = (self.a1.id_,d_a1,self.a2.id_,d_a2)#AgentPair(self.a1.id_, d_a1, self.a2.id_, d_a2)
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
        self.cond = threading.Condition(threading.RLock())

    def insert(self, list_of_msgs):
        #with self.cond:
        for msg in list_of_msgs:
            self.buffer.append(msg)
        #    self.cond.notify_all()

    def extract(self):
       #with self.cond:
        #    while len(self.buffer) == 0:
        #        self.cond.wait()
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
        self.records_dcop = {}


    def create_agents(self):
        for i in range(self.A):
            if self.algorithm == Algorithm.branch_and_bound:
                self.agents.append(BranchAndBound(i + 1, self.D))




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

    def execute(self):
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

    def draw_global_things(self):
        if Globals_.draw_dfs_tree_flag:
            draw_dfs_tree(self.agents,self.dcop_id)
            Globals_.draw_dfs_tree_flag = False

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






class DCOP_RandomUniform(DCOP):
    def __init__(self, id_,A,D,dcop_name,algorithm):
        DCOP.__init__(self,id_,A,D,dcop_name,algorithm)

    def create_neighbors(self):
        for i in range(self.A):
            a1 = self.agents[i]
            for j in range(i+1,self.A):
                a2 = self.agents[j]
                rnd_number = self.rnd_neighbors.random()
                if rnd_number<sparse_p1:
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
                if rnd_number<sparse_p1:
                    self.neighbors.append(Neighbors(a1, a2, graph_coloring_cost_function, self.dcop_id))
