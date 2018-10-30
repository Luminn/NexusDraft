

class HotSDraft:
    """A class that simulates a HotS draft session"""
    def __init__(self, left_first=True, tl_draft=False):
        self.turn = -1
        self.tl_draft = tl_draft
        self.left_first = left_first

    def is_tl(self):
        """Is Team League"""
        return self.tl_draft

    def _pos(self, turn):
        """The draft position of a given turn"""
        if self.tl_draft:
            if turn < 4:
                result = ["ban", [turn % 2, turn // 2]]
            elif turn == 4:
                result = ["tl_pick", turn % 2]
            elif turn < 7:
                result = ["tl_pick", turn % 2, turn % 2]
            elif turn < 9:
                result = ["ban", [turn % 2, 2]]
            elif turn < 11:
                result = ["tl_pick", turn % 2, turn % 2]
            else:
                result = ["tl_pick", turn % 2]
        else:
            if turn < 4:
                result = ["ban", [turn % 2, turn // 2]]
            elif turn == 4:
                result = ["pick", [0, 0]]
            elif turn == 5:
                result = ["pick", [1, 0], [1, 1]]
            elif turn == 6:
                result = ["pick", [0, 1], [0, 2]]
            elif turn < 9:
                result = ["ban", [turn % 2, 2]]
            elif turn == 9:
                result = ["pick", [1, 2], [1, 3]]
            elif turn == 10:
                result = ["pick", [0, 3], [0, 4]]
            else:
                result = ["pick", [1, 4]]
        if self.left_first:
            return result
        else:
            return [result[0]] + [[1 - i[0], i[1]] for i in result[1:]]

    def draft_position(self):
        """The draft position of the current turn."""
        if self.turn == -1:
            return None
        l = self._pos(self.turn)
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
        self.turn += 1
        if self.turn > 11:
            self.turn = -1
            return None
        return self.draft_position()


    


