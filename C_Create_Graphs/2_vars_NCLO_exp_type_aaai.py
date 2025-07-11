import pickle

from C_Create_Graphs.Graph_functions_aaai import *

from enums import ExplanationType, QueryType


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
                        for comm in measures_all_dicts.keys():
                            for numbers_ in measures_all_dicts[comm]:
                                ans[density][query_type][algo][var_num][explanation_type].append(numbers_[selected_measure])
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
    if prob == "meeting_scheduling":
        densities = [0.5]
    else:
        densities = [0.2, 0.7]
    agent_amount = 10
    query_types = [QueryType.educated.name, QueryType.semi_educated.name]
    algos = ["BNB_Complete"]
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

                data_to_put = avg_dict[selected_density][query_name]["BNB_Complete"][var_num][exp_name]
                ans[query_new_name][exp_new_name][var_num]  = data_to_put
    return ans




if __name__ == '__main__':
    scale = "query" #
    selected_queries = [QueryType.educated,QueryType.semi_educated]
    probs =["meeting_scheduling"]
    for selected_query in selected_queries:
        for is_with_legend in [True,False]:

            for prob in probs:
                graph_type = "2_vars_NCLO_exp_type"

                file_name = "explanations_"+scale+"_scale_"+prob+"_aaai.pkl"
                with open(file_name, "rb") as file:
                    exp_dict = pickle.load(file)
                #del exp_dict[0.5][10][QueryType.semi_educated.name]

                selected_measure =  "NCLO_for_valid_solution"#" #"Cost delta of All Alternatives""Cost delta of Valid"
                avg_dict = get_all_avg_dict()




                selected_vars_nums_list = range(1, 11)
                selected_explanation_types = list(ExplanationType)



                curve_explanation_algos = {
                    "CEDAR": 3,
                    r"CEDAR$(O_1)$" : 3,
                    r"CEDAR$(O_2)$": 3,
                    r"CEDAR$(V_1)$": 3

                }
                y_name = "NCLO"
                x_name =  r" $|var(\sigma_Q)|$"

                #selected_density = 0.2
                #data = simply_avg_dict()
                #del data["Semi Educated"]["CEDAR$(V_2)$"]

                #folder_to_save,figure_name = get_folder_to_save_figure_name(graph_type,prob,selected_density)

                #create_single_graph(is_with_legend,data, ColorsInGraph.explanation_algorithms, curve_explanation_algos, x_name, y_name, folder_to_save,
                #                    figure_name,
                #                    x_min = 1,x_max=10, y_min=None, y_max=None, is_highlight_horizontal=False,x_ticks=range(1,11))

                #selected_density = 0.2
                #data = simply_avg_dict()
                #del data["Semi Educated"]["CEDAR$(V_2)$"]

                #folder_to_save,figure_name = get_folder_to_save_figure_name(graph_type,prob,selected_density)

                #create_single_graph(is_with_legend,data, ColorsInGraph.explanation_algorithms, curve_explanation_algos, x_name, y_name, folder_to_save,
                #                    figure_name,
                #                    x_min = 1,x_max=10, y_min=None, y_max=None, is_highlight_horizontal=False,x_ticks=range(1,11))

                if prob == "meeting_scheduling":
                    selected_density = 0.5
                    data = simply_avg_dict()
                    if selected_query == QueryType.educated:
                        del data["Next Best"]["CEDAR$(V_2)$"]
                        del data["Semi Educated"]

                    if selected_query == QueryType.semi_educated:
                        del data["Next Best"]
                        del data["Semi Educated"]["CEDAR$(V_2)$"]
                    folder_to_save, figure_name = get_folder_to_save_figure_name(graph_type, prob, selected_density)
                    figure_name = figure_name + "_"+selected_query.name
                    create_single_graph(is_with_legend, data, ColorsInGraph.explanation_algorithms, curve_explanation_algos,
                                        x_name, y_name, folder_to_save,
                                        figure_name,
                                        x_min=1, x_max=10, y_min=None, y_max=None, is_highlight_horizontal=False,
                                        x_ticks=range(1, 11))
