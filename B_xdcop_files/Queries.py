import copy
from collections import defaultdict
from itertools import product
from A_dcop_files.Algorithm_BnB_Central import Bnb_central
from Globals_ import *
from enums import *


class Query:
    def __init__(self,id_,dcop_id,agent,variables_in_query,solution_complete_assignment,alternative_values,solution_partial_assignment ):
        self.id_number = id_
        self.id_str= "dcop:"+str(dcop_id)+",seed:"+str(self.id_number)
        self.agent = agent
        self.variables_in_query = variables_in_query
        self.solution_complete_assignment = solution_complete_assignment
        self.solution_partial_assignment = solution_partial_assignment
        self.alternative_values = alternative_values
        #self.alternative_partial_assignments = self.get_alternative_values_combinations(alternative_values)


    def get_alternative_values_combinations(self, alternative_values):
        keys = list(alternative_values.keys())
        values = [list(alternative_values.values())]
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

class AgentForEducatedQuery():
    def __init__(self,id_,domain_list,neighbors_obj,neighbors_obj_dict,neighbors_agents_id,unary_constraint):
        self.variable = None
        self.id_ = id_
        self.domain = domain_list

        self.neighbors_obj = neighbors_obj
        self.neighbors_obj_dict = neighbors_obj_dict  # id, obj
        self.neighbors_agents_id = neighbors_agents_id

        self.unary_constraint = unary_constraint


class QueryMeetingScheduling(Query):
    def __init__(self, id_, dcop_id, agent, variables_in_query, solution_complete_assignment, alternative_values,
                 solution_partial_assignment,meetings_per_agent_dict ,
                                           agents_assigned_to_meetings_dict ):
        Query.__init__(self, id_, dcop_id, agent, variables_in_query, solution_complete_assignment, alternative_values,
                       solution_partial_assignment)
        self.meetings_per_agent_dict = meetings_per_agent_dict
        self.agents_assigned_to_meetings_dict = agents_assigned_to_meetings_dict

        self.solution_complete_assignment = self.fix_partial_assignment(self.solution_complete_assignment)
        self.solution_partial_assignment = self.fix_partial_assignment(self.solution_partial_assignment)
        self.alternative_partial_assignments = self.fix_alternative_partial_assignment()
        self.variables_in_query = self.fix_variables_in_query()

        #self.solution_partial_assignment = solution_partial_assignment
        #self.alternative_values = alternative_values
        #self.alternative_partial_assignments = self.get_alternative_values_combinations(alternative_values)

    def fix_partial_assignment(self, dict_):
        ans = {}
        old_format = dict_

        for meeting_id,time_slot  in old_format.items():
            meeting_agents = self.agents_assigned_to_meetings_dict[meeting_id]
            for meeting_agent in meeting_agents:
                ans[meeting_agent.id_] = time_slot
        return ans

    def fix_alternative_partial_assignment(self):
        ans = []
        for pa in self.alternative_partial_assignments:
            updated_dict = self.fix_partial_assignment(pa)
            ans.append(updated_dict)
        return ans

    def fix_variables_in_query(self):
        ans = {}
        for meeting_id, meeting_agents in self.variables_in_query.items():
            for meeting_agent in meeting_agents:
                ans[meeting_agent.id_]=meeting_agent
        return ans

class QueryGenerator:
    def __init__(self, dcops_dict, amount_of_vars, query_type, with_connectivity_constraint=True):
        self.dcops_dict = dcops_dict
        self.first_dcop = list(dcops_dict.values())[0]
        first_id = self.first_dcop.dcop_id
        if not all(dcop.dcop_id == first_id for dcop in list(dcops_dict.values())):
            raise Exception("all dcops must have the same id_")
        self.id_ = first_id

        self.seed_ = 17+(1+self.id_)*18
        self.rnd = random.Random(self.seed_ )
        for _ in range(5): self.rnd.randint(1,100)
        #self.dcop = dcop
        self.query_type = query_type
        self.complete_assignments_dict = {}
        for k,dcop in self.dcops_dict.items():
            self.complete_assignments_dict[k]=dcop.get_complete_assignment()
        self.num_variables = amount_of_vars
        for _ in range(10):a_q_id = self.rnd.choice( list(self.dcops_dict.values())[0].agents).id_
        self.a_q_dict = {}
        for algo,dcop in self.dcops_dict.items():
            self.a_q_dict[algo] = dcop.agents_dict[a_q_id]
        self.with_connectivity_constraint = with_connectivity_constraint
        self.variables_dict = self.get_variables()
        self.solution_partial_assignment_dict = self.get_solution_partial_assignment_dict()
        self.alternative_values = self.get_alternative_values()

    def get_query(self,algo,dcop_id):
        return Query( id_=self.id_,dcop_id=dcop_id,agent=self.a_q_dict[algo], variables_in_query=self.variables_dict[algo], solution_complete_assignment=self.complete_assignments_dict[algo],
            alternative_values = self.alternative_values[algo], solution_partial_assignment=self.solution_partial_assignment_dict[algo])

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
        for algo in self.a_q_dict.keys():
            a_q = self.a_q_dict[algo]
            ans[algo] = {a_q.id_:a_q}
        current_num_variables = self.num_variables - 1
        flag = False
        if self.with_connectivity_constraint:
            for _ in range(current_num_variables):
                rnd_n_id = self.get_random_neighbor_id_from_list(ans[algo])
                if rnd_n_id is None:
                    flag = True
                    ans = {}
                    for algo, a_q in self.a_q_dict.items():
                        ans[algo] = {a_q.id_: a_q}
                    break
                for algo, dcop in self.dcops_dict.items():
                    agent = dcop.agents_dict[rnd_n_id]
                    ans[algo][rnd_n_id] =agent

                if self.with_connectivity_constraint== False or flag:
                    for algo, a_q in self.a_q_dict.items():
                        other_agents = self.dcops_dict[algo].get_random_agents(rnd=self.rnd, without=a_q,
                                                                   amount_of_variables=self.num_variables - 1)
                        for agent in other_agents:
                            ans[algo][agent.id_] = self.dcops_dict[algo].agents_dict[agent.id_]

        return ans

    def get_solution_partial_assignment_dict(self):
        ans = {}
        for algo in self.dcops_dict.keys():
            ans[algo] = {}
            for variable in self.variables_dict[algo].keys():
                ans[algo][variable] = self.complete_assignments_dict[algo][variable]
        return ans

    def get_values_to_remove_dict(self, from_which_dict):
        ans = {}


        for dict_ in from_which_dict.values():
            for variable_num, value in dict_.items():
                if variable_num not in ans.keys():
                    ans[variable_num] = [value]
                elif value not in ans[variable_num]:
                    ans[variable_num].append(value)
        return  ans

    def get_possible_alternatives_dict(self,for_what_dict ):
        values_to_remove_dict = self.get_values_to_remove_dict(for_what_dict)

        domain_of_agents = list(self.dcops_dict.values())[0].agents[0].domain
        ans = {}
        for variable, values_to_remove_list in values_to_remove_dict.items():
            a = copy.deepcopy(domain_of_agents)
            b = values_to_remove_list
            possible_alternatives = [item for item in a if item not in b]
            ans[variable] = possible_alternatives

        return ans
    def get_alternative_values(self):
        ans = {}


        if self.query_type == QueryType.rnd:
            possible_alternatives_dict = self.get_possible_alternatives_dict(self.solution_partial_assignment_dict)
            pa_rnd = {}
            for agent_id, possible_alternatives in possible_alternatives_dict.items():
                selected_alternative = self.rnd.choice(possible_alternatives)
                pa_rnd[agent_id] = [selected_alternative]
            for algo in self.dcops_dict.keys():
                ans[algo] = copy.deepcopy(pa_rnd)


        if self.query_type == QueryType.educated or self.query_type == QueryType.semi_educated:
            possible_alternatives_dict = self.get_possible_alternatives_dict(self.complete_assignments_dict)

            agents_for_educated_dict = self.create_agents_for_educated(possible_alternatives_dict)
            for algo, agents_for_educated in agents_for_educated_dict.items():
                bnb = Bnb_central(agents_for_educated)

                dcop_solution = bnb.UB
                dict_ = dcop_solution[0]
                alternative_values = {}
                for a_id,val in dict_.items():
                    if a_id in self.variables_dict.keys():
                        alternative_values[a_id] = [val]
                ans[algo] = alternative_values
        return ans

    def get_agent_domain(self,domain_list,algo,solution_value,possible_alternatives_dict,id_):
        if id_ in self.variables_dict[algo].keys():
            if self.query_type == QueryType.educated:
                domain_list.remove(solution_value)
            if self.query_type == QueryType.semi_educated:
                domain_list = copy.deepcopy( possible_alternatives_dict[id_])

        else:
            if self.query_type == QueryType.educated:
                domain_list = copy.deepcopy([solution_value])
            else:
                ttt = []
                for d in domain_list:
                    if d not in possible_alternatives_dict[id_]:
                        ttt.append(d)
                domain_list = copy.deepcopy(ttt)
        return domain_list
    def create_agents_for_educated(self,possible_alternatives_dict):
        ans = {}
        for algo, dcop in self.dcops_dict.items():
            ans[algo] =[]
            for agent in dcop.agents:
                id_ = copy.deepcopy(agent.id_)
                solution_value = self.complete_assignments_dict[algo][id_]
                full_domain_list = copy.deepcopy(agent.domain)
                domain_list = self.get_agent_domain(full_domain_list,algo,solution_value,possible_alternatives_dict,id_)
                neighbors_obj = copy.deepcopy(agent.neighbors_obj)
                neighbors_obj_dict = copy.deepcopy(agent.neighbors_obj_dict)
                neighbors_agents_id = copy.deepcopy(agent.neighbors_agents_id)
                a = AgentForEducatedQuery(id_, domain_list, neighbors_obj, neighbors_obj_dict, neighbors_agents_id,
                                              None)
                ans[algo].append(a)

        return ans



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