from enum import Enum





class QueryType(Enum):
    educated = 1
    semi_educated = 2
    rnd = 3


class ExplanationType(Enum):
    Centralized = 1
    BroadcastCentral = 2
    BroadcastDistributed = 3


class DcopType(Enum):
    #sparse_random_uniform = 1
    #dense_random_uniform = 2
    random_uniform = 1
    graph_coloring = 2
    meeting_scheduling_v2  = 3

class RunWhat(Enum):
    dcops = 1
    xdcops = 2
    handle_data = 3

class Algorithm(Enum):
    bnb = 1
    mgm = 2