import matplotlib.pyplot as plt

from globals_ import *
from problems import *

def create_selected_dcop(i,A,D,dcop_name):
    if dcop_type == DcopType.sparse_random_uniform:
        return DCOP_RandomUniform(i,A,D,dcop_name)


def draw_dcop(dcop):
    if debug_draw_graph:
        draw_dcop_graph(dcop)
        #draw_dcop_dense_agent(dcop)



def solve_dcops(dcops):
    for dcop in dcops:
        draw_dcop(dcop)
        dcop.execute()


if __name__ == '__main__':
    A,D,dcop_name = given_dcop_create_input()
    dcops = []
    for i in range(repetitions):
        dcops.append(create_selected_dcop(i,A,D,dcop_name))
    solve_dcops(dcops)
    #create_data(dcops)

