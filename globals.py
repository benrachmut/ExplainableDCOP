from enums import *
from random import Random


dcop_type = DcopType.sparse_random_uniform
algorithm = Algorithm.branch_and_bound_by_index


is_complete = None
repetitions = 1
incomplete_iterations = 1000


#### DCOPS_INPUT ####
A=None
D=None
is_neighbor_function = None
cost_generator_function = None
cost_matrix_function = None


# dcop_type = DcopType.sparse_random_uniform
sparse_p1 = 0.2
sparse_p2 = 1
sparse_min_cost = 1
sparse_max_cost = 100

def sparse_random_uniform_cost_function(rnd_cost:Random):
    if rnd_cost.random()<sparse_p2:
        return rnd_cost.randint(sparse_min_cost, sparse_max_cost)
    else:
        return 0

def sparse_random_is_neighbor_function(rnd_:Random):
    if rnd_.random()< sparse_p1 :
        return True
    return False


# dcop_type = DcopType.dense_random_uniform
dense_p1 = 0.7
dense_p2 = 1
dense_min_cost = 1
dense_max_cost = 100

def dense_random_uniform_cost_function(rnd_cost:Random):
    if rnd_cost.random()<dense_p2:
        return rnd_cost.randint(dense_min_cost, dense_max_cost)
    else:
        return 0

def dense_random_is_neighbor_function(rnd_: Random):
    if rnd_.random() < dense_p1:
        return True
    return False



# dcop_type = DcopType.scale_free_network
scale_free_hubs = 10
scale_others_number_of_neighbors = 3
scale_min_cost = 1
scale_max_cost = 100

def scale_free_network_cost_function(rnd_cost:Random):
    #TODO
    raise Exception("TODO scale_free_network_cost_function")

def scale_free_network_is_neighbor_function(rnd_: Random):
    #TODO
    raise Exception("TODO scale_free_network_is_neighbor_function")

# dcop_type = DcopType.graph_coloring
graph_coloring_p1 = 0.05
graph_coloring_constant_cost = 10

def graph_coloring_function(d1,d2):
    if d1==d2:
        return graph_coloring_constant_cost
    else:
        return 0

def graph_coloring_is_neighbor_function(rnd_:Random):
    if rnd_.random()<0.05:
        return True
    return False

# dcop_type = DcopType.meeting_scheduling
meeting_schedual_meet_amount = 20







######## dcop input ########

def given_dcop_create_input():
    if dcop_type == DcopType.sparse_random_uniform:
        global A, D, is_neighbor_function,cost_generator_function, cost_matrix_function
        A = 50
        D = 10
        is_neighbor_function = sparse_random_is_neighbor_function
        cost_generator_function = sparse_random_uniform_cost_function
        cost_matrix_function = TODO

    if dcop_type == DcopType.dense_random_uniform:
        global A, D, is_neighbor_function,cost_generator_function, cost_matrix_function
        A = 50
        D = 10
        is_neighbor_function = dense_random_is_neighbor_function
        cost_generator_function = dense_random_uniform_cost_function
        cost_matrix_function = TODO


    if dcop_type == DcopType.graph_coloring:
        global A, D, is_neighbor_function,cost_generator_function, cost_matrix_function
        A = 50
        D = 3
        is_neighbor_function = graph_coloring_is_neighbor_function
        cost_generator_function = graph_coloring_function
        cost_matrix_function = TODO

    if dcop_type == DcopType.scale_free_network:
        global A, D, is_neighbor_function,cost_generator_function, cost_matrix_function
        A = 50
        D = 10
        is_neighbor_function = scale_free_network_is_neighbor_function
        cost_generator_function = scale_free_network_cost_function
        cost_matrix_function = TODO



    if dcop_type == DcopType.meeting_scheduling:
        global A, D, is_neighbor_function,cost_generator_function, cost_matrix_function
        A = 90
        D = 2
        is_neighbor_function = TODO
        cost_generator_function = TODO
        cost_matrix_function = TODO

        raise Exception("I did not meeting scheduling yet")

