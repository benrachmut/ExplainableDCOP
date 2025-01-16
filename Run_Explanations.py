import pickle

from B_xdcop_files.XDCOPS import Explanation
from enums import ExplanationType


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
                        print("vars_in_query", vars_in_query)

                        ans[density][amount_agents][query_type][algo][vars_in_query] = {}
                        for ex_type in explanation_types:
                            #print("ex_type", ex_type)

                            ans[density][amount_agents][query_type][algo][vars_in_query][ex_type.name] = []
                            for x_dcop in x_dcops_list:
                                dcop = x_dcop.dcop
                                query = x_dcop.query
                                explanation = Explanation(dcop, query, ex_type)
                                d_e = explanation.data_entry
                                ans[density][amount_agents][query_type][algo][vars_in_query][ex_type.name].append(d_e)
    return ans


if __name__ == '__main__':
    folder_begin = "pickels_"
    what_scale = "query_scale" #pickles_dcop_scale
    prob = "meeting_scheduling" #"random # meeting_scheduling
    directory = folder_begin+what_scale+"/"+prob
    import os

    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    print()
    ans= {}
    for file in files:
        with open(directory+"/"+file, "rb") as file:
            x_dcops_dict = pickle.load(file)


        explanation_types =  [ExplanationType.CEDAR_opt2, ExplanationType.Sort_Parallel]#list(ExplanationType)


        explanations = create_explanations()
        for density,others in explanations.items():
            ans[density] =others

    name_to_export = what_scale+"_"+prob+".pkl"
    with open("C_Create_Graphs/explanations_"+what_scale+"_"+prob+"_.pkl", "wb") as file:
        pickle.dump(ans, file)


