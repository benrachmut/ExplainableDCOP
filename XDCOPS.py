import random
from collections import defaultdict

from problems import DCOP





class QueryGenerator:
    def __init__(self,dcop:DCOP,seed,num_variables,num_values,with_connectivity_constraint):
        self.rnd = random.Random(seed*17)
        self.dcop = dcop
        self.complete_assignment = self.dcop.get_complete_assignment()

        self.num_variables = num_variables
        self.agent = self.dcop.select_random_agent(self.rnd)
        self.with_connectivity_constraint =with_connectivity_constraint
        self.variables_dict = self.get_variables()
        self.solution_partial_assignment = self.get_solution_partial_assignment()

        self.num_values = num_values
        alternative_values = self.get_alternative_values()






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
        ans[self.agent.id_] =self.agent
        current_agent = self.agent
        current_num_variables =  self.num_variables-1
        if self.num_variables - 1 > 0:
            if self.with_connectivity_constraint:
                for _ in range(current_num_variables):
                    rnd_n_id = self.get_random_neighbor_id_from_list(ans)
                    if rnd_n_id is None:
                        break
                    ans[rnd_n_id] =self.dcop.agents_dict[rnd_n_id]
            else:
                other_agents = self.dcop.get_random_agents(rnd = self.rnd,without = self.agent, amount_of_variables=self.num_variables-1)
                for agent in other_agents:
                    ans[agent.id_] = agent

    def get_solution_partial_assignment(self):
        ans = {}
        for variable in self.variables_dict.keys():
            self.ans[variable] = self.complete_assignment[variable]
        return ans

    def get_alternative_values(self):
        alternative_values = defaultdict(list)
        for agent_id, agent in self.variables_dict.items():
            solution_value = self.complete_assignment[agent_id]
            agent_domain = agent.domain.remove(solution_value)
            selected_alternatives = self.rnd.sample(agent_domain, self.num_values)
            alternative_values[agent_id] = selected_alternatives


class Query:
    def __init__(self,agent,variables_in_query,complete_assignment,alternative_partial_assignment,solution_partial_assignment ):
        self.agent = agent
        self.variables_in_query = variables_in_query
        self.complete_assignment = complete_assignment
        self.alternative_partial_assignment = alternative_partial_assignment
        self.solution_partial_assignment = solution_partial_assignment

    def create_solution_partial_assignment(self):
        ans = {}
        for variable in self.variables_in_query:
            ans[variable]= self.complete_assignment[variable]
        return ans


#class XDCOP:
#    def __init__(self,dcop):
#        self.dcop = dcop
#        self.query = self.create_query()
#        self.explanation = self.create_explanation()