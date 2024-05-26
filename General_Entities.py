class SingleInformation:
    def __init__(self, context: {}, constraints: {}):
        self.context = context
        self.constraints = constraints
        self.cost = 0
        self.update_total_cost()

    def __lt__(self, other):
        if self.cost < other.cost:
            return True
        else:
            return False


    def __add__(self, other):
        context = {}
        for id_,value in other.context.items(): context[id_]=value
        for id_,value in self.context.items(): context[id_]=value

        constraints = {}
        for id_,value in other.constraints.items(): constraints[id_] = value
        for id_,value in self.constraints.items(): constraints[id_] = value
        return SingleInformation(context=context, constraints=constraints)

    def reset_given_id(self, heights_to_include):
        context = {}
        for id_, val in self.context.items():
            if id_ in heights_to_include:
                context[id_] = val

        constraints = {}
        for id_, val in self.constraints.items():
            if id_ in heights_to_include:
                constraints[id_] = val

        return SingleInformation(context = context, constraints = constraints)



    def update_total_cost(self):
        ans = 0
        for dict_ in self.constraints.values():
            for cost in dict_.values():
                ans = ans + cost
        self.cost = ans

    def update_constraints(self, id_, constraints):
        self.constraints[id_] = constraints
        self.update_total_cost()

    def update_context(self, id_, variable):
        self.context[id_] = variable

    def __str__(self):
        return str(self.constraints)

    def __deepcopy__(self, memodict={}):
        context_input = {}
        for k, v in self.context.items():
            context_input[k] = v

        constraints_input = {}
        for k, v in self.constraints.items():
            t_dict = {}
            for ap, c in v.items():
                t_dict[ap] = c
            constraints_input[k] = t_dict

        return SingleInformation(context_input, constraints_input)

    def __hash__(self):
        context_items = frozenset(self.context.items())
        constraints_items = frozenset((k, frozenset(v.items())) for k, v in self.constraints.items())
        return hash((context_items, constraints_items))



class PruneExplanation:
    def __init__(self, winner: SingleInformation, loser: SingleInformation, text):
        self.winner = winner
        self.loser = loser
        self.text = text

        ########### constraints ###########
        self.joint_constraints = {}
        self.disjoint_winner_constraints = {}
        self.disjoint_loser_constraints = {}
        self.create_joint_and_disjoint_constraints()

        ########### costs ###########
        self.disjoint_winner_cost = sum(self.disjoint_winner_constraints.values())
        self.disjoint_loser_cost = sum(self.disjoint_loser_constraints.values())
        self.joint_cost = sum(self.joint_constraints.values())

    def create_joint_and_disjoint_constraints(self):
        self.check_if_in_winner_and_not_in_loser()
        self.check_if_in_loser_and_not_in_winner()

        winner_context = self.winner.context
        loser_context = self.loser.context

        in_winner_disjoint_agents, in_loser_disjoint_agents = self.get_disjoint_agents(winner_context, loser_context)
        ids_with_different_values = self.get_ids_with_different_values(winner_context, loser_context)
        ids_to_ignore = ids_with_different_values + in_winner_disjoint_agents + in_loser_disjoint_agents
        self.create_joint_constraints(ids_to_ignore)
        self.disjoint_loser_constraints = self.create_disjoint_constraints(ids_with_different_values, self.loser)
        self.disjoint_winner_constraints = self.create_disjoint_constraints(ids_with_different_values, self.winner)

    def check_if_in_loser_and_not_in_winner(self):
        winner_constraints = self.winner.constraints
        loser_constraints = self.loser.constraints
        for n_id, constraints_dict in loser_constraints.items():
            if n_id not in winner_constraints:
                for variables_tuple, cost in constraints_dict.items():
                    self.disjoint_winner_constraints[variables_tuple] = cost
                    self.disjoint_loser_constraints[variables_tuple] = cost

    def check_if_in_winner_and_not_in_loser(self):
        winner_constraints = self.winner.constraints
        loser_constraints = self.loser.constraints
        for n_id, constraints_dict in winner_constraints.items():
            if n_id not in loser_constraints:
                for variables_tuple, cost in constraints_dict.items():
                    self.disjoint_winner_constraints[variables_tuple] = cost
                    self.disjoint_loser_constraints[variables_tuple] = cost

    @staticmethod
    def get_ids_with_different_values(winner_context, loser_context):
        ans = []
        for id_, winner_value in winner_context.items():
            if id_ in loser_context.keys():
                loser_value = loser_context[id_]
                if winner_value != loser_value:
                    ans.append("A_" + str(id_))
        return ans

    def create_joint_constraints(self, ids_to_ignore):
        constraints_per_id = self.winner.constraints
        for constraints in constraints_per_id.values():
            for tuples_, cost in constraints.items():
                first_agent = tuples_[0][0]
                second_agent = tuples_[1][0]
                if first_agent not in ids_to_ignore and second_agent not in ids_to_ignore:
                    self.joint_constraints[tuples_] = cost

    @staticmethod
    def get_disjoint_agents(winner_context, loser_context):
        in_winner_disjoint_agents = []
        in_loser_disjoint_agents = []

        for id_ in winner_context.keys():
            if id_ not in loser_context.keys():
                in_winner_disjoint_agents.append("A_" + str(id_))

        for id_ in loser_context.keys():
            if id_ not in winner_context.keys():
                in_loser_disjoint_agents.append("A_" + str(id_))

        return in_winner_disjoint_agents, in_loser_disjoint_agents

    def create_disjoint_constraints(self, ids_with_different_values, single_info):
        ans = {}
        constraints_per_id = single_info.constraints
        for constraints in constraints_per_id.values():
            for tuples_, cost in constraints.items():
                first_agent = tuples_[0][0]
                second_agent = tuples_[1][0]
                if first_agent in ids_with_different_values or second_agent in ids_with_different_values:
                    ans[tuples_] = cost
        return ans
