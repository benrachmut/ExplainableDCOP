from enums import *
from random import Random
import networkx as nx
import matplotlib.pyplot as plt

dcop_type = DcopType.sparse_random_uniform
algorithm = Algorithm.branch_and_bound

is_complete = None
repetitions = 2
incomplete_iterations = 1000


#### DCOPS_INPUT ####

#*******************************************#
# dcop_type = DcopType.sparse_random_uniform
#*******************************************#
sparse_p1 = 0.5
sparse_p2 = 1
sparse_min_cost = 1
sparse_max_cost = 100



def sparse_random_uniform_cost_function(rnd_cost:Random,a1,a2,d_a1,d_a2):
    if rnd_cost.random()<sparse_p2:
        return rnd_cost.randint(sparse_min_cost, sparse_max_cost)
    else:
        return 0




# *******************************************#
# dcop_type = DcopType.dense_random_uniform
# *******************************************#

dense_p1 = 0.7
dense_p2 = 1
dense_min_cost = 1
dense_max_cost = 100

def dense_random_uniform_cost_function(rnd_cost:Random,a1,a2,d_a1,d_a2):
    if rnd_cost.random()<dense_p2:
        return rnd_cost.randint(sparse_min_cost, sparse_max_cost)
    else:
        return 0



#*******************************************#
# dcop_type = DcopType.scale_free_network
#*******************************************#

scale_free_hubs = 10
scale_others_number_of_neighbors = 3
scale_min_cost = 1
scale_max_cost = 100

def scale_free_network_cost_function(rnd_cost:Random,a1,a2,d_a1,d_a2):
    #TODO
    raise Exception("TODO scale_free_network_cost_function")


#*******************************************#
# dcop_type = DcopType.graph_coloring
#*******************************************#

graph_coloring_p1 = 0.05
graph_coloring_constant_cost = 10

def graph_coloring_cost_function(rnd_cost:Random,a1,a2,d_a1,d_a2):
    if d_a1==d_a2:
        return graph_coloring_constant_cost
    else:
        return 0


#*******************************************#
# dcop_type = DcopType.meeting_scheduling
#*******************************************#

meeting_schedule_meet_amount = 20







######## dcop input ########

def given_dcop_create_input():

    if dcop_type == DcopType.sparse_random_uniform:
        A = 10
        D = 10
        dcop_name = "Sparse Uniform"


    if dcop_type == DcopType.dense_random_uniform:
        A = 50
        D = 10
        dcop_name = "Dense Uniform"


    if dcop_type == DcopType.graph_coloring:
        A = 50
        D = 3
        dcop_name = "Graph Coloring"


    if dcop_type == DcopType.scale_free_network:
        A = 50
        D = 10
        dcop_name = "Scale Free"


    if dcop_type == DcopType.meeting_scheduling:
        A = 90
        D = 2
        dcop_name = "Meeting Scheduling"

    return A,D,dcop_name
    #    is_neighbor_function = TODO
    #    cost_generator_function = TODO
    #    cost_matrix_function = TODO

    #    raise Exception("I did not meeting scheduling yet")

def get_agent_id(a):
    return a.id_


def get_neighbor_str_tuple(neighbors):
    first_str = get_agent_id(neighbors.a1)
    second_str = get_agent_id(neighbors.a2)
    if first_str<second_str:
        return (first_str,second_str)
    else:
        return  (second_str,first_str)


def draw_dcop_graph(dcop):
    plt.figure()  # Create a new figure
    agents = [get_agent_id(item) for item in dcop.agents]
    neighbors = {get_neighbor_str_tuple(item) for item in dcop.neighbors}
    G = nx.Graph()
    G.add_nodes_from(agents)
    G.add_edges_from(neighbors)
    nx.draw(G, with_labels=True, node_color='skyblue', node_size=700, edge_color='k', linewidths=1, font_size=15,
            pos=nx.spring_layout(G))
    #plt.show()

def draw_dcop_dense_agent(dcop):
    plt.figure()  # Create a new figure
    a_max = dcop.most_dense_agent()
    agents = a_max.neighbors_agents_id
    neighbors = a_max.get_neighbors_tuples()
    G = nx.Graph()
    G.add_nodes_from(agents)
    G.add_edges_from(neighbors)
    nx.draw(G, with_labels=True, node_color='skyblue', node_size=700, edge_color='k', linewidths=1, font_size=15,
            pos=nx.spring_layout(G))
    #plt.show()


class Msg():

    def __init__(self, sender, receiver, information,msg_type):
        self.sender = sender
        self.receiver = receiver
        self.information = information
        self.msg_type = msg_type





bnb_tree_debug = True
