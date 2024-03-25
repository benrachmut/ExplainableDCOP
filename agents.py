

from abc import ABC, abstractmethod




class Agent(ABC):

    def __init__(self,id_,D):
        self.id_ = id_
        self.domain = []
        for i in range(D): self.domain.append(i)
        self.neighbors = None

    def set_neighbors(self,neighbors):
        self.neighbors = neighbors

    def execute(self):

    @abstractmethod
    def my_abstract_method(self):
        pass




class AgentVariable(ABC):
