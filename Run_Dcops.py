import pickle

from A_dcop_files.problems import *
from B_xdcop_files.Queries import QueryGenerator
from B_xdcop_files.XDCOPS import XDCOP


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
        return DCOP_RandomUniform(i, A, sparse_D,density_type_str+"_Random Uniform", algorithm,p1)

    if dcop_type == DcopType.graph_coloring:
        return DCOP_GraphColoring(i, A,graph_coloring_D, density_type_str+"_Graph Coloring", algorithm)

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
                if not (algo == Algorithm.bnb and A>10):
                    for i in range(repetitions):
                        dcop = get_DCOP(i, algo, dcop_type, A,p1)
                        print(algo.name,"start:",i, dcop.create_summary())
                        if algo == Algorithm.bnb:
                            dcop.execute_center()
                        else:
                            dcop.execute_distributed()
                        ans[p1][A][algo.name][i] = (dcop)

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


            for dcop_id in dict_2[algos_list[0]]:
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

                if agents_amount <= 10:

                    amount_of_variables_list = range(min_vars, min(max_vars_below_eq_10, agents_amount) + 1)
                else:
                    amount_of_variables_list = vars_above_10_list

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

    dcop_type = DcopType.meeting_scheduling_v2
    p1s = [0.7]#,0.5,0.2]
    repetitions = 3
    agents_amounts = [5]#[5,15,20,25,30,35,40,45,50] #+[10]
    algos = [Algorithm.mgm,Algorithm.bnb]
    dcops = create_dcops()

    seeds_xdcop = [1]
    min_vars = 1
    max_vars_below_eq_10 = 5
    vars_above_10_list = [1,5]

    query_types_list = list(QueryType)#[QueryType.semi_educated]#[QueryType.educated,QueryType.rnd]
    xdcops = create_xdcop()

    with open("xdcops_"+dcop_type.name+"_A_"+str(agents_amounts)+"_p1_"+str(p1s)+".pkl", "wb") as file:
        pickle.dump(xdcops, file)


