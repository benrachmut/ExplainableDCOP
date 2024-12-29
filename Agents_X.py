
from abc import ABC, abstractmethod

class AgentX(ABC):

    def __init__(self,id_,variable,domain,neighbors_agents_id):
        self.global_clock = 0
        self.id_ = id_

        self.variable = variable
        self.domain = domain
        self.neighbors_agents_id = neighbors_agents_id
        self.local_view = {}
        for k in self.neighbors_agents_id:
            self.local_view[k]=None

        self.inbox = None
        self.outbox = None
        self.local_clock = 0




    def get_general_info_for_records(self):
        return {"Agent_id":self.id_,"local_clock":self.local_clock,"global_clock":self.global_clock}


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



class AgentX_Query(AgentX,ABC):
    pass

class AgentX_Query_BroadcastNaive(AgentX_Query):
    def __init__(self,id_,variable,domain,neighbors_agents_id,agents_in_query):
        AgentX.__init__(self,id_,variable,domain,neighbors_agents_id)
        for agent_in_query in agents_in_query:
            if agent_in_query not in self.neighbors_agents_id:
                self.neighbors_agents_id.append(agent_in_query)




class AgentX_Broadcast(AgentX):
    def __init__(self,id_,variable,domain,neighbors_agents_id):
        AgentX.__init__(self,id_,variable,domain,neighbors_agents_id)
