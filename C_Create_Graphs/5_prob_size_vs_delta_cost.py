import pickle

import numpy as np
from matplotlib import pyplot as plt

from C_Create_Graphs.Graph_functions import *
from enums import ExplanationType, QueryType
from matplotlib.lines import Line2D


def get_full_dict(densities,agents_amounts,query_types,algos,explanation_type,vars_nums_list):
    ans = {}

    for density in densities:
        ans[density] = {}
        for query_type in query_types:
            ans[density][query_type] = {}
            for algo in algos:

                ans[density][query_type][algo] = {}
                for var_num in vars_nums_list:
                    ans[density][query_type][algo][var_num] = {}
                    for agent_amount in agents_amounts:
                        if algo == "Complete" and agent_amount>10:
                            break
                        input_dict = exp_dict[density][agent_amount][query_type][algo][var_num][explanation_type]
                        ans[density][query_type][algo][var_num][agent_amount]= input_dict

    return ans


def get_measure_dict(full_dict):
    ans = {}
    for density, dict_1 in full_dict.items():
        ans[density] = {}
        for query_type, dict_2 in dict_1.items():
            ans[density][query_type] = {}
            for algo,dict_3 in dict_2.items():
                ans[density][query_type][algo] = {}
                for var_num, dict_4 in dict_3.items():
                    ans[density][query_type][algo][var_num] = {}
                    for explanation_type,measures_all_dicts in dict_4.items():
                        ans[density][query_type][algo][var_num][explanation_type] = []
                        for measure_single_dict in measures_all_dicts:
                            ans[density][query_type][algo][var_num][explanation_type].append(measure_single_dict[measure_name])
    return ans


def get_avg_dict(measure_dict):
    ans = {}
    for density, dict_1 in measure_dict.items():
        ans[density] = {}
        for query_type, dict_2 in dict_1.items():
            ans[density][query_type] = {}
            for algo, dict_3 in dict_2.items():
                ans[density][query_type][algo] = {}
                for var_num, dict_4 in dict_3.items():
                    ans[density][query_type][algo][var_num] = {}
                    for explanation_type, measures_list in dict_4.items():
                        avg_ = sum(measures_list) / len(measures_list)
                        ans[density][query_type][algo][var_num][explanation_type] = avg_

    return ans


def get_all_avg_dict():
    densities = [0.2, 0.7]
    agents_amounts = range(5, 55,5)
    query_types = [QueryType.educated.name,  QueryType.rnd.name]
    algos = ["Complete", "One_Opt"]
    vars_nums_list = [1,5]
    explanations_type = ExplanationType.Shortest_Explanation.name

    full_dict = get_full_dict(densities,agents_amounts,query_types,algos,explanations_type,vars_nums_list)
    measure_dict = get_measure_dict(full_dict)
    return get_avg_dict(measure_dict)


def simply_avg_dict():
    ans = {}

    for query_name,query_new_name in selected_query_types_and_new_name.items():
        ans[query_new_name] = {}
        for algo,algo_new_name in selected_algos_and_new_name.items():
            ans[query_new_name][algo_new_name] = {}
            for agent_amount in range(5,55,5):
                ans[query_new_name][algo_new_name] =avg_dict[selected_density][query_name][algo][selected_var]

    return ans



if __name__ == '__main__':

    scale = "dcop" #
    prob ="meeting_scheduling" #"meeting_scheduling" #"random"

    folder_to_save = "5_prob_size_vs_delta_cost"


    graph_type = "5_prob_size_vs_delta_cost"
    file_name = "explanations_"+scale+"_scale_"+prob+".pkl"
    with open(file_name, "rb") as file:
        exp_dict = pickle.load(file)
    measure_name =  "Cost delta of Valid" #"Cost delta of All Alternatives""Cost delta of Valid"
    avg_dict = get_all_avg_dict()





    axes_titles_font = 14
    axes_number_font = 14


    curve_dcop_algos = {'Complete': 4, '1-Opt': 2.5}


    if prob == "meeting_scheduling":  # random:
        y_name = r"$\Delta$ cost (Symlog Scale)"
    else:
        y_name = (r"$\Delta$ cost")
    if prob == "meeting_scheduling":
        manipulate_y = True
    else:
        manipulate_y = False
    selected_var = 5
    x_name = "Amount of Agents"
    selected_density = 0.7
    data = simply_avg_dict()
    figure_name = graph_type+"_"+prob+"_"+str(int(selected_density*10))
    create_single_graph(data, ColorsInGraph.dcop_algorithms,curve_dcop_algos, x_name, y_name, folder_to_save, figure_name,manipulate_y=manipulate_y,x_min = 5,x_max=55,y_min=None,y_max=None,is_highlight_horizontal=True,x_ticks=range(5,55,5))


    selected_density = 0.2
    data = simply_avg_dict()
    figure_name = graph_type+"_"+prob+"_"+str(int(selected_density*10))
    create_single_graph(data, ColorsInGraph.dcop_algorithms,curve_dcop_algos, x_name, y_name, folder_to_save, figure_name,manipulate_y=manipulate_y,x_min = 5,x_max=55,y_min=None,y_max=None,is_highlight_horizontal=True,x_ticks=range(5,55,5))

