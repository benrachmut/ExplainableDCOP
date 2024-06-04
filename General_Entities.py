class SingleInformation:
    def __init__(self, context: {}, constraints: {}):
        self.context = context
        self.constraints = constraints
        self.constraints_readable = self.get_constraints_readable()
        self.cost = 0
        self.update_total_cost()

    def __lt__(self, other):
        if self.cost < other.cost:
            return True
        else:
            return False

    def get_context_anytime(self,neighbors):
        ans = {}
        for id_, value in self.context.items():
            if id_ in neighbors:
                ans[id_] = value
        return ans

    def get_constraints_anytime(self,id_):
        ans = {}
        for constraint_tuple in self.constraints_readable:
            first_agent = constraint_tuple[0]
            second_agent = constraint_tuple[1]
            cost = constraint_tuple[2]
            if first_agent == id_:
               ans[second_agent] = cost
            if second_agent == id_:
               ans[first_agent] = cost
        return ans

    def get_anytime_info (self,id_, neighbors):
        variable_anytime = self.context[id_]
        context_anytime = self.get_context_anytime(neighbors)
        constraints_anytime = self.get_constraints_anytime(id_)
        return variable_anytime,context_anytime,constraints_anytime


    @staticmethod
    def convert_str_A_number(input_str):
        _, number_str = input_str.split('_')
        # Convert the part after the underscore to an integer
        return int(number_str)

    def get_constraints_readable(self):
        ans = []
        for list_of_constraints in self.constraints.values():
            for context,cost in list_of_constraints.items():
                first_agent_num = self.convert_str_A_number(context[0][0])
                second_agent_num = self.convert_str_A_number(context[1][0])
                ans.append((first_agent_num,second_agent_num,cost))
        return ans

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

    def __eq__(self, other):
        dict1 = self.context
        dict2 = other.context
        if not set(dict1.keys()) == set(dict2.keys()):
            return False
        try:
            for k,v in self.context.items():
                if v != other.context[k]:
                    return False
            return True
        except:
            return False





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
        return str(self.context)

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
    def __init__(self, winner: SingleInformation, loser: SingleInformation, text, agent_id,local_clock,global_clock):
        self.winner = winner
        self.loser = loser
        self.text = text
        self.agent_id = agent_id
        self.local_clock =local_clock
        self.global_clock = global_clock

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

    def get_explanation_as_dict(self):
        ans = {}
        ans["text"] = self.text
        ans["winner_constraints"] = str(self.winner.constraints)
        ans["winner_context"] = str(self.winner.context)
        ans["loser_constraints"] = str(self.loser.constraints)
        ans["loser_context"] = str(self.loser.context)
        ans["joint_constraints"] = str(self.joint_constraints)
        ans["joint_cost"] = str(self.joint_cost)
        ans["disjoint_loser_constraints"] = str(self.disjoint_loser_constraints)
        ans["disjoint_loser_cost"] = str(self.disjoint_loser_cost)
        ans["disjoint_winner_constraints"] = str(self.disjoint_winner_constraints)
        ans["disjoint_winner_cost"] = str(self.disjoint_winner_cost)
        ans["local_clock"] = str(self.local_clock)
        ans["global_clock"] = str(self.global_clock)
        ans["agent_id"] = str(self.agent_id)
        return ans



    @staticmethod
    def get_explanation_headers_as_list(self):
        return ["text", "winner_constraints", "winner_context", "loser_constraints", "loser_context", "joint_constraints", "joint_cost"
            , "disjoint_loser_constraints", "disjoint_loser_cost", "disjoint_winner_constraints", "disjoint_winner_cost"]
