from enum import Enum

class DcopType(Enum):
    sparse_random_uniform = 1
    dense_random_uniform = 2
    graph_coloring = 3
  



class Algorithm(Enum):
    branch_and_bound = 1
    dsa_c = 2