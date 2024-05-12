import random

from enums import *
from random import Random
import pandas as pd

import networkx as nx
import matplotlib.pyplot as plt
import os
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz-10.0.1-win64/bin'
from itertools import chain

import graphviz

dcop_type = DcopType.graph_coloring
algorithm = Algorithm.branch_and_bound

is_complete = None
repetitions = 1
incomplete_iterations = 1000
draw_dfs_tree_flag = False


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

graph_coloring_p1 = 0.5
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
        A = 10
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
    filename=dcop.__str__()
    g = graphviz.Graph("G",filename=filename, format = "pdf")


    for n in dcop.neighbors:
        g.edge(n.a1.__str__(), n.a2.__str__())
    g.render(view=False)




class Msg():

    def __init__(self, sender, receiver, information,msg_type):
        self.sender = sender
        self.receiver = receiver
        self.information = information
        self.msg_type = msg_type



def draw_dfs_tree(dfs_nodes,dcop_id):
    # Create a directed graph
    # filename=TODO

    # Create a new graph
    g = graphviz.Digraph('G',filename="DFS_tree,id_"+str(dcop_id), format="pdf")

    # Add nodes to the graph
    for node in dfs_nodes:
        g.node(str(node.id_))

    # Add edges to the graph with solid line style
    added_edges = set()  # To keep track of added edges

    for node in dfs_nodes:
        if node.dfs_father is not None:
            edge = (str(node.dfs_father), str(node.id_))
            if edge not in added_edges:
                g.edge(*edge)
                added_edges.add(edge)

        for child_id in node.dfs_children:
            edge = (str(node.id_), str(child_id))
            if edge not in added_edges:
                g.edge(*edge)
                added_edges.add(edge)
    g.render(view=False)

    # View the graph (open it in the default viewer)
    #g.view()
    ##########


def get_all_personal_data_dict(dcops):
    ans = {}
    for dcop in dcops:
        records = dcop.records_dcop
        for k in records.keys():
            if k not in ans.keys():
                ans[k] = []
            ans[k] = ans[k] + records[k]
    return ans


def create_personal_data(dcops):
    all_data_dict = get_all_personal_data_dict(dcops)
    lengths = [len(v) for v in all_data_dict.values()]
    if len(set(lengths)) == 1:
        df = pd.DataFrame(all_data_dict)
    else:
        print("Error: Lists have different lengths.")
    df.to_csv(dcops[0].__str__()+".csv",index=False)


def create_data(dcops):
    create_personal_data(dcops)


def draw_dcop(dcop):
    if debug_draw_graph:
        draw_dcop_graph(dcop)
        # draw_dcop_dense_agent(dcop)


color_list_hex = [
    "#FF0000", "#0000FF", "#008000", "#FFFF00", "#FFA500",
    "#800080", "#FFC0CB", "#A52A2A", "#00FFFF", "#FF00FF",
    "#F5F5DC", "#000000", "#FFFFFF", "#808080", "#C0C0C0",
    "#FFD700", "#E6E6FA", "#00FF00", "#800000", "#000080",
    "#808000", "#008080", "#40E0D0", "#EE82EE", "#BC8F8F",
    "#C71585", "#FFA07A", "#B0C4DE", "#778899", "#FFB6C1",
    "#90EE90", "#FAFAD2", "#E0FFFF", "#FFFACD", "#F0E68C",
    "#FFFFF0", "#CD5C5C", "#F0FFF0", "#DAA520", "#B22222",
    "#556B2F", "#DC143C", "#D2691E", "#5F9EA0", "#DEB887",
    "#00FFFF", "#FAEBD7", "#F0F8FF", "#7FFFD4", "#F0FFFF",
    "#FFEBCD", "#7FFF00", "#FF7F50", "#6495ED", "#E9967A",
    "#FF1493", "#00BFFF", "#1E90FF", "#FF00FF", "#DCDCDC",
    "#F8F8FF", "#FF69B4", "#4B0082", "#FFF0F5", "#ADD8E6",
    "#F08080", "#D3D3D3", "#87CEFA", "#0000CD", "#BA55D3",
    "#9370DB", "#3CB371", "#7B68EE", "#48D1CC", "#C71585",
    "#F5FFFA", "#FFE4E1", "#FFDEAD", "#FDF5E6", "#EEE8AA",
    "#98FB98", "#AFEEEE", "#FFEFD5", "#FFDAB9", "#CD853F",
    "#B0E0E6", "#8B4513", "#2E8B57", "#A0522D", "#87CEEB",
    "#00FF7F", "#4682B4", "#D2B48C", "#D8BFD8", "#FF6347",
    "#F5DEB3", "#9ACD32", "#00FA9A", "#66CDAA", "#7B68EE"
]


def get_distinct_values_colors(dcop):
    distinct_values = {agent.variable_anytime for agent in dcop.agents}
    random.seed(((dcop.dcop_id + 1) * 17) + (dcop.A + 1) * 170 + (dcop.D + 2) * 1700)
    random.shuffle(color_list_hex)

    # Create a dictionary pairing each value from distinct_values with a unique color
    distinct_values_colors = {}
    for value in distinct_values:
        # Pop a color from the shuffled color_list_hex to ensure uniqueness
        color = color_list_hex.pop()
        distinct_values_colors[value] = color
    return  distinct_values_colors

def draw_dcop_result(dcop):
    distinct_values_colors = get_distinct_values_colors(dcop)

    print()
    for a in dcop.agents:
       pass


def draw_result(dcop):
    if debug_draw_result:
        draw_dcop_result(dcop)






debug_draw_graph = False
debug_draw_result = True
debug_DFS_tree = True

debug_DFS_draw_tree = True
debug_BNB = True
