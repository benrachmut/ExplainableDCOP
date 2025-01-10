import pickle

import Algorithm_BnB
from XDCOPS import QueryGenerator, XDCOP, QueryGeneratorScheduling
from enums import *
from Globals_ import *
from problems import *


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
        return DCOP_RandomUniform(i, A, sparse_D,density_type_str+"_Sparse Uniform", algorithm,p1)

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










if __name__ == '__main__':
    #####--------------------------------

    dcop_type = DcopType.meeting_scheduling_v2
    p1s = [0.2,0.5,0.7]
    repetitions = 100
    agents_amounts = [5,10,15,20,25,30,35,40,45,50]
    algos = [Algorithm.mgm,Algorithm.bnb]
    dcops = create_dcops()


    with open( "dcops_"+dcop_type.name+".pkl", "wb") as file:
        pickle.dump(dcops, file)


    #####--------------------------------


    #query_type = QueryType.educated
    #with_connectivity_constraint = True
    #seeds_xdcop = [1]  # range(0, 2)
    #nums_variables = [8]  # [1, 5, 9]  # range(2, A)
    #nums_values = [1]  # [1,2,3,4,5]#[1,5,9]  # range(1, max_domain-1)
    #num_meetings = [2, 3]
    #num_alternative_slots = [1]
