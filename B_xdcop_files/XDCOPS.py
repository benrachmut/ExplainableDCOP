from B_xdcop_files.Agents_X import *
from B_xdcop_files.Queries import *
from Globals_ import *



class Explanation():
    def __init__(self, dcop,query,explanation_type ):
        self.query = query
        self.explanation_type = explanation_type
        self.iteration = 0
        self.data_entry = {}
        #self.data_entry["dcop_id"] =  dcop.dcop_id
        #self.data_entry["dcop_type"] = dcop.dcop_name
        #self.data_entry["num_variables"] = len(query.variables_in_query)
        #self.data_entry["Explanation_Algorithm"]= explanation_type.name
        #self.data_entry["Query_Generator_Type"]= query.query_type.name

        #if explanation_type == ExplanationType.Centralized:
        #    self.get_centralized_explanation()

        #else:# explanation_type == ExplanationType.BroadcastNaive:
        self.query_agent,query_agent_id = self.create_query_x_agent(self.query.agent)
        self.x_agents = self.create_x_agents(dcop,query_agent_id) # all
        self.x_agents.append(self.query_agent)
        self.mailer = Mailer(self.x_agents)
        self.execute_distributed()

    def agents_init(self):
        for a in self.x_agents:
            a.initialize()

    def execute_distributed(self):

        self.agents_init()
        while not self.query_agent.is_termination_condition_met():
            self.iteration+=1
            mailer_feedback = self.mailer.place_messages_in_agents_inbox()
            if mailer_feedback : break
            self.agents_perform_iteration()
        self.mailer.place_messages_in_agents_inbox()
        self.collect_data()



    def agents_perform_iteration(self):
        for a in self.x_agents:
            a.execute_iteration()

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
        infeasible_pa = {}
        for auc in self.constraints_collections:
            cum_delta_from_solution_dict[auc] = {}
            sum_of_alternative_cost_dict[auc] = {}
            sorted_unique_alternative_constraints = sorted(auc.alternative_unique_constraints, key=lambda x: x.cost, reverse=True)
            sum_of_alternative_cost = 0
            for constraint in sorted_unique_alternative_constraints:
                cost = constraint.cost

                sum_of_alternative_cost = sum_of_alternative_cost + cost
                delta = (sum_of_alternative_cost - solution_unique_sum_cost)
                cum_delta_from_solution_dict[auc][constraint] = delta
                sum_of_alternative_cost_dict[auc][constraint]=sum_of_alternative_cost
                if cost == my_inf:
                    if auc not in infeasible_pa.keys():
                        infeasible_pa[auc] = []
                    infeasible_pa[auc].append(constraint)

        return cum_delta_from_solution_dict,sum_of_alternative_cost_dict,infeasible_pa

    def create_query_x_agent(self, agent):
        id_,variable,domain,neighbors_agents_id,neighbors_obj_dict = self.get_info_for_x_agent(agent)
        if self.explanation_type == ExplanationType.Shortest_Explanation:
            ax = AgentX_Query_BroadcastCentral(id_, variable, domain, neighbors_agents_id, neighbors_obj_dict, self.query)
        if self.explanation_type == ExplanationType.Grounded_Constraints:
            ax = AgentX_Query_BroadcastCentral_NoSort(id_, variable, domain, neighbors_agents_id, neighbors_obj_dict, self.query)
        #if self.explanation_type == ExplanationType.CEDAR_opt3A:
        #    ax = AgentX_Query_BroadcastDistributed(id_, variable, domain, neighbors_agents_id, neighbors_obj_dict, self.query)
        if self.explanation_type == ExplanationType.Sort_Parallel:
            ax = AgentX_Query_BroadcastDistributedV2(id_, variable, domain, neighbors_agents_id, neighbors_obj_dict,
                                                   self.query)

        if self.explanation_type == ExplanationType.Varint_max:
            ax = AgentX_Query_BroadcastDistributed_communication_heurtsic_max(id_, variable, domain, neighbors_agents_id, neighbors_obj_dict,
                                                     self.query)
        if self.explanation_type == ExplanationType.Varint_mean:
            ax = AgentX_Query_BroadcastDistributed_communication_heurtsic_mean(id_, variable, domain,
                                                                              neighbors_agents_id, neighbors_obj_dict,
                                                                              self.query)
        return ax,id_


    def get_info_for_x_agent(self, agent):
        id_ = agent.id_
        variable = copy.deepcopy(agent.variable)
        domain = copy.deepcopy(agent.domain)
        neighbors_agents_id = copy.deepcopy(agent.neighbors_agents_id)
        neighbors_obj_dict = agent.neighbors_obj_dict
        return id_,variable,domain,neighbors_agents_id,neighbors_obj_dict

    def create_x_agents(self, dcop, query_agent_id):
        ans = []
        for agent in dcop.agents:
            id_,variable,domain,neighbors_agents_id,neighbors_obj_dict = self.get_info_for_x_agent(agent)
            if id_ != query_agent_id:
                if self.explanation_type == ExplanationType.Shortest_Explanation or  self.explanation_type == ExplanationType.Grounded_Constraints:
                    ax = AgentX_BroadcastCentral(id_, variable, domain, neighbors_agents_id, neighbors_obj_dict)
                if self.explanation_type == ExplanationType.Sort_Parallel:
                    ax = AgentX_BroadcastDistributed(id_, variable, domain, neighbors_agents_id, neighbors_obj_dict)
                if self.explanation_type == ExplanationType.Varint_max or self.explanation_type == ExplanationType.Varint_mean:
                    ax = AgentX_BroadcastDistributed(id_, variable, domain, neighbors_agents_id, neighbors_obj_dict)

                ans.append(ax)
        return ans

    def get_centralized_explanation(self):
        self.constraints_collections = self.collect_constraints()
        self.cum_delta_from_solution_dict, self.sum_of_alternative_cost_dict, self.infeasible_pa = self.get_cumulative_delta_from_solution_dict()
        self.min_constraint_collection = min(self.constraints_collections,key=lambda x: x.alternative_unique_constraints_cost)
        self.min_cum_delta_from_solution = self.cum_delta_from_solution_dict[self.min_constraint_collection]

    def collect_data(self):
        self.data_entry["Alternative_delta_cost_per_addition"] = self.query_agent.alternative_delta_constraints_cost_per_addition
        self.data_entry["Iterations"] = self.iteration
        self.data_entry["NCLO"] = self.mailer.mailer_clock
        self.data_entry["NCLO_for_valid_solution"] = self.query_agent.NCLO_for_valid_solution

        self.data_entry["Total Messages"] =self.mailer.total_msgs
        self.data_entry["Bandwidth"] = self.mailer.total_bandwidth



        self.data_entry["Alternative # Constraint"] = len(self.query_agent.alternative_constraints_for_explanations)
        self.data_entry["Cost delta of Valid"] = self.get_alternative_cost_delta(is_min_for_valid=True)
        self.data_entry["Delta Cost per Constraint"] = self.data_entry["Cost delta of Valid"]/self.data_entry["Alternative # Constraint"]
        self.data_entry["Cost delta of All Alternatives"] = self.get_alternative_cost_delta(is_min_for_valid=False)
        self.data_entry["Delta Cost of All Alternatives per Constraint"] = self.data_entry["Cost delta of All Alternatives"]/self.data_entry["Alternative # Constraint"]
    #self.alternative_constraints_min_valid_cost = 0
    #self.alternative_constraints_max_measure = 0
    @staticmethod
    def measure_names():
        return ["Iterations","NCLO","Total Messages","Bandwidth","Alternative # Constraint","Cost delta","Delta Cost per Constraint"]
    def get_alternative_cost_delta(self,is_min_for_valid):
        if is_min_for_valid:
            alt_sum = self.query_agent.alternative_constraints_min_valid_cost
        else:
            alt_sum = self.query_agent.alternative_constraints_max_measure

        solution_sum  = self.query_agent.solution_cost

        ans = alt_sum-solution_sum

        return ans


class XDCOP:
    def __init__(self,dcop,query):
        self.dcop = dcop
        self.query = query
        #self.explanation = Explanation(query,explanation_type,dcop)



