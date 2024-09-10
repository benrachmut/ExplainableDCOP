import matplotlib.pyplot as plt

from Globals_ import *
from problems import *




def create_selected_dcop(i,dcop_type,algorithm):
    if dcop_type == DcopType.sparse_random_uniform:
        A = 10
        D = 10
        dcop_name = "Sparse Uniform"
        return DCOP_RandomUniform(i,A,D,dcop_name,algorithm)
    if dcop_type == DcopType.dense_random_uniform:
        A = 10
        D = 10
        dcop_name = "Dense Uniform"
        return DCOP_RandomUniform(i,A,D,dcop_name,algorithm)
    if dcop_type == DcopType.graph_coloring:
        A = 10
        D = 3
        dcop_name = "Dense Uniform"
        return DCOP_GraphColoring(i,A,D,dcop_name,algorithm)



if __name__ == '__main__':
    dcop_type = DcopType.graph_coloring
    algorithm = Algorithm.branch_and_bound
    for i in range(repetitions):
        dcop = create_selected_dcop(i,dcop_type,algorithm)
        #draw_dcop(dcop)
        dcop.execute()
        print("X")
        #dcop.create_queries()
    #create_data(dcops)


