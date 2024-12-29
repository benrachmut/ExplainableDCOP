
from abc import ABC, abstractmethod

from Globals_ import *


class MsgTypeX(Enum):
    solution_value = 1

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
        self.atomic_operations = 0




    def get_general_info_for_records(self):
        return {"Agent_id":self.id_,"local_clock":self.local_clock,"global_clock":self.global_clock}


    def execute_iteration(self,global_clock):
        self.global_clock = global_clock
        msgs = self.inbox.extract()
        self.atomic_operations = 0

        if len(msgs)!=0:
            self.update_msgs_in_context(msgs)
            self.change_status_after_update_msgs_in_context(msgs)
            if self.is_compute_in_this_iteration():
                self.atomic_operations = self.compute()
                if self.atomic_operations is None: raise Exception("compute must return NCLO count")
                self.send_msgs()
                self.change_status_after_send_msgs()
            self.atomic_operations = 0

    def __str__(self):
        return "A_"+str(self.id_)

    @abstractmethod
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
        self.outbox.append(msg_list)



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
    def __init__(self, id_, variable, domain, neighbors_agents_id, query):
        AgentX.__init__(self, id_, variable, domain, neighbors_agents_id)
        self.query = query

    @abstractmethod
    def is_termination_condition_met(self): pass

class AgentX_Query_BroadcastNaive(AgentX_Query):
    def __init__(self,id_,variable,domain,neighbors_agents_id,query):
        AgentX_Query.__init__(self,id_,variable,domain,neighbors_agents_id,query)
        for agent_in_query in self.query.variables_in_query:
            if agent_in_query not in self.neighbors_agents_id:
                self.neighbors_agents_id.append(agent_in_query)




class AgentX_Broadcast(AgentX):
    def __init__(self,id_,variable,domain,neighbors_agents_id):
        AgentX.__init__(self,id_,variable,domain,neighbors_agents_id)
