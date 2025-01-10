from abc import ABC, abstractmethod
from Agents import Agent
from enum import Enum
from Globals_ import Msg, copy_dict
import random


class MGM_Status(Enum):
    wait_for_neighbors_assignments = 1  # Waiting for neighbors' variable assignment messages
    wait_for_neighbors_lost_reduction = 2  # Waiting for neighbors' loss reduction messages
    calc_local_reduction = 3  # Status for calculating the local reduction based on assignments


class MGM_Msg(Enum):
    assignment = 1  # Message type for sending variable assignments
    lost_reduction = 2  # Message type for sending local reduction values


class MGM(Agent,ABC):

    def __init__(self, id_, D, dcop_id):
        Agent.__init__(self,id_,D)
        self.neighbors_assignments = {}
        self.neighbors_lost_reduction = {}
        self.status = MGM_Status.wait_for_neighbors_assignments
        self.constraints = {}
        self.agent_random = random.Random((((dcop_id+1)+100)+((self.id_+1)+10))*17)
        self.variable = self.agent_random.randint(0, D-1)
        self.lr = None  # Local reduction
        self.lr_potential_asgmt = self.variable  # Potential assignment that leads to max local reduction

    def set_constraints(self):
        """Copies constraints from neighbors' objects and stores them in the local constraints' dictionary."""
        for n_obj in self.neighbors_obj:
            neighbor_id = n_obj.get_other_agent(self)
            cost_table = copy_dict(n_obj.cost_table)
            self.constraints[neighbor_id] = cost_table

    def initialize(self):
        """Sets up constraints and sends initial variable assignments to neighbors."""
        self.set_constraints()
        self.send_assignments_msgs()

    def send_msgs(self):
        """Sends local reduction messages to neighbors after computing."""
        self.send_lost_reduction_msgs()

    def send_assignments_msgs(self):
        """Sends the agent's current variable assignment to all neighbors."""
        msgs = []
        for n_id in self.neighbors_agents_id:
            sender = self.id_
            receiver = n_id
            information = self.variable
            msgs.append(Msg(sender=sender, receiver=receiver, information=information, msg_type=MGM_Msg.assignment))
        self.outbox.insert(msgs)

    def send_lost_reduction_msgs(self):
        """Sends local reduction messages to neighbors."""
        msgs = []
        for n_id in self.neighbors_agents_id:
            sender = self.id_
            receiver = n_id
            information = self.lr
            msgs.append(Msg(sender=sender, receiver=receiver, information=information, msg_type=MGM_Msg.lost_reduction))
        self.outbox.insert(msgs)

    def update_msgs_in_context(self, msgs):
        """Updates the local context based on received messages (either assignment or lost reduction)."""
        for msg in msgs:
            if msg.msg_type == MGM_Msg.assignment:
                self.update_msg_in_context_neighbors_assignment(msg)
            if msg.msg_type == MGM_Msg.lost_reduction:
                self.update_msg_in_context_neighbors_lost_reduction(msg)

    def update_msg_in_context_neighbors_assignment(self, msg):
        """Updates the neighbors' assignments based on received assignment message."""
        neighbor_id = msg.sender
        neighbor_assignment = msg.information
        self.neighbors_assignments[neighbor_id]=neighbor_assignment

    def update_msg_in_context_neighbors_lost_reduction(self, msg):
        """Updates the neighbors' local reduction based on received lost reduction message."""
        neighbor_id = msg.sender
        neighbor_lost_reduction = msg.information
        self.neighbors_lost_reduction[neighbor_id] = neighbor_lost_reduction

    def change_status_after_update_msgs_in_context(self, msgs):
        """Changes the agent's status after processing received messages."""

        if self.status == MGM_Status.wait_for_neighbors_assignments:
            # Switch status to calculate local reduction after receiving assignments
            self.status = MGM_Status.calc_local_reduction

        elif self.status == MGM_Status.wait_for_neighbors_lost_reduction:
            # Update the agent's assignment if it has the greatest local reduction
            if self.is_best_lr():
                self.variable = self.lr_potential_asgmt
            self.send_assignments_msgs()
            # Reset status to wait for neighbors' assignments
            self.status = MGM_Status.wait_for_neighbors_assignments

    def is_compute_in_this_iteration(self):
        """Returns True if the agent should compute in this iteration
        (i.e., if the status is set to calculate the local reduction)."""
        return self.status == MGM_Status.calc_local_reduction

    def compute(self):
        """Calculates the maximum local reduction by exploring all possible assignments and
         determines the best assignment that minimizes local cost."""
        self.lr = 0
        current_local_cost = self.calc_local_cost()
        min_possible_local_cost = current_local_cost
        best_local_assignment = self.variable

        for optional_asgmt in self.domain:
            current_costs = 0
            for neighbor_id, neighbor_asgmt in self.neighbors_assignments.items():
                constraint = self.constraints[neighbor_id]
                if self.id_ < neighbor_id:
                    cost = constraint[(("A_"+str(self.id_), optional_asgmt), ("A_"+str(neighbor_id), neighbor_asgmt))]
                else:
                    cost = constraint[(("A_"+str(neighbor_id), neighbor_asgmt), ("A_"+str(self.id_), optional_asgmt))]
                current_costs += cost

            if current_costs < min_possible_local_cost:
                min_possible_local_cost = current_costs
                best_local_assignment = optional_asgmt

        # If a lower local cost is found with a different assignment, calculate the local reduction
        if min_possible_local_cost < current_local_cost:
            self.lr = current_local_cost - min_possible_local_cost
            self.lr_potential_asgmt = best_local_assignment

    def change_status_after_send_msgs(self):
        """Changes the agent's status to wait for neighbors' lost reduction after sending messages."""
        self.status = MGM_Status.wait_for_neighbors_lost_reduction

    def calc_local_cost(self):
        """Calculates the local cost based on the current variable assignment and neighbors' assignments context."""
        local_cost = 0
        for neighbor_id, neighbor_variable in self.neighbors_assignments.items():
            constraint = self.constraints[neighbor_id]
            if self.id_ < neighbor_id:
                cost = constraint[(("A_"+str(self.id_), self.variable), ("A_"+str(neighbor_id), neighbor_variable))]
            else:
                cost = constraint[(("A_"+str(neighbor_id), neighbor_variable), ("A_"+str(self.id_), self.variable))]
            local_cost += cost
        return local_cost

    def is_best_lr(self):
        """Returns True if the agent holds the greatest local reduction (greater than zero) compared to its neighbors
         (or breaks ties with a lower ID)."""
        flag_greatest_local_lr = True
        for neighbor_id, neighbor_lr in self.neighbors_lost_reduction.items():
            if neighbor_lr > self.lr or (neighbor_lr == self.lr and self.id_ > neighbor_id):
                # Another agent has a greater local reduction or Another agent has the same local reduction
                # but a lower ID (Tie break)
                return False
        return self.lr > 0

    def is_algorithm_complete(self):
        """Checks if the algorithm has completed (i.e., if no positive local reduction is left)."""


        if self.lr is None:
            return False
        else:
            return self.lr <= 0

    def __str__(self):
        """String representation of the agent."""
        return f'MGM_Agent_{self.id_} - {self.variable}'