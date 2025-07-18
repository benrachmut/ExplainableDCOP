import pickle

from B_xdcop_files.XDCOPS import Explanation
from enums import ExplanationType, CommunicationType


def create_explanations():
    ans = {}
    for density, dict_1 in x_dcops_dict.items():
        print("density",density)
        ans[density] = {}
        for amount_agents, dict_2 in dict_1.items():
            print("amount_agents", amount_agents)

            ans[density][amount_agents] = {}
            for query_type, dict_3 in dict_2.items():
                print("query_type", query_type)

                ans[density][amount_agents][query_type] = {}
                for algo, dict_4 in dict_3.items():
                    print("algo", algo)

                    ans[density][amount_agents][query_type][algo] = {}
                    for vars_in_query, x_dcops_list in dict_4.items():
                        if vars_in_query<21:
                            print("vars_in_query", vars_in_query)

                            ans[density][amount_agents][query_type][algo][vars_in_query] = {}
                            for ex_type in explanation_types:
                                #print("ex_type", ex_type)

                                ans[density][amount_agents][query_type][algo][vars_in_query][ex_type.name] = {}
                                for communication_type in communication_types:
                                    ans[density][amount_agents][query_type][algo][vars_in_query][ex_type.name][communication_type.name] = []

                                    for x_dcop in x_dcops_list:
                                        dcop = x_dcop.dcop
                                        #print("dcop",dcop.dcop_id)
                                        query = x_dcop.query
                                        explanation = Explanation(dcop, query, ex_type, communication_type)
                                        d_e = explanation.data_entry
                                        ans[density][amount_agents][query_type][algo][vars_in_query][ex_type.name][communication_type.name].append(d_e)
    return ans


def cut_for_privacy(x_dcops_dict):
    selected = x_dcops_dict[0.2][10]["educated"]["Complete"][5]
    ans = {}
    ans[0.2] ={}
    ans[0.2][10] ={}
    ans[0.2][10]["educated"] ={}
    ans[0.2][10]["educated"]["Complete"] ={}
    ans[0.2][10]["educated"]["Complete"][5] =selected
    return ans


if __name__ == '__main__':
    folder_begin = "pickles_"
    what_scale = "query_scale" #dcop_scale, query_scale
    prob = "meeting_scheduling" #"random # meeting_scheduling
    is_privacy = False
    if is_privacy:
        directory = folder_begin+what_scale+"_privacy/"+prob+"_aaai"
    else:
        directory = folder_begin+what_scale+"/"+prob+"_aaai"

    import os

    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    ans= {}
    for file in files:
        with open(directory+"/"+file, "rb") as file:
            x_dcops_dict = pickle.load(file)
        #x_dcops_dict = cut_for_privacy(x_dcops_dict)
        if is_privacy:
            explanation_types = [ExplanationType.Shortest_Explanation]
            communication_types = list(CommunicationType)

        else:
            explanation_types = list(ExplanationType)
            communication_types = [CommunicationType.Broadcast]

        explanations = create_explanations()
        for density,others in explanations.items():
            ans[density] =others


    name_to_export = what_scale+"_"+prob+".pkl"
    if is_privacy:
        with open("C_Create_Graphs/explanations_"+what_scale+"_"+prob+"_privacy.pkl", "wb") as file:
            pickle.dump(ans, file)
    else:
        with open("C_Create_Graphs/explanations_" + what_scale + "_" + prob + "_aaai.pkl", "wb") as file:
            pickle.dump(ans, file)


