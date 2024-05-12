
class SingleInformation:
    def __init__(self,context:{},constraints:{}):
        self.context = context
        self.constraints = constraints
        self.cost = 0
        self.update_total_cost()


    def __lt__(self, other):
        if self.cost <other.cost:
            return True
        else:
            return False

    def update_total_cost(self):
        ans = 0
        for dict_ in self.constraints.values():
            for cost in dict_.values():
                ans = ans + cost
        self.cost = ans

    def update_constraints(self,id_,constraints):
        self.constraints[id_] = constraints
        self.update_total_cost()

    def update_context(self,id_, variable):
        self.context[id_] = variable

    def __str__(self):
        return str(self.constraints)

    def __deepcopy__(self, memodict={}):
        context_input = {}
        for k,v in self.context.items():
            context_input[k] = v

        constraints_input = {}
        for k,v in self.constraints.items():
            t_dict = {}
            for ap,c in v.items():
                t_dict[ap] = c
            constraints_input[k] = t_dict


        return SingleInformation(context_input,constraints_input)




class PruneExplanation:
    def __init__(self,winner,loser,text):
        self.winner = winner
        self.loser = loser
        self.text = text
        self.disjoint = self.get_disjoint_constraints()