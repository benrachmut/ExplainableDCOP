import pickle

import Algorithm_BnB
from XDCOPS import QueryGenerator, XDCOP, QueryGeneratorScheduling
from enums import *
from Globals_ import *
from problems import *


def get_DCOP(i,algorithm,dcop_type,A):
    if dcop_type == DcopType.sparse_random_uniform:
        return DCOP_RandomUniform(i, A, sparse_D, "Sparse Uniform", algorithm,sparse_p1)
    if dcop_type == DcopType.dense_random_uniform:
        return DCOP_RandomUniform(i, A, dense_D, "Dense Uniform", algorithm,dense_p1)
    if dcop_type == DcopType.graph_coloring:
        return DCOP_GraphColoring(i, A,graph_coloring_D, "Graph Coloring", algorithm)

    if  dcop_type == DcopType.meeting_scheduling_v2:
        return DCOP_MeetingSchedualingV2(id_=i, A=A, dcop_name="Meeting Scheduling",
                                       algorithm=algorithm)

    #if dcop_type == DcopType.meeting_scheduling :
    #    return DCOP_MeetingSchedualing(id_=i, A=A, meetings=meetings, meetings_per_agent=meetings_per_user,
    #                                   time_slots_D=time_slots_D, dcop_name="Meeting Scheduling",
    #                                   algorithm = algorithm)


def create_dcops():
    ans = {}
    for A in agents_amounts:
        ans[A] = {}
        for algo in algos:
            ans[A][algo.name] = []
            if not (algo == Algorithm.bnb and A>10):
                for i in range(repetitions):
                    dcop = get_DCOP(i, algo, dcop_type, A)
                    print("start:",i, dcop.create_summary())
                    if algo == Algorithm.bnb:
                        dcop.execute_center()
                    else:
                        dcop.execute_distributed()
            ans[A][algo.name].append(dcop)
    return ans





def create_x_standard_dcop(dcop, seed_query, num_variables, num_values,with_connectivity_constraint,query_type):
    query = QueryGenerator(dcop, seed_query, num_variables, num_values, with_connectivity_constraint,query_type).get_query()
    query.query_type = query_type

    return XDCOP(dcop, query)

def create_x_MeetingSchedualing_dcop(dcop, seed_query, num_meeting, num_alternative_slot,with_connectivity_constraint,query_type):
    qg = QueryGeneratorScheduling(dcop, seed_query, num_meeting, num_alternative_slot, with_connectivity_constraint,query_type)
    query =qg.get_query()
    query.query_type = query_type
    return XDCOP(dcop, query)






if __name__ == '__main__':
    #####--------------------------------

    dcop_type = DcopType.meeting_scheduling_v2

    repetitions = 100
    agents_amounts = [5,10,15,20,25,30,35,40,45,50]
    algos = [Algorithm.mgm,Algorithm.bnb]
    dcops = create_dcops()


    with open( dcop_type.name+".pkl", "wb") as file:
        pickle.dump(dcops, file)


    #####--------------------------------


    #query_type = QueryType.educated
    #with_connectivity_constraint = True
    #seeds_xdcop = [1]  # range(0, 2)
    #nums_variables = [8]  # [1, 5, 9]  # range(2, A)
    #nums_values = [1]  # [1,2,3,4,5]#[1,5,9]  # range(1, max_domain-1)
    #num_meetings = [2, 3]
    #num_alternative_slots = [1]
