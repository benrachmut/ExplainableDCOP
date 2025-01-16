from enum import Enum





class QueryType(Enum):
    educated = 1
    semi_educated = 2
    rnd = 3


class ExplanationType(Enum):
    #"CEDAR_opt2_no_sort": "Grounded_Constraints(O1)",
    #"CEDAR_opt2": "Shortest_Explanation(O2)",
    #"CEDAR_opt3B_not_optimal": "Sort_Parallel(O3)",
    #"CEDAR_variant_mean": "Varint(Mean)"

    #Centralized = 1
    Grounded_Constraints = 1

    Shortest_Explanation = 2

    #CEDAR_opt3A = 3
    Sort_Parallel = 4
    Sort_Parallel_Not_Opt = 5
    Varint_max=6
    Varint_mean=7

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
    Complete = 1
    One_Opt = 2