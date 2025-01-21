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
                        measures_list = input_dict
                        updated_list = []

                        for data_ in measures_list:
                            if is_ignonre_valid:
                                if data_["Cost delta of Valid"] > 0:
                                    updated_list.append(data_[measure_name])
                                else:
                                    print()
                            else:
                                updated_list.append(data_[measure_name])
                        #for single_measure in measures_list:
                        #    if single_measure[measure_name]>=0:
                        #        updated_list.append(1)
                        #    else:
                        #        updated_list.append(0)

                        #avg_ = sum(updated_list) / len(updated_list)
                        ans[density][query_type][algo][var_num][agent_amount] = updated_list
                    #    ans[density][query_type][algo][var_num][agent_amount]= input_dict


                    #for explanation_type, measures_list in dict_4.items():
                    #    updated_list = []
                    #    for single_measure in measures_list:
                    #        if single_measure>=0:
                    #            updated_list.append(1)
                    #        else:
                    #            updated_list.append(0)
                    #for agent_amount in agents_amounts:
                    #    if algo == "Complete" and agent_amount>10:
                    #        break
                    #    input_dict = exp_dict[density][agent_amount][query_type][algo][var_num][explanation_type]
                    #    ans[density][query_type][algo][var_num][agent_amount]= input_dict

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
                        #for measure_single_dict in measures_all_dicts:
                        ans[density][query_type][algo][var_num][explanation_type].append(measures_all_dicts)
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
                    for agent_amount, measures_list in dict_4.items():
                        avg_ = sum(measures_list[0]) / len(measures_list[0])
                        ans[density][query_type][algo][var_num][agent_amount] = avg_

    return ans


def get_all_avg_dict():
    if prob == "meeting_scheduling":
        densities = [0.2,0.5, 0.7]
    else:
        densities = [0.2, 0.7]
    agents_amounts = range(5, 55,5)
    query_types = [QueryType.educated.name,  QueryType.rnd.name]
    algos = ["Complete", "One_Opt"]
    vars_nums_list = [1,5]

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
    is_ignonre_valid  =False
    for is_with_legend in  [True, False]:

        scale = "dcop" #
        probs =["meeting_scheduling","random"]
        for prob in probs:

            graph_type = "7_prob_size_vs_number_of_constraints"
            file_name = "explanations_"+scale+"_scale_"+prob+".pkl"
            with open(file_name, "rb") as file:
                exp_dict = pickle.load(file)
            measure_name =  'Alternative # Constraint'
            explanations_type = ExplanationType.Varint_max.name

            avg_dict = get_all_avg_dict()


            curve_dcop_algos = {'Complete': 4, '1-Opt': 2.5}

            y_name = "Number of Constraints"
            x_name = "Amount of Agents"

            selected_var = 5
            selected_density = 0.7
            data = simply_avg_dict()
            folder_to_save,figure_name = get_folder_to_save_figure_name(graph_type,prob,selected_density)
            create_single_graph(is_with_legend, data, ColorsInGraph.dcop_algorithms, curve_dcop_algos, x_name,
                                y_name, folder_to_save,
                                figure_name,
                                x_min=5, x_max=50, y_min=None, y_max=None, is_highlight_horizontal=False,
                                )

            selected_density = 0.2
            data = simply_avg_dict()
            folder_to_save,figure_name = get_folder_to_save_figure_name(graph_type,prob,selected_density)
            create_single_graph(is_with_legend, data, ColorsInGraph.dcop_algorithms, curve_dcop_algos, x_name,
                                y_name, folder_to_save,
                                figure_name,
                                x_min=5, x_max=50, y_min=None, y_max=None, is_highlight_horizontal=False,
                                )
            if prob == "meeting_scheduling":
                selected_density = 0.5
                data = simply_avg_dict()
                folder_to_save, figure_name = get_folder_to_save_figure_name(graph_type, prob, selected_density)
                create_single_graph(is_with_legend, data, ColorsInGraph.dcop_algorithms, curve_dcop_algos, x_name,
                                    y_name, folder_to_save,
                                    figure_name,
                                    x_min=5, x_max=50, y_min=None, y_max=None, is_highlight_horizontal=False,
                                    )