import copy
import random
from collections import defaultdict
from itertools import product

from problems import DCOP







class Query:
    def __init__(self,id_,dcop_id,agent,variables_in_query,complete_assignment,alternative_partial_assignment,solution_partial_assignment ):
        self.id_number = id_
        self.id_str= "dcop:"+str(dcop_id)+",seed:"+str(self.id_number)
        self.agent = agent
        self.variables_in_query = variables_in_query
        self.complete_assignment = complete_assignment
        self.alternative_partial_assignments = alternative_partial_assignment
        self.solution_partial_assignment = solution_partial_assignment

    def create_solution_partial_assignment(self):
        ans = {}
        for variable in self.variables_in_query:
            ans[variable]= self.complete_assignment[variable]
        return ans

    def print_representation(self):
        ans = "+++" + self.id_str + "++++\n"
        for alt in self.alternative_partial_assignments:
            ans = ans + "<" + str(self.solution_partial_assignment) + "," + str(alt) + ">\n"
        return ans
    def __str__(self):
        return self.id_


class QueryGenerator:
    def __init__(self, dcop: DCOP, seed, num_variables, num_values, with_connectivity_constraint):
        self.id_ = seed
        self.seed_ = (1+seed)*17+(1+dcop.dcop_id)*18
        self.rnd = random.Random(self.seed_ )
        self.rnd.randint(1,100)
        self.dcop = dcop
        self.complete_assignment = self.dcop.get_complete_assignment()

        self.num_variables = num_variables
        for _ in range(10):
            self.agent = self.rnd.choice(self.dcop.agents)
        self.with_connectivity_constraint = with_connectivity_constraint
        self.variables_dict = self.get_variables()
        self.solution_partial_assignment = self.get_solution_partial_assignment()

        self.num_values = num_values
        alternative_values = self.get_alternative_values()
        self.alternative_values_combinations = self.get_alternative_values_combinations(alternative_values)

    def get_query(self):
        return Query( id_=self.id_,dcop_id=self.dcop.dcop_id,agent=self.agent, variables_in_query=self.variables_dict, complete_assignment=self.complete_assignment,
            alternative_partial_assignment=self.alternative_values_combinations, solution_partial_assignment=self.solution_partial_assignment)

    def get_random_neighbor_id_from_list(self, agent_dict):
        neighbors_set = set()
        for agent in agent_dict.values():
            neighbors_set.update(agent.neighbors_agents_id)
        neighbors_set = neighbors_set - set(agent_dict.keys())
        neighbors_list = list(neighbors_set)
        try:
            rnd_neighbor = self.rnd.choice(neighbors_list)
        except:
            rnd_neighbor = None
        return rnd_neighbor

    def get_variables(self):
        ans = {}
        ans[self.agent.id_] = self.agent
        current_num_variables = self.num_variables - 1
        if self.num_variables - 1 > 0:
            if self.with_connectivity_constraint:
                for _ in range(current_num_variables):
                    rnd_n_id = self.get_random_neighbor_id_from_list(ans)
                    if rnd_n_id is None:
                        break
                    ans[rnd_n_id] = self.dcop.agents_dict[rnd_n_id]
            else:
                other_agents = self.dcop.get_random_agents(rnd=self.rnd, without=self.agent,
                                                           amount_of_variables=self.num_variables - 1)
                for agent in other_agents:
                    ans[agent.id_] = agent
        return ans

    def get_solution_partial_assignment(self):
        ans = {}
        for variable in self.variables_dict.keys():
            ans[variable] = self.complete_assignment[variable]
        return ans

    def get_alternative_values(self):
        alternative_values = defaultdict(list)
        for agent_id, agent in self.variables_dict.items():
            solution_value = self.complete_assignment[agent_id]
            agent_domain = copy.deepcopy(agent.domain)
            agent_domain.remove(solution_value)
            selected_alternatives = self.rnd.sample(agent_domain, self.num_values)
            alternative_values[agent_id] = selected_alternatives
        return alternative_values

    def get_alternative_values_combinations(self, alternative_values):
        keys = list(alternative_values.keys())
        values = list(alternative_values.values())
        combinations = list(product(*values))  # Use product to generate combinations

        # Create list of dictionaries for each combination
        return [dict(zip(keys, combination)) for combination in combinations]

class XDCOP:
    def __init__(self,dcop,query):
        self.dcop = dcop
        self.query = query
        self.explanation = self.create_explanation()