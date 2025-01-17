import pickle

import numpy as np
from matplotlib import pyplot as plt

from Graph_functions import *
from enums import ExplanationType, QueryType
from matplotlib.lines import Line2D


def get_full_dict(densities,agent_amount,query_types,algos,vars_nums_list,explanation_types):
    ans = {}
    for density in densities:
        ans[density] = {}
        for query_type in query_types:
            ans[density][query_type] = {}
            for algo in algos:
                ans[density][query_type][algo] = {}
                for var_num in vars_nums_list:
                    ans[density][query_type][algo][var_num] = {}
                    for explanation_type in explanation_types:
                        input_dict = exp_dict[density][agent_amount][query_type][algo][var_num][explanation_type]
                        ans[density][query_type][algo][var_num][explanation_type] = input_dict

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
    densities = [0.2,  0.7]
    agent_amount = 10
    query_types = [QueryType.educated.name, QueryType.rnd.name]
    algos = ["Complete", "One_Opt"]
    vars_nums_list = range(1, 11)
    explanation_types = []
    for exp_type in list(ExplanationType): explanation_types.append(exp_type.name)

    full_dict = get_full_dict(densities,agent_amount,query_types,algos,vars_nums_list,explanation_types)
    measure_dict = get_measure_dict(full_dict)
    return get_avg_dict(measure_dict)


def simply_avg_dict():
    ans = {}

    for query_name,query_new_name in selected_query_types_and_new_name.items():
        ans[query_new_name] = {}

        for exp_name,exp_new_name in selected_explanations_and_new_name.items():
            ans[query_new_name][exp_new_name] =  {}

            for var_num in selected_vars_nums_list:
                ans[query_new_name][exp_new_name][var_num]=  {}

                data_to_put = avg_dict[selected_density][query_name]["Complete"][var_num][exp_name]
                ans[query_new_name][exp_new_name][var_num]  = data_to_put
    return ans




if __name__ == '__main__':
    scale = "query" #
    prob ="meeting_scheduling" #"meeting_scheduling" #"random"

    folder_to_save = "2_vars_NCLO_exp_type"
    graph_type = "2_vars_NCLO_exp_type"

    file_name = "explanations_"+scale+"_scale_"+prob+".pkl"
    with open(file_name, "rb") as file:
        exp_dict = pickle.load(file)
    measure_name =  "NCLO"#NCLO_for_valid_solution" #"Cost delta of All Alternatives""Cost delta of Valid"
    avg_dict = get_all_avg_dict()


    selected_query_types_and_new_name = {QueryType.educated.name: "Educated",QueryType.rnd.name: "Random"}


    selected_vars_nums_list = range(1, 11)
    selected_explanation_types = list(ExplanationType)





    axes_titles_font = 14
    axes_number_font = 14
    linewidth = 3


    y_name = "NCLO"
    x_name = "Variables in Query"

    curve_explanation_algos = {
        "Grounded_Constraints(O1)": 3,
        "Shortest_Explanation(O2)": 3,
        "Sort_Parallel(O3)": 3,
        "Sort_Parallel(O3)*":3 ,
        # "Varint(Mean)":"brown",
        "Varint(Max)": 3
    }



    selected_density = 0.7
    data = simply_avg_dict()
    figure_name = graph_type+"_"+prob+"_"+str(int(selected_density*10))
    create_single_graph(data, ColorsInGraph.explanation_algorithms, curve_explanation_algos, x_name, y_name, folder_to_save,
                        figure_name,
                        x_min = 1,x_max=10, y_min=None, y_max=None, is_highlight_horizontal=False,x_ticks=range(1,11))

    selected_density = 0.2
    data = simply_avg_dict()
    figure_name = graph_type+"_"+prob+"_"+str(int(selected_density*10))
    create_single_graph(data, ColorsInGraph.explanation_algorithms, curve_explanation_algos, x_name, y_name, folder_to_save,
                        figure_name,
                        x_min = 1,x_max=10, y_min=None, y_max=None, is_highlight_horizontal=False,x_ticks=range(1,11))
