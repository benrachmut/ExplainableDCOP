import random
import threading

from agents import *
from globals import *
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

class Neighbors():
    def __init__(self, a1:Agent, a2:Agent, cost_generator,dcop_id):
        self.a1 = a1
        self.a2 = a2
        self.dcop_id = dcop_id
        self.rnd_cost = random.Random(((dcop_id+1)+99)+((a1.id_+1)*19)+((a1.id_+8)*19))
        self.cost_table = {}
        self.create_dictionary_of_costs(cost_generator)




    def create_dictionary_of_costs(self,cost_generator):
        for d_a1 in self.a1.domain:
            for d_a2 in self.a2.domain:
                ap = AgentPair(self.a1.id_, d_a1, self.a2.id_, d_a2)
                cost = cost_generator(self.rnd_cost,self.a1,self.a2,d_a1,d_a2)
                self.cost_table[ap] = cost


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
        with self.cond:
            self.buffer.append(list_of_msgs)
            self.cond.notify_all()

    def extract(self):
        with self.cond:

            while len(self.buffer) == 0:
                self.cond.wait()
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
        self.agents = {}
        for a in agents:
            outbox = UnboundedBuffer()
            self.agents[a.id_] = outbox
            a.inbox = outbox
            a.outbox = self.inbox

class DCOP(ABC):
    def __init__(self,id_,A,D,dcop_name):
        self.dcop_id = id_
        self.A = A
        self.D = D
        self.dcop_name = dcop_name
        self.agents = []
        self.create_agents()
        self.neighbors = []
        self.rnd_neighbors = random.Random((id_+5)*17)
        self.rnd_cost= random.Random((id_+7)*177)
        self.create_neighbors()
        self.connect_agents_to_neighbors()
        self.mailer = Mailer(self.agents)

    def create_agents(self):
        for i in range(self.A):
            if algorithm == Algorithm.branch_and_bound:
                if i == 0:
                    self.agents.append(BranchAndBound(i+1,self.D,is_root=True))
                else:
                    self.agents.append(BranchAndBound(i+1,self.D,is_root=False))


    def most_dense_agent(self):
        # Sort agents by the number of neighbors (descending) and then by id_ (ascending)
        sorted_agents = sorted(self.agents, key=lambda x: (-len(x.neighbors_obj), x.id_))
        # Return the agent with the most neighbors
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
        for i in

    @abstractmethod
    def create_neighbors(self): pass
class DCOP_RandomUniform(DCOP):
    def __init__(self, id_,A,D,dcop_name):
        DCOP.__init__(self,id_,A,D,dcop_name)



    def create_neighbors(self):
        for i in range(self.A):
            a1 = self.agents[i]
            for j in range(i+1,self.A):
                a2 = self.agents[j]
                rnd_number = self.rnd_neighbors.random()
                if rnd_number<sparse_p1:
                    self.neighbors.append(Neighbors(a1, a2, sparse_random_uniform_cost_function, self.dcop_id))