import pickle

from XDCOPS import QueryGenerator, XDCOP, QueryGeneratorScheduling
from enums import DcopType
from Globals_ import *
from problems import *


def get_DCOP(i,algorithm,dcop_type,A):
    if dcop_type == DcopType.sparse_random_uniform:
        return DCOP_RandomUniform(i, A, sparse_D, "Sparse Uniform", algorithm,sparse_p1)
    if dcop_type == DcopType.dense_random_uniform:
        return DCOP_RandomUniform(i, A, dense_D, "Dense Uniform", algorithm,dense_p1)
    if dcop_type == DcopType.graph_coloring:
        return DCOP_GraphColoring(i, A,graph_coloring_D, "Graph Coloring", algorithm)
    if dcop_type == DcopType.meeting_scheduling:
        return DCOP_MeetingSchedualing(id_=i, A=A, meetings=meetings, meetings_per_agent=meetings_per_agent,
                                        time_slots_D=time_slots_D, dcop_name="Meeting Scheduling",
                                       algorithm = algorithm)


def create_dcops():
    dcops_complete = []
    for i in range(repetitions):

        dcop = get_DCOP(i, algorithm, dcop_type, A)
        print("start:",i, dcop.create_summary())

        dcop.execute_center()
        dcops_complete.append(dcop)

        with open( dcop.create_summary()+".pkl", "wb") as file:
            pickle.dump(dcops_complete, file)
    return dcops_complete





def create_x_standard_dcop(dcop, seed_query, num_variables, num_values,with_connectivity_constraint,query_type):
    query = QueryGenerator(dcop, seed_query, num_variables, num_values, with_connectivity_constraint,query_type).get_query()
    query.query_type = query_type

    return XDCOP(dcop, query)

def create_x_MeetingSchedualing_dcop(dcop, seed_query, num_meeting, num_alternative_slot,with_connectivity_constraint,query_type):
    qg = QueryGeneratorScheduling(dcop, seed_query, num_meeting, num_alternative_slot, with_connectivity_constraint,query_type)
    query =qg.get_query()
    query.query_type = query_type
    return XDCOP(dcop, query)




def create_xdcop(nums_variables,nums_values):
    ans = {}
    for query_type in list(QueryType):
        for num_variables in nums_variables:
            for num_values in nums_values:
                ans[(query_type,num_variables)] = []

                for dcop in dcops:
                    print("dcop id:",dcop.dcop_id,(query_type,num_variables))
                    dcop.create_agent_dict()
                    for seed_ in seeds_xdcop:
                        if dcop_type == DcopType.meeting_scheduling:
                            xdcop = create_x_MeetingSchedualing_dcop(dcop, seed_ + 1, num_variables, num_values,
                                                                     with_connectivity_constraint, query_type)
                        else:
                            xdcop = create_x_standard_dcop(dcop, (seed_ + 1), num_variables, num_values,with_connectivity_constraint,query_type)
                        ans[(query_type,num_variables)].append(xdcop)

    return ans




def create_num_variables():
    if dcop_type == DcopType.meeting_scheduling:
        ans = range(1, meetings + 1)
    else:
        ans = range(1, A + 1)

    return ans


if __name__ == '__main__':
    #####--------------------------------


    dcop_type = DcopType.meeting_scheduling

    if dcop_type == DcopType.sparse_random_uniform or dcop_type == DcopType.dense_random_uniform:
        A = 10
    if dcop_type == DcopType.graph_coloring:
        A = 20
    if dcop_type == DcopType.meeting_scheduling:
        A = 8

    repetitions = 100

    dcops = create_dcops()
    #####--------------------------------
    seeds_xdcop=[1]
    nums_variables = create_num_variables()
    nums_values = [1]

    xdcops = create_xdcop(nums_variables,nums_values)
    with open("xdcops_"+dcops[0].create_summary() + ".pkl", "wb") as file:
        pickle.dump(xdcops, file)

    #query_type = QueryType.educated
    #with_connectivity_constraint = True
    #seeds_xdcop = [1]  # range(0, 2)
    #nums_variables = [8]  # [1, 5, 9]  # range(2, A)
    #nums_values = [1]  # [1,2,3,4,5]#[1,5,9]  # range(1, max_domain-1)
    #num_meetings = [2, 3]
    #num_alternative_slots = [1]
