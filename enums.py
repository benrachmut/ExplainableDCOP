from enum import Enum





class QueryType(Enum):
    educated = 1
    rnd = 2


class ExplanationType(Enum):
    Centralized = 1
    BroadcastCentral = 2
    BroadcastDistributed = 3


class DcopType(Enum):
    sparse_random_uniform = 1
    dense_random_uniform = 2
    graph_coloring = 3
    meeting_scheduling  = 4
    meeting_scheduling_v2  = 5

class RunWhat(Enum):
    dcops = 1
    xdcops = 2
    handle_data = 3

class Algorithm(Enum):
    branch_and_bound = 1
    dsa_c = 2