import matplotlib.pyplot as plt

from Globals_ import *
from problems import *




def create_selected_dcop(i,dcop_type,algorithm):
    if dcop_type == DcopType.sparse_random_uniform:
        A = 3
        D = 3
        dcop_name = "Sparse Uniform"
        return DCOP_RandomUniformSparse(i, A, D, dcop_name, algorithm)
    if dcop_type == DcopType.dense_random_uniform:
        A = 5
        D = 5
        dcop_name = "Dense Uniform"
        return DCOP_RandomUniformSparse(i, A, D, dcop_name, algorithm)
    if dcop_type == DcopType.graph_coloring:
        A = 10
        D = 3
        dcop_name = "Graph Coloring"
        return DCOP_GraphColoring(i,A,D,dcop_name,algorithm)



if __name__ == '__main__':
    dcop_type = DcopType.sparse_random_uniform
    algorithm = Algorithm.branch_and_bound
    for i in range(repetitions):
        dcop = create_selected_dcop(i,dcop_type,algorithm)
        #draw_dcop(dcop)
        if is_center_solver:
            dcop.execute_center()
        else:
            dcop.execute_distributed()
        print("X")
        #dcop.create_queries()
    #create_data(dcops)


