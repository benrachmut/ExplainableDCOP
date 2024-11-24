import pickle

import matplotlib.pyplot as plt

from Globals_ import *
from problems import *

dcop_type = DcopType.sparse_random_uniform
algorithm = Algorithm.branch_and_bound
amount_agents = range(10,110,10)
is_center_solver = True
repetitions = 100
is_create_dcops_pickle = True


def get_DCOP(i,algorithm,dcop_type,A = 50):
    if dcop_type == DcopType.sparse_random_uniform:
        return DCOP_RandomUniform(i, A, sparse_D, "Sparse Uniform", algorithm,sparse_p1)
    if dcop_type == DcopType.dense_random_uniform:
        return DCOP_RandomUniform(i, A, dense_D, "Dense Uniform", algorithm,dense_p1)
    if dcop_type == DcopType.graph_coloring:
        return DCOP_GraphColoring(i, A,graph_coloring_D, "Graph Coloring", algorithm)


def get_pickle_name(A,property="complete"):
    return str(dcop_type.name)+"_"+property+"_agnets"+str(A)+".pkl"


def create_pickles():
        for A in amount_agents:
            dcops_complete = []
            for i in range(repetitions):
                print("start",dcop_type,"number:",i)

                dcop = get_DCOP(i,algorithm,dcop_type,A )
                #draw_dcop(dcop)
                if is_center_solver:
                    dcop.execute_center()
                else:
                    dcop.execute_distributed()
                dcops_complete.append(dcop)
                # Open a file to save the pickle
                pickle_name = get_pickle_name(A,"complete")
                with open(pickle_name, "wb") as file:
                    pickle.dump(dcops_complete, file)

if __name__ == '__main__':
    if is_create_dcops_pickle:
        create_pickles()

    else:
        pickle_name = get_pickle_name(5, "complete")
        with open(pickle_name, "rb") as file:
            loaded_data = pickle.load(file)

        print()


