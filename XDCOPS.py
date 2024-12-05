import copy
import random
from collections import defaultdict
from itertools import product

from problems import DCOP, Constraint


class Query:
    def __init__(self,id_,dcop_id,agent,variables_in_query,solution_complete_assignment,alternative_values,solution_partial_assignment ):
        self.id_number = id_
        self.id_str= "dcop:"+str(dcop_id)+",seed:"+str(self.id_number)
        self.agent = agent
        self.variables_in_query = variables_in_query
        self.solution_complete_assignment = solution_complete_assignment
        self.solution_partial_assignment = solution_partial_assignment
        self.alternative_values = alternative_values
        self.alternative_partial_assignments = self.get_alternative_values_combinations(alternative_values)


    def get_alternative_values_combinations(self, alternative_values):
        keys = list(alternative_values.keys())
        values = list(alternative_values.values())
        combinations = list(product(*values))  # Use product to generate combinations
        # Create list of dictionaries for each combination
        return [dict(zip(keys, combination)) for combination in combinations]

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
        self.alternative_values = self.get_alternative_values()

    def get_query(self):
        return Query( id_=self.id_,dcop_id=self.dcop.dcop_id,agent=self.agent, variables_in_query=self.variables_dict, solution_complete_assignment=self.complete_assignment,
            alternative_values = self.alternative_values, solution_partial_assignment=self.solution_partial_assignment)

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




class ConstraintCollection():
    def __init__ (self,solution_partial_assignment,alternative_partial_assignment,complete_assignment,agent_dict):
        self.solution_partial_assignment = solution_partial_assignment
        self.solution_complete_assignment = complete_assignment
        self.alternative_partial_assignment = alternative_partial_assignment
        self.agent_dict = agent_dict


        self.alternative_constraints_dict = self.get_constraints_variable_dict(is_alternative = True)
        self.alternative_unique_constraints = self.get_unique_constraints(is_alternative = True)


        self.alternative_unique_constraints_cost = 0
        for auc in self.alternative_unique_constraints:self.alternative_unique_constraints_cost+=auc.cost

        self.solution_constraints_dict = self.get_constraints_variable_dict(is_alternative = False)
        self.solution_unique_constraints = self.get_unique_constraints(is_alternative = False)

        self.solution_unique_constraints_cost = 0
        for auc in self.solution_unique_constraints: self.solution_unique_constraints_cost += auc.cost


    def get_constraints_variable_dict(self,is_alternative = True):
        ans = {}
        if is_alternative:
            complete_assignment = self.get_alternative_complete_assignment()
        else:
            complete_assignment = copy.deepcopy(self.solution_complete_assignment)
        for variable in self.alternative_partial_assignment.keys():
            ans[variable] = self.get_all_constraints(variable,complete_assignment)
        return ans


    def get_alternative_complete_assignment(self):
        ans = copy.deepcopy(self.solution_complete_assignment)
        others_in_alternatives = copy.deepcopy(self.alternative_partial_assignment)
        for variable, value in others_in_alternatives.items():
            ans[variable] = value
        return ans

    def get_all_constraints(self, agent_variable, alternative_complete_assignment):
        list_of_constraints = []
        agent_obj=self.agent_dict[agent_variable]
        neighbors_obj_dict = agent_obj.neighbors_obj_dict

        agent_value = alternative_complete_assignment[agent_variable]
        for n_variable, n_obj in neighbors_obj_dict.items():
            n_value = alternative_complete_assignment[n_variable]
            ap,cost = n_obj.get_ap_and_cost(agent_variable,agent_value,n_variable,n_value)
            constraint = Constraint(ap,cost)
            list_of_constraints.append(constraint)

        return list_of_constraints

    def get_unique_constraints(self,is_alternative ):
        combined = []
        constraint_dict = None
        if is_alternative:
            constraint_dict = self.alternative_constraints_dict
        else:
            constraint_dict = self.solution_constraints_dict

        for list in constraint_dict.values():
            combined = combined + list

        # Use a set to remove duplicates based on the __eq__ method
        unique_constraints = []
        for constraint in combined:
            if constraint not in unique_constraints:
                unique_constraints.append(constraint)
        return unique_constraints

    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return str(self.alternative_partial_assignment)


class Explanation():
    def __init__(self, query):
        self.query = query
        self.constraints_collections = self.collect_constraints()
        self.cum_delta_from_solution_dict,self.sum_of_alternative_cost_dict = self.get_cumulative_delta_from_solution_dict()

        self.min_constraint_collection = min(self.constraints_collections,key=lambda x: x.alternative_unique_constraints_cost)
        self.min_cum_delta_from_solution = self.cum_delta_from_solution_dict[self.min_constraint_collection]

    def collect_constraints(self):
        ans = []
        agent_dict = self.query.variables_in_query
        alternative_partial_assignments = self.query.alternative_partial_assignments
        for aps in alternative_partial_assignments:

            ans.append(ConstraintCollection(solution_partial_assignment = self.query.solution_partial_assignment,
                                            alternative_partial_assignment=aps,
                                            complete_assignment = self.query.solution_complete_assignment, agent_dict =agent_dict))
        return ans

    def get_cumulative_delta_from_solution_dict(self):

        solution_unique_sum_cost = sum(constraint.cost for constraint in self.constraints_collections[0].solution_unique_constraints)

        cum_delta_from_solution_dict = {}
        sum_of_alternative_cost_dict = {}
        for auc in self.constraints_collections:
            cum_delta_from_solution_dict[auc] = {}
            sum_of_alternative_cost_dict[auc] = {}
            sorted_unique_alternative_constraints = sorted(auc.alternative_unique_constraints, key=lambda x: x.cost, reverse=True)
            sum_of_alternative_cost = 0
            for constraint in sorted_unique_alternative_constraints:
                sum_of_alternative_cost = sum_of_alternative_cost + constraint.cost
                delta = (sum_of_alternative_cost - solution_unique_sum_cost)
                cum_delta_from_solution_dict[auc][constraint] = delta
                sum_of_alternative_cost_dict[auc][constraint]=sum_of_alternative_cost
        return cum_delta_from_solution_dict,sum_of_alternative_cost_dict


class XDCOP:
    def __init__(self,dcop,query):
        self.dcop = dcop
        self.query = query
        self.explanation = Explanation(query)



