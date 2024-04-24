from enums import *
from random import Random
import networkx as nx
import matplotlib.pyplot as plt
import os
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz-10.0.1-win64/bin'

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
    #filename=dcop.__str__(),
    g = graphviz.Graph("G", format = "pdf")
    for n in dcop.neighbors:
        g.edge(n.a1.__str__(), n.a2.__str__())
    #g.render(view=False)
    g.view()

    # Generate the PDF directly (without creating a text file)
    #pdf_bytes = g.pipe(format='pdf')

    # Save the PDF bytes to a file
    #with open('graph.pdf', 'wb') as pdf_file:
    #    pdf_file.write(pdf_bytes)



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
    g = graphviz.Digraph('G',filename="DCOP_ID_"+dcop_id+", DFS_tree", format="pdf")

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

    # View the graph (open it in the default viewer)
    g.view()
    ##########
    #g = graphviz.Graph("G", format="pdf")
    #for n in dcop.neighbors:
    #    g.edge(n.a1.__str__(), n.a2.__str__())
    ## g.render(view=False)
    #g.view()
    #########
    #G = nx.DiGraph()

    ## Add nodes to the graph
    #for node in dfs_nodes:
    #    G.add_node(node.id_)

    ## Add edges to the graph
    #for node in dfs_nodes:
    #    if node.dfs_father is not None:
    #        G.add_edge(node.dfs_father, node.id_)

    ## Manually assign positions based on depth
    #positions = {}
    #for node in dfs_nodes:
    #    depth = get_depth(node, dfs_nodes)
    #    positions[node.id_] = (depth, -node.id_)  # Assign positions based on depth and node ID

    ## Draw the graph with full lines for edges in the tree
    #nx.draw(G, positions, with_labels=True, arrows=True, node_color='lightblue', node_size=1000, edge_color='black')

    ## Draw node labels
    #node_labels = {node.id_: node.id_ for node in dfs_nodes}  # Use the node ID as label
    #nx.draw_networkx_labels(G, positions, labels=node_labels)

    ## Show the plot
    #plt.pause(0.01)

def get_depth(node, dfs_nodes):
    depth = 0
    while node.dfs_father is not None:
        depth += 1
        node = next((n for n in dfs_nodes if n.id_ == node.dfs_father), None)
    return depth


debug_draw_graph = True
debug_DFS_tree = True
debug_DFS_draw_tree = True
debug_BNB = True