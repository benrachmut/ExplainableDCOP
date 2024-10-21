from abc import ABC, abstractmethod

class Explanation(ABC):
    def __init__(self, dcop, category_1_agents, category_2_agents, category_3_agents, category_4_agents):
        """
        Args:
            dcop: A solved DCOP instance (i.e., given context).
            category_1_agents: List of agent IDs in Category 1 (constrained to context assignment).
            category_2_agents: List of agent IDs in Category 2 (free to select any value except the context assignment).
            category_3_agents: Dict of agent IDs in Category 3 (constrained to specific non-context assignment).
            category_4_agents: List of agent IDs in Category 4 (completely free to select any value).
        """
        self.dcop = dcop
        self.context = {agent.id_: agent.variable for agent in self.dcop.agents}  # Agent assignments taken from dcop.
        self.context_global_cost = calc_global_cost(dcop)
        self.category_1_agents = category_1_agents
        self.category_2_agents = category_2_agents
        self.category_3_agents = category_3_agents  # Dictionary {agent_id: specific_non_context_given_value}
        self.verify_category_3_agents()
        self.category_4_agents = category_4_agents
        self.verify_agents_in_categories()
        self.no_good = {}
        self.no_good_global_cost = None

    def verify_agents_in_categories(self):
        """
        Verifies that all agents in the DCOP agents list are assigned to exactly one category.

        Raises:
            ValueError: If any agent is missing from the categories or appears in more than one category.
        """

        # Combine all agents from all categories
        all_categories_agents = (
                self.category_1_agents +
                self.category_2_agents +
                list(self.category_3_agents.keys()) +
                self.category_4_agents
        )

        # Ensure all agents appear exactly once
        if len(all_categories_agents) != len(set(all_categories_agents)):
            raise ValueError("Some agents appear in more than one category.")

        # Check if all agents are covered
        dcop_agent_ids = [agent.id_ for agent in self.dcop.agents]
        if set(dcop_agent_ids) != set(all_categories_agents):
            raise ValueError("Not all dcop agents are assigned to a category, or extra agents are found.")

    def verify_category_3_agents(self):
        """
        Verifies that all agents in Category 3 have assigned values that differ from their context assignments.

        Raises:
            ValueError: If an agent's assigned value is equal to its context assignment or if the assigned value
            is not part of the agent's domain.
        """
        for agent in self.dcop.agents:
            if agent.id_ in self.category_3_agents.keys():
                context_assignment = self.context[agent.id_]
                assigned_value = self.category_3_agents[agent.id_]
                if context_assignment == assigned_value:
                    raise ValueError(f"Agent {agent.id_} in category 3 must be assigned to a different value from"
                                     f" the one exists in the context: ({context_assignment}).")

                if assigned_value not in agent.domain:
                    raise ValueError(f"Chosen value: {assigned_value}"
                                     f" for Agent_{agent.id_} is not a valid assignment (not in agent's domain).")

    def update_agent_domains(self):
        """
        Updates the domain of each agent based on their category.
        """
        for agent in self.dcop.agents:
            if agent.id_ in self.category_1_agents:
                # Category 1: Constrained to context assignment
                agent.domain = [agent.variable]
            elif agent.id_ in self.category_2_agents:
                # Category 2: Free to select any value except the context assignment
                agent.domain = [value for value in agent.domain if value != agent.variable]
                agent.variable = agent.agent_random.choice(agent.domain)
            elif agent.id_ in self.category_3_agents:
                # Category 3: Constrained to specific non-context assignment
                assigned_value = self.category_3_agents[agent.id_]
                agent.domain = [assigned_value]
                agent.variable = assigned_value

    def validate_k_limit_on_categories(self, k: int):
        """
         Ensures that there are at most 'k' agents in total across categories 2, 3, and 4.

         Raises:
             ValueError: If the total number of agents in categories 2, 3, and 4 exceeds 'k'.
         """
        # Calculate the total number of agents in categories 2, 3, and 4
        total_agents = (len(set(self.category_2_agents)) + len(set(self.category_3_agents))
                        + len(set(self.category_4_agents)))

        if total_agents > k:
            raise ValueError(
                f"The total number of agents in categories 2, 3, and 4 exceeds the allowed maximum of k={k} "
                f"(Query includes {total_agents} agents in categories 2, 3, and 4)")

    @abstractmethod
    def update_agents_before_generate_no_good(self):
        """
        Abstract method to reset and reinitialize relevant fields for each agent
        according to the algorithm's requirements before generating no-good.
        """
        pass

    @abstractmethod
    def generate_no_good(self):
        """
        Abstract method to generate a no-good. Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def explain(self):
        """
        Abstract method to provide an explanation by comparing the no-good and a given context.
        Must be implemented by subclasses.
        """
        pass


def calc_global_cost(dcop):
    """
    Calculates the global cost based on the current assignments of agents in the DCOP.

    Args:
        dcop: A DCOP instance containing the agents and their constraints.

    Returns:
        global_cost: The total cost of the current assignments.
    """
    global_cost = 0
    for n in dcop.neighbors:
        a1_id, a1_variable =n.a1.id_, n.a1.variable
        a2_id, a2_variable = n.a2.id_, n.a2.variable
        _, constraint_cost = n.get_constraint((a1_id, a1_variable), (a2_id, a2_variable))
        global_cost += constraint_cost
    return global_cost
