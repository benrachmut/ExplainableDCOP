from Explanation import Explanation, calc_global_cost
from MGM import MGM_Status


class MGM_Explanation(Explanation):

    def __init__(self, dcop, category_1_agents, category_2_agents, category_3_agents, category_4_agents):
        """
        Initializes the MGM_Explanation instance, validating the agent categories.

        Args:
            dcop: A solved DCOP instance (i.e., given context).
            category_1_agents: List of agent IDs in Category 1 (constrained to context assignment).
            category_2_agents: List of agent IDs in Category 2 (free to select any value except the context assignment).
            category_3_agents: Dict of agent IDs in Category 3 (constrained to specific non-context assignment).
            category_4_agents: List of agent IDs in Category 4 (completely free to select any value).
        """
        Explanation.__init__(self, dcop, category_1_agents, category_2_agents, category_3_agents, category_4_agents)
        self.validate_k_limit_on_categories(k=1)

    def update_agents_before_generate_no_good(self):
        """Resets relevant fields for each agent before generating a no-good clause."""
        self.update_agent_domains()
        for agent in self.dcop.agents:
            # Reset local reduction variables and status for each agent
            agent.lr = None
            agent.lr_potential_asgmt = agent.variable
            agent.local_clock = 0
            agent.status = MGM_Status.wait_for_neighbors_assignments

    def generate_no_good(self):
        """Executes the DCOP and captures the no-good clause and its global cost."""
        self.dcop.execute()
        self.no_good = {agent.id_: agent.variable for agent in self.dcop.agents}
        self.no_good_global_cost = calc_global_cost(self.dcop)

    def explain(self):
        """Prints a detailed explanation of the context assignments, 
          no-good clause, global costs, and differences in global costs and in implicit constraints 
          between the context and the no-good clause.
          """
        print("Context assignments:")
        for agent, variable in self.context.items():
            print(f'    MGM_Agent_{agent} - {variable}')
        print("")
        print(f"Context global cost is: {self.context_global_cost}")
        print("")
        for agent, variable in self.no_good.items():
            print(f'    MGM_Agent_{agent} - {variable}')
        print("")
        print(f"No-Good global cost is: {self.no_good_global_cost}")
        print("")
        print(f"Therefore the exceed cost comparing to the context the query base on is:"
              f" {self.no_good_global_cost-self.context_global_cost}")
        print("")
        print("Implicit constraints differences:")
        print("")

        # Iterate over agents and their neighbors to compare the implicit constraints of the context and the no-good
        for agent in self.dcop.agents:
            for neighbor in agent.neighbors_agents_id:
                constraint = agent.constraints[neighbor]
                if agent.id_ < neighbor:
                    if not (agent.id_ in self.category_1_agents and neighbor in self.category_1_agents):
                        # Fetch former and current implicit constraints for comparison
                        former_implicit_constraint = constraint[(("A_" + str(agent.id_), self.context[agent.id_]),
                                                                 ("A_" + str(neighbor), self.context[neighbor]))]
                        current_implicit_constraint = constraint[(("A_" + str(agent.id_), self.no_good[agent.id_]),
                                                                  ("A_" + str(neighbor), self.no_good[neighbor]))]
                        print(f"    Constraint of A_{agent.id_} and  A_{neighbor} :")
                        print(f"        Former implicit constraint {former_implicit_constraint}")
                        print(f"        Current implicit constraint {current_implicit_constraint}")
                        print("")
