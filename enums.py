from enum import Enum

class ExplanationType(Enum):
    Centralized = 1
    BroadcastNaive = 2


class DcopType(Enum):
    sparse_random_uniform = 1
    dense_random_uniform = 2
    graph_coloring = 3
    meeting_scheduling  = 4

class RunWhat(Enum):
    dcops = 1
    xdcops = 2
    handle_data = 3

class Algorithm(Enum):
    branch_and_bound = 1
    dsa_c = 2