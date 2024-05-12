def select_next_value(self):
    self.domain_index = self.domain_index + 1
    self.reset_tokens_from_children()
    if self.root_of_tree_start_algorithm:
        self.variable = self.domain[self.domain_index]
        return
    while self.domain_index < len(self.domain):
        self.variable = self.domain[self.domain_index]
        lb_to_update = self.get_lb_to_update()
        did_update = self.try_to_update_lb(lb_to_update)
        if did_update:
            return True
        self.domain_index = -1
        if debug_BNB:
            print(self, "finished going over domain", self.variable)
        return False
