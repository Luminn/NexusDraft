

class HotSDraft:

    def __init__(self, left_first=True, tl_draft=False):
        self.bp_pos = -1
        self.tl_draft = tl_draft
        self.left_first = left_first
        self.stored_bp_location = None

    def is_tl(self):
        return self.tl_draft

    def _bp_loc(self, bp_pos):
        if self.tl_draft:
            if bp_pos < 4:
                return ["ban", [bp_pos % 2, bp_pos // 2]]
            elif bp_pos == 4:
                return ["tl_pick", bp_pos % 2]
            elif bp_pos < 7:
                return ["tl_pick", bp_pos % 2, bp_pos % 2]
            elif bp_pos < 9:
                return ["ban", [(bp_pos + 1) % 2, 2]]
            elif bp_pos < 11:
                return ["tl_pick", bp_pos % 2, bp_pos % 2]
            else:
                return ["tl_pick", bp_pos % 2]
        else:
            if bp_pos < 4:
                return ["ban", [bp_pos % 2, bp_pos // 2]]
            elif bp_pos == 4:
                return ["pick", [0, 0]]
            elif bp_pos == 5:
                return ["pick", [1, 0], [1, 1]]
            elif bp_pos == 6:
                return ["pick", [0, 1], [0, 2]]
            elif bp_pos < 9:
                return ["ban", [(bp_pos) % 2, 2]]
            elif bp_pos == 9:
                return ["pick", [1, 2], [1, 3]]
            elif bp_pos == 10:
                return ["pick", [0, 3], [0, 4]]
            else:
                return ["pick", [1, 4]]

    def draft_position(self):
        if self.stored_bp_location is not None:
            return self.stored_bp_location
        if self.bp_pos == -1:
            return None
        l = self._bp_loc(self.bp_pos)
        if not self.left_first:
            if self.tl_draft:
                l = [l[0]] + [1 - x for x in l[1:]]
            else:
                l = [l[0]] + [[1 - x[0], x[1]] for x in l[1:]]
        self.stored_bp_location = l
        return l

    def side(self):
        return self.draft_position()[1][0]

    def all_picked_positions(self):
        all_positons = [self._bp_loc(i) for i in range(self.bp_pos) if self._bp_loc(i)[0] != "ban"]
        result = []
        for i in all_positons:
            for j in i[1:]:
                result.append(j)
        return result

    def all_banned_positions(self):
        all_positons = [self._bp_loc(i) for i in range(self.bp_pos) if self._bp_loc(i)[0] == "ban"]
        result = []
        for i in all_positons:
            for j in i[1:]:
                result.append(j)
        return result

    def get_picked_positions(self, left=True):
        return [i for i in self.all_picked_positions() if (i[0] == 0) == left]

    def next(self):
        self.stored_bp_location = None
        self.bp_pos += 1
        if self.bp_pos > 11:
            self.bp_pos = -1
            return None
        return self.draft_position()


    


