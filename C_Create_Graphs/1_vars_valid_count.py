import pickle
from Graph_functions import *
import numpy as np
from matplotlib import pyplot as plt

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
                        updated_list = []
                        for single_measure in measures_list:
                            if single_measure>=0:
                                updated_list.append(1)
                            else:
                                updated_list.append(0)



                        avg_ = sum(updated_list) / len(updated_list)
                        ans[density][query_type][algo][var_num][explanation_type] = avg_

    return ans


def get_all_avg_dict():
    if prob == "meeting_scheduling":
        densities = [0.2,0.5,0.7]
    else:
        densities = [0.2,0.7]

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
        for algo,algo_new_name in selected_algos_and_new_name.items():
            ans[query_new_name][algo_new_name] = {}
            for var_ in selected_vars_nums_list:
                ans[query_new_name][algo_new_name][var_] = avg_dict[selected_density][query_name][algo][var_][selected_explanation_type]*100
    return ans


def print_data_for_table():
    print("$$$$$$$$$$$", prob, "$$$$$$$$$$$")

    print("*****", selected_density, "*****")
    for query_type, dict_1 in data.items():
        print("&&&", query_type, "&&&")
        for algo, dict_2 in dict_1.items():
            print("##", algo, "##")
            for k, v in dict_2.items():
                print(k, v)


if __name__ == '__main__':
    scale = "query" #
    probs = ["meeting_scheduling","random"]# "meeting_scheduling"
    for is_with_legend in [True,False]:

        for prob in probs:
            #folder_to_save = "1_vars_valid_count"
            graph_type = "1_vars_valid_count"
            file_name = "explanations_"+scale+"_scale_"+prob+".pkl"
            with open(file_name, "rb") as file:
                exp_dict = pickle.load(file)


            measure_name =  "Cost delta of Valid" #"Cost delta of All Alternatives""Cost delta of Valid"
            avg_dict = get_all_avg_dict()


            selected_vars_nums_list = range(1, 11)
            selected_explanation_type = ExplanationType.Shortest_Explanation.name

            curve_dcop_algos = {'Complete': 4, '1-Opt': 2.5}

            y_name = "Valid Explanation %"
            x_name = r" $|var(\sigma_Q)|$"
            ###################



            selected_density = 0.7
            data = simply_avg_dict()
            print_data_for_table()

            folder_to_save,figure_name = get_folder_to_save_figure_name(graph_type,prob,selected_density)

            create_single_graph(is_with_legend,data, ColorsInGraph.dcop_algorithms,curve_dcop_algos, x_name, y_name, folder_to_save, figure_name,x_min = 1,x_max=10,y_min=0,y_max=110,is_highlight_horizontal=True,x_ticks=range(1,11),horizontal_width = 10, horizontal_alpha = 0.2,horizontal_location = 100)
            #create_single_graph()



            ###################



            selected_density = 0.2
            data = simply_avg_dict()
            print_data_for_table()

            folder_to_save,figure_name = get_folder_to_save_figure_name(graph_type,prob,selected_density)
            create_single_graph(is_with_legend,data, ColorsInGraph.dcop_algorithms,curve_dcop_algos, x_name, y_name, folder_to_save, figure_name,x_min = 1,x_max=10,y_min=0,y_max=110,is_highlight_horizontal=True,x_ticks=range(1,11),horizontal_width = 10, horizontal_alpha = 0.2,horizontal_location = 100)


            if prob == "meeting_scheduling":
                selected_density = 0.5
                print_data_for_table()

                data = simply_avg_dict()
                folder_to_save, figure_name = get_folder_to_save_figure_name(graph_type, prob, selected_density)
                create_single_graph(is_with_legend, data, ColorsInGraph.dcop_algorithms, curve_dcop_algos, x_name,
                                    y_name, folder_to_save, figure_name, x_min=1, x_max=10, y_min=0, y_max=110,
                                    is_highlight_horizontal=True, x_ticks=range(1, 11), horizontal_width=10,
                                    horizontal_alpha=0.2, horizontal_location=100)
