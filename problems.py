import random

from agents import *
from globals import *
from abc import ABC, abstractmethod


class AgentPair():
    def __init__(self, a1_id, a1_domain, a2_id, a2_domain):
        if a1_id < a2_id:
            self.agent_pair = (a1_id, a2_id)
            self.domain_pair = (a1_domain, a2_domain)
        else:
            self.agent_pair_identifier = (a2_id, a1_id)
            self.domain_pair = (a2_domain, a1_domain)


class Neighbors():
    def __init__(self, a1:Agent, a2:Agent, cost_generator,dcop_id):
        self.a1 = a1
        self.a2 = a2

        self.dcop_id = dcop_id
        self.rnd_cost = random.Random(((dcop_id+1)+99)+((a1.id_+1)*19)+((a1.id_+8)*19))
        self.cost_generator = cost_generator
        stop here
        #cost_table.set_cost((agent1, agent2), ('Meeting1', 'Meeting2'), 10)
        # cost_table.set_cost((agent1, agent2), ('Meeting2', 'Meeting3'), 20)
        self.create_dictionary_of_costs(cost_generator, self.rnd_cost)





class DCOP(ABC):
    def __init__(self,id_):
        self.dcop_id = id_
        self.agents = self.create_agents()
        self.neighbors = []
        self.rnd_neighbors = random.Random((id_+5)*17)
        self.rnd_cost= random.Random((id_+7)*177)
        #self.mailer = Mailer()

    def create_agents(self):
        for i in range(A):
            self.agents.append(Agent(i+1,D))

    @abstractmethod
    def create_neighbors(self):pass




class DCOP_RandomUniform(DCOP):
    def __init__(self, id_):
        super.__init__(self,id_)



    def create_neighbors(self):
        for i in range(A):
            a1 = self.agents.append(self.agents[i])
            for j in range(i+1,A):
                a2 = self.agents.append(self.agents[j])
                if self.rnd_neighbors.random()<sparse_p1:
                    self.neighbors.append(Neighbors(a1, a2, sparse_random_uniform_cost_function, self.dcop_id))