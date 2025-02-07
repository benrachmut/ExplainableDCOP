from Globals_ import max_iteration_k


class Group():
    def __init__(self, agents):
        self.agents = agents
        self.neighbors_of_agents = self.get_neighbors_get_neighbors_of_agents()
        self.LR = None
        self.LR_of_neighbors_dict = None

class K_Opt:
    def __init__(self, agents , K):
        self.K = K
        self.iteration = 0

        self.max_iteration = max_iteration_k
        self.agents = agents
        self.solve()

    def solve(self):
        global_cost = self.calculate_global_cost()
        while self.is_converge() == False and self.iteration<self.max_iteration:
            groups = self.create_groups_of_k()
            self.calculate_LR_per_group(groups)
            self.group_change_if_can

            self.iteration = self.iteration+1
