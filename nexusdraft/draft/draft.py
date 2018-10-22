

class HotSDraft:
    """A class that simulates a HotS draft session"""
    def __init__(self, left_first=True, tl_draft=False):
        self.turn = -1
        self.tl_draft = tl_draft
        self.left_first = left_first
        self.stored_bp_location = None

    def is_tl(self):
        """Is Team League"""
        return self.tl_draft

    def _pos(self, turn):
        """The draft position of a given turn"""
        if self.tl_draft:
            if turn < 4:
                return ["ban", [turn % 2, turn // 2]]
            elif turn == 4:
                return ["tl_pick", turn % 2]
            elif turn < 7:
                return ["tl_pick", turn % 2, turn % 2]
            elif turn < 9:
                return ["ban", [(turn + 1) % 2, 2]]
            elif turn < 11:
                return ["tl_pick", turn % 2, turn % 2]
            else:
                return ["tl_pick", turn % 2]
        else:
            if turn < 4:
                return ["ban", [turn % 2, turn // 2]]
            elif turn == 4:
                return ["pick", [0, 0]]
            elif turn == 5:
                return ["pick", [1, 0], [1, 1]]
            elif turn == 6:
                return ["pick", [0, 1], [0, 2]]
            elif turn < 9:
                return ["ban", [(turn) % 2, 2]]
            elif turn == 9:
                return ["pick", [1, 2], [1, 3]]
            elif turn == 10:
                return ["pick", [0, 3], [0, 4]]
            else:
                return ["pick", [1, 4]]

    def draft_position(self):
        """The draft position of the current turn."""
        if self.stored_bp_location is not None:
            return self.stored_bp_location
        if self.turn == -1:
            return None
        l = self._pos(self.turn)
        if not self.left_first:
            if self.tl_draft:
                l = [l[0]] + [1 - x for x in l[1:]]
            else:
                l = [l[0]] + [[1 - x[0], x[1]] for x in l[1:]]
        self.stored_bp_location = l
        return l

    def side(self):
        """The active side"""
        return self.draft_position()[1][0]

    def all_picked_positions(self):
        """All draft positions that have been picked"""
        all_positons = [self._pos(i) for i in range(self.turn) if self._pos(i)[0] != "ban"]
        result = []
        for i in all_positons:
            for j in i[1:]:
                result.append(j)
        return result

    def all_banned_positions(self):
        """All draft positions that have been banned"""
        all_positons = [self._pos(i) for i in range(self.turn) if self._pos(i)[0] == "ban"]
        result = []
        for i in all_positons:
            for j in i[1:]:
                result.append(j)
        return result

    def get_picked_positions(self, left=True):
        """All draft positions in a given side that have been picked"""
        return [i for i in self.all_picked_positions() if (i[0] == 0) == left]

    def next(self):
        """Move to the next turn and return the next draft position"""
        self.stored_bp_location = None
        self.turn += 1
        if self.turn > 11:
            self.turn = -1
            return None
        return self.draft_position()


    


