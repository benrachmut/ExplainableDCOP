import pickle

from A_dcop_files.problems import *
from B_xdcop_files.Queries import QueryGenerator, Query
from B_xdcop_files.XDCOPS import XDCOP
from enums import QueryType





def get_density_type_str(p1):
    if p1<0.5:
        return "sparse"
    if p1>0.5:
        return "dense"

    else:
        return "mid_density"



def get_DCOP(i,algorithm,dcop_type,A,p1):
    density_type_str = get_density_type_str(p1)


    if dcop_type == DcopType.random_uniform:
        try:
            return DCOP_RandomUniform(i, A, sparse_D,density_type_str+"_Random Uniform", algorithm,p1)
        except NoNeigException:
            raise NoNeigException()

    if dcop_type == DcopType.graph_coloring:
        try:
            return DCOP_GraphColoring(i, A,graph_coloring_D, density_type_str+"_Graph Coloring", algorithm,p1)
        except NoNeigException:
            raise NoNeigException()

    if  dcop_type == DcopType.meeting_scheduling_v2:


        return DCOP_MeetingSchedualingV2(id_=i, A=A, dcop_name=density_type_str+"_Meeting Scheduling",
                                       algorithm=algorithm,p1 = p1)


    #if dcop_type == DcopType.meeting_scheduling :
    #    return DCOP_MeetingSchedualing(id_=i, A=A, meetings=meetings, meetings_per_agent=meetings_per_user,
    #                                   time_slots_D=time_slots_D, dcop_name="Meeting Scheduling",
    #                                   algorithm = algorithm)


def create_dcops():
    ans = {}

    for p1 in p1s:
        ans[p1]={}
        for A in agents_amounts:
            ans[p1][A] = {}
            for algo in algos:
                ans[p1][A][algo.name] = {}

                max_num = 0
                if dcop_type == DcopType.graph_coloring:
                    max_num = 20
                if dcop_type == DcopType.meeting_scheduling_v2:
                    max_num = 10
                if dcop_type == DcopType.random_uniform and p1 < 0.3:
                    max_num = 15
                if dcop_type == DcopType.random_uniform and p1 > 0.3:
                    max_num = 10

                if not (algo == Algorithm.BNB_Complete and A > max_num):
                    i = 0
                    while len(ans[p1][A][algo.name])<repetitions:

                        try:
                            dcop = get_DCOP(i, algo, dcop_type, A,p1)
                            print(algo.name, "start:", i, dcop.create_summary())

                            if algo == Algorithm.BNB_Complete:
                                dcop.execute_bnb_center()
                            if algo == Algorithm.One_Opt:
                                dcop.execute_k_opt(1)
                            if algo == Algorithm.Two_Opt:
                                dcop.execute_k_opt(2)
                            if algo == Algorithm.Three_Opt:
                                dcop.execute_k_opt(3)
                            if algo == Algorithm.Four_Opt:
                                dcop.execute_k_opt(4)
                            if algo == Algorithm.Five_Opt:
                                dcop.execute_k_opt(5)

                            #else:
                            #    dcop.execute_distributed()
                            ans[p1][A][algo.name][i] = (dcop)
                            i = i+1
                        #with open("test_k_opt.pkl", "wb") as file:
                        #    pickle.dump(ans, file)
                        except NoNeigException:
                            i = i+1


    return ans





def create_x_standard_dcop(dcop, seed_query, num_variables, num_values,with_connectivity_constraint,query_type):
    query = QueryGenerator(dcop, seed_query, num_variables, num_values, with_connectivity_constraint,query_type).get_query()
    query.query_type = query_type

    return XDCOP(dcop, query)

def get_dcops_for_different_configs():
    ans = {}
    for density, dict_1 in dcops.items():
        #print("density",density)
        ans[density] = {}
        for agent_size, dict_2 in dict_1.items():
            #print("agent_size",agent_size)
            ans[density][agent_size] = {}
            algos_list = list(dict_2.keys())
            algos_to_remove = []
            for algo in algos_list:
                if len(dict_2[algo]) == 0:
                    algos_to_remove.append(algo)
            algos_list = [item for item in algos_list if item not in algos_to_remove]
            id_dcops_and_solutions_for_diff_algo = {}


            for dcop_id in dict_2[algos_list[0]].keys():
                id_dcops_and_solutions_for_diff_algo[dcop_id] = {}
                for algo in algos_list:
                    dcop_for_algo = dict_2[algo][dcop_id]
                    id_dcops_and_solutions_for_diff_algo[dcop_id][algo] = dcop_for_algo
            ans[density][agent_size] = id_dcops_and_solutions_for_diff_algo

    return ans

def get_x_dcops_dict(dcops_for_different_configs):
    ans = {}
    for density, dict_1 in dcops_for_different_configs.items():
        print("################ density",density)
        ans[density] = {}

        for agents_amount, dict_2 in dict_1.items():
            print("------ agents_amount", agents_amount)

            ans[density][agents_amount] = {}
            for query_type in query_types_list:
                print("**** query_type", query_type)

                ans[density][agents_amount][query_type.name] = {}

                if scale_type == ScaleType.query_scale:

                    amount_of_variables_list = range(1, agents_amount+ 1)
                else:
                    amount_of_variables_list = vars_DCOP_scale

                for amount_of_vars in amount_of_variables_list:
                    print("%% amount_of_vars", amount_of_vars)

                    ans[density][agents_amount][query_type.name][amount_of_vars] = {}
                    for dcop_id, dcops_dict in dict_2.items():

                        query_generator = QueryGenerator(dcops_dict, amount_of_vars, query_type)
                        #                      query_type).get_query()

                        for algo,dcop in dcops_dict.items():
                            if algo not in ans[density][agents_amount][query_type.name][amount_of_vars]:
                                ans[density][agents_amount][query_type.name][amount_of_vars][algo] = []
                            query = query_generator.get_query(algo, dcop_id)
                            ans[density][agents_amount][query_type.name][amount_of_vars][algo].append(XDCOP(dcop,query))
    return ans

def get_organized_dcop(x_dcop_to_re_organize):
    ans = {}
    for density, dict1 in x_dcop_to_re_organize.items():
        ans[density] = {}
        for amount_vars, dict2 in dict1.items():
            ans[density][amount_vars] = {}
            for q_type, dict_3 in dict2.items():
                ans[density][amount_vars][q_type] = {}
                for dcop_id, dict_4 in dict_3.items():
                    for algo, x_dcop in dict_4.items():
                        if algo not in ans[density][amount_vars][q_type]:
                            ans[density][amount_vars][q_type][algo] = {}
                        ans[density][amount_vars][q_type][algo][dcop_id] = x_dcop
    return ans

def create_xdcop():


    dcops_for_different_configs = get_dcops_for_different_configs()
    x_dcop_to_re_organize = get_x_dcops_dict(dcops_for_different_configs)
    x_dcop = get_organized_dcop(x_dcop_to_re_organize)



    return x_dcop





if __name__ == '__main__':
    #####--------------------------------
    is_privacy = False
    scale_type = ScaleType.dcop_scale
    dcop_type = DcopType.random_uniform
    if dcop_type == DcopType.random_uniform:
        p1s = [0.2]
    if dcop_type == DcopType.graph_coloring:
        p1s = [0.1]
    if dcop_type == DcopType.meeting_scheduling_v2:
        p1s = [0.5]

    repetitions = 100
    if scale_type ==ScaleType.dcop_scale:

        agents_amounts = [10,20,30,40,50]
        if is_privacy:
            algos = [Algorithm.One_Opt]
        else:
            algos = [Algorithm.BNB_Complete,Algorithm.One_Opt,Algorithm.Two_Opt,Algorithm.Three_Opt]#,Algorithm.Two_Opt,Algorithm.Three_Opt,Algorithm.Four_Opt,Algorithm.Five_Opt]#, Algorithm.One_Opt]
    else:
        if is_privacy:
            agents_amounts = [50]
            algos = [Algorithm.One_Opt]

        else:


            if dcop_type == DcopType.random_uniform and 0.7 in p1s:
                agents_amounts = [10]
            if dcop_type == DcopType.random_uniform and 0.2 in p1s:
                agents_amounts = [10]
            if dcop_type == DcopType.meeting_scheduling_v2 :
                agents_amounts = [10]
            if dcop_type == DcopType.graph_coloring:
                agents_amounts = [20,15,10,5]
            if is_privacy:
                algos = [Algorithm.One_Opt]

            algos = [Algorithm.BNB_Complete]#, Algorithm.Two_Opt, Algorithm.Three_Opt,
                     #Algorithm.Four_Opt, Algorithm.Five_Opt]  #
    #algos = [Algorithm.BNB_Complete,Algorithm.Three_Opt, Algorithm.One_Opt, Algorithm.Two_Opt,Algorithm.Four_Opt]# ,Algorithm.Four_Opt,Algorithm.Five_Opt, [Algorithm.Three_Opt,Algorithm.One_Opt, Algorithm.BNB_Complete]
    dcops = create_dcops()
    #with open("test_k_opt.pkl", "wb") as file:
    #    pickle.dump(dcops, file)
    seeds_xdcop = [1]
    min_vars = 1
    #max_vars_below_eq_10 = 5
    if is_privacy:
        vars_DCOP_scale = [5, 10]
        query_types_list = [QueryType.educated, QueryType.semi_educated]  # [QueryType.rnd,QueryType.educated]
    else:
        vars_DCOP_scale = [5, 10]
        query_types_list =  [QueryType.educated,QueryType.semi_educated]


    xdcops = create_xdcop()

    if is_privacy:
        with open("xdcops_"+dcop_type.name+"_A_"+str(agents_amounts)+"_p1_"+str(p1s)+"_"+scale_type.name+"_privacy.pkl", "wb") as file:pickle.dump(xdcops, file)

    else:
        with open("xdcops_"+dcop_type.name+"_A_"+str(agents_amounts)+"_p1_"+str(p1s)+"_"+scale_type.name+".pkl", "wb") as file:pickle.dump(xdcops, file)

