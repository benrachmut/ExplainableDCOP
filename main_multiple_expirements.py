import pickle

import matplotlib.pyplot as plt

from Globals_ import *
from XDCOPS import *
from problems import *
from Functions import *


def get_DCOP(i,algorithm,dcop_type,A = 50):
    if dcop_type == DcopType.sparse_random_uniform:
        return DCOP_RandomUniform(i, A, sparse_D, "Sparse Uniform", algorithm,sparse_p1)
    if dcop_type == DcopType.dense_random_uniform:
        return DCOP_RandomUniform(i, A, dense_D, "Dense Uniform", algorithm,dense_p1)
    if dcop_type == DcopType.graph_coloring:
        return DCOP_GraphColoring(i, A,graph_coloring_D, "Graph Coloring", algorithm)

def create_pickles():
    for A in amount_agents:
        dcops_complete = []
        for i in range(repetitions):
            print("start", dcop_type, "number:", i)

            dcop = get_DCOP(i, algorithm, dcop_type, A)
            # draw_dcop(dcop)
            if is_center_solver:
                dcop.execute_center()
            else:
                dcop.execute_distributed()
            dcops_complete.append(dcop)
            # Open a file to save the pickle
            pickle_name = get_pickle_name(A, "complete")
            with open(pickle_name, "wb") as file:
                pickle.dump(dcops_complete, file)


def get_dcops(A, property= "complete"):
    pickle_name = get_pickle_name(A, property)
    with open(pickle_name, "rb") as file:
        return pickle.load(file)


if __name__ == '__main__':
    A = 10
    if is_create_dcops_pickle:
        create_pickles()
    else:
        dcops = get_dcops(A)
        with_connectivity_constraint = True
        seeds_xdcop = range(0, 100)
        nums_variables = range(7, A)
        max_domain = len(dcops[0].agents[0].domain)
        nums_values = [5]  # range(1, max_domain-1)


        x_dcops = []
        for dcop in dcops:
            dcop.create_agent_dict()
            for num_variables in nums_variables:
                for num_values in nums_values:
                    for seed_ in seeds_xdcop:
                        query = QueryGenerator(dcop,seed_,num_variables,num_values,with_connectivity_constraint)



        print()


