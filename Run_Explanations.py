import pickle

from B_xdcop_files.XDCOPS import Explanation
from enums import ExplanationType

if __name__ == '__main__':
    folder_name = "pickles_query_scale"
    exp_name = "xdcops_meeting_scheduling_v2_A_[10]_p1_[0.7]_query_scale"

    with open(folder_name+"/"+exp_name+".pkl", "rb") as file:
        x_dcops_dict = pickle.load(file)
    ans = {}
    explanation_types = [ExplanationType.BroadcastCentral]
    for density, dict_1 in x_dcops_dict.items():
        ans[density] = {}
        for amount_agents, dict_2 in dict_1.items():
            ans[density][amount_agents] = {}
            for query_type, dict_3 in dict_2.items():
                ans[density][amount_agents][query_type] = {}
                for algo, dict_4 in dict_3.items():
                    ans[density][amount_agents][query_type][algo] = {}
                    for vars_in_query, x_dcops_list in dict_4.items():
                        ans[density][amount_agents][query_type][algo] = {}
                        for x_dcop in x_dcops_list:
                            dcop = x_dcop.dcop
                            query = x_dcop.query
                            for ex_type in explanation_types:
                                explanation = Explanation(dcop, query, ex_type)
                                if ex_type not in ans[density][amount_agents][query_type][algo]:
                                    ans[density][amount_agents][query_type][algo][ex_type.name]=[]
                                ans[density][amount_agents][query_type][algo][ex_type.name].append(explanation)
                                print()
