def check_to_change_best_local_UB(self):
    if self.local_UB is not None:
        if self.token.LB < self.local_UB:
            prev_local_UB = self.local_UB.__deepcopy__()
            self.local_UB = self.token.LB.__deepcopy__()
            text = "local UB is not valid any more, children found a lower UB"
            self.add_to_records(winner=self.local_UB.__deepcopy__(), losers=[prev_local_UB.__deepcopy__()], text=text)
    else:
        self.local_UB = self.token.LB.__deepcopy__()