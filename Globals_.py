import random

from matplotlib import pyplot as plt

from enums import *
from random import Random
import pandas as pd


import os


os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz-10.0.1-win64/bin'
from itertools import chain

import graphviz


# for x dcop




# for DCOPS
algorithm = Algorithm.branch_and_bound
amount_agents = range(10,110,10)
is_center_solver = True
repetitions = 100

is_complete = None
incomplete_iterations = 1000

#### DCOPS_INPUT ####
#*******************************************#
# dcop_type = DcopType.sparse_random_uniform
#*******************************************#

sparse_p1 = 0.2
sparse_p2 = 1
sparse_min_cost = 1
sparse_max_cost = 100
sparse_D = 10


def sparse_random_uniform_cost_function(rnd_cost:Random,a1,a2,d_a1,d_a2):
    if rnd_cost.random()<sparse_p2:
        for _ in range(5):
            rnd_cost.randint(sparse_min_cost, sparse_max_cost)
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
dense_D = 10

def dense_random_uniform_cost_function(rnd_cost:Random,a1,a2,d_a1,d_a2):
    if rnd_cost.random()<dense_p2:
        return rnd_cost.randint(dense_min_cost, dense_max_cost)
    else:
        return 0



#*******************************************#
# dcop_type = DcopType.scale_free_network
#*******************************************#

scale_free_hubs = 10
scale_others_number_of_neighbors = 3
scale_min_cost = 1
scale_max_cost = 100
scale_D = 10

def scale_free_network_cost_function(rnd_cost:Random,a1,a2,d_a1,d_a2):
    #TODO
    raise Exception("TODO scale_free_network_cost_function")


#*******************************************#
# dcop_type = DcopType.graph_coloring
#*******************************************#

graph_coloring_p1 = 0.5
graph_coloring_constant_cost = 10
graph_coloring_D = 3

def graph_coloring_cost_function(rnd_cost:Random,a1,a2,d_a1,d_a2):
    if d_a1==d_a2:
        return graph_coloring_constant_cost
    else:
        return 0












######## dcop input ########


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
        records = dcop.collect_records()
        for k,v in records.items():
            if k not in ans:
                ans[k] = []
            ans[k] =ans[k]+v
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
    distinct_values = {agent.anytime_variable for agent in dcop.agents}
    random.seed(((dcop.dcop_id + 1) * 17) + (dcop.A + 1) * 170 + (dcop.D + 2) * 1700)
    random.shuffle(color_list_hex)

    # Create a dictionary pairing each value from distinct_values with a unique color
    distinct_values_colors = {}
    for value in distinct_values:
        # Pop a color from the shuffled color_list_hex to ensure uniqueness
        color = color_list_hex.pop()
        distinct_values_colors[value] = color
    return  distinct_values_colors







def copy_dict(dict):
    ans = {}
    for k,v in dict.items():
        ans[k]=v
    return ans


class PrepData():
    def __init__(self, num_variables,num_values):
        self.num_variables = num_variables
        self.num_values = num_values
        self.x_dcops =[]
        self.id_ = self.num_variables*100+self.num_values*10
        self.avg_cum_delta_over_dcop = {}

    def __eq__(self, other):
        return self.id_ == other.id_

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "variables_"+str(self.num_variables)+"_values_"+str(self.num_values)+"_"

    def execute_data(self,x_dcops):
        self.generate_avg_cum_delta_over_dcops(x_dcops)

    def generate_avg_cum_delta_over_dcops(self,x_dcops):
        lists = []
        for xdcop in x_dcops:
            lists.append(list(xdcop.explanation.min_cum_delta_from_solution.values()))
        ans = {}

        max_constraints_list = max(lists,key=len)
        for i in range(len(max_constraints_list)):
            delta_per_i = []
            for l in lists:
                try:
                    delta_per_i.append(l[i])
                except:
                    delta_per_i.append(l[len(l)-1])

            ans[i]= sum(delta_per_i)/len(delta_per_i)
        self.avg_cum_delta_over_dcop = ans


def plot_dictionaries(dicts, colors, labels, amount_variables, legend_title,name):
    """
    Plots multiple dictionaries on a graph with different colors.

    Args:
        dicts (list): List of dictionaries to plot.
        colors (list): List of colors corresponding to each dictionary.
        labels (list): List of labels for each dictionary (for the legend).
        amount_variables (int): Number of variables for the title.
        legend_title (str): Title for the legend.
    """
    if len(dicts) != len(colors) or len(dicts) != len(labels):
        raise ValueError("The number of dictionaries, colors, and labels must match.")

    plt.figure(figsize=(10, 6))

    for i, dictionary in enumerate(dicts):
        x = list(dictionary.keys())
        y = list(dictionary.values())
        plt.plot(x, y, color=colors[i], label=labels[i], marker='o')  # Ensure labels[i] is passed

    plt.xlabel("Amount of Constraints")
    plt.ylabel("Average cumulative delta from solution")
    plt.title("|X|=" + str(amount_variables))
    plt.legend(title=legend_title)  # Add the legend title here
    plt.grid(True, linestyle='--', alpha=0.7)
    #plt.show()
    file_name = str(amount_variables)+"_"+name+".png"
    plt.savefig(file_name, format='png', dpi=300)  # Use high resolution
    plt.close()  # Close the plot to avoid display


central_bnb_problem_details_debug = False

central_bnb_debug = False
debug_draw_graph = True
debug_DFS_tree = True
debug_DFS_draw_tree = False
draw_dfs_tree_flag = False
debug_BNB = False
