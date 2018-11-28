from tkinter import *
from tkinter.ttk import *
import tkinter.font as tkFont
from nexusdraft.hotslogs.rawexport.csvreader import read_hero_list, read_map_list
from nexusdraft.draft.draft import HotSDraft
import nexusdraft.draft.ranking as Ranking
import nexusdraft.hotslogs.rawexport.update as update
from nexusdraft.hotslogs.rawexport.countertableloader import CounterTableGenerator
from nexusdraft.app.player import get_player_profile, FriendManager, PlayerBox
from nexusdraft.app.settings import SettingsManager
import nexusdraft.meta.metascript as metascript
import threading

try:
    hero_list = sorted([i[1] for i in read_hero_list("data/hero_map.csv")])
    map_list = sorted([i[1] for i in read_map_list("data/hero_map.csv")])
except FileNotFoundError:
    hero_list = []
    map_list = []
ctg = CounterTableGenerator()


class PickBox(Combobox):
    def __init__(self, parent):
        Combobox.__init__(self, parent)
        self.list = hero_list
        self.configure(width=12, values=self.list)
        self.set("")
        self.bind("<KeyRelease>", self.keydown)

    def check(self):
        return self.get() in hero_list or self.get() == "IGNORE"

    def autocomplete(self):
        def raw_str(str):
            s = ""
            for i in str:
                if i.isalpha():
                    s += i.lower()
            return s
        raw_text = raw_str(self.get())
        match = []
        non_match = []
        for i in hero_list:
            raw_name = raw_str(i)
            if len(raw_text) > len(raw_name):
                non_match.append(i)
            elif raw_text == raw_name[:len(raw_text)]:
                match.append(i)
            else:
                non_match.append(i)
        self.list = match + non_match
        self.configure(values=self.list)

    def keydown(self, event):
        if event.keysym == "Return":
            self.event_generate("<Down>")
        self.autocomplete()


class MainWindow(Tk):

    def __init__(self):
        Tk.__init__(self)
        self.draft = HotSDraft()
        self.title("Nexus Draft, the HotS draft helper")
        self.friend_manager = FriendManager()
        self.settings_manager = SettingsManager()

        title_font = tkFont.Font(family="Helvetica", size=24)

        main_frame = Frame(self)
        main_frame.pack(fill=BOTH, expand=True)

        title_frame = Frame(main_frame)
        title_frame.pack()
        Label(title_frame, text="Nexus Draft", font=title_font).pack(pady=10)

        self.left_first = BooleanVar(None, True)

        sequence_frame = Frame(main_frame)
        sequence_frame.pack(pady=5)

        sequence_btns = [
            Radiobutton(sequence_frame, text="Left First", variable=self.left_first, value=True, command=self.change_sequence),
            Radiobutton(sequence_frame, text="Right First", variable=self.left_first, value=False, command=self.change_sequence)]
        sequence_btns[0].pack(side=LEFT, padx=15)
        sequence_btns[1].pack(side=RIGHT, padx=15)

        map_frame = Frame(main_frame)
        map_frame.pack(pady=5)
        self.map_box = Combobox(map_frame, value=map_list)
        self.map_box.pack()

        ban_frame = Frame(main_frame)
        ban_frame.pack(pady=5)
        nums = ["1st", "2nd", "3rd"]
        ban_frames = [Frame(ban_frame) for _ in range(6)]
        for i in ban_frames:
            i.pack(side=LEFT)
        ban_boxes = [[Label(ban_frames[i], text="{} Ban:".format(nums[i % 3])), PickBox(ban_frames[i])] for i in range(6)]
        for i in ban_boxes:
            i[0].pack()
            i[1].pack()
        self.ban_boxes = [ban_boxes[:3], ban_boxes[3:]]

        pick_frame = Frame(main_frame)
        pick_frame.pack()
        left_frame = Frame(pick_frame)
        left_frame.pack(side=LEFT)
        mid_frame = Frame(pick_frame, width=100)
        mid_frame.pack(side=LEFT)
        right_frame = Frame(pick_frame)
        right_frame.pack(side=LEFT)

        left_frames = [Frame(left_frame) for i in range(5)]
        self.tl_checks = [BooleanVar(left_frame) for i in range(5)]
        self.tl_picked = set()
        for i in left_frames:
            i.pack(pady=5)
        left_pick_widgets = [
            [Label(v, text="Player{} ID:".format(i + 1)), PlayerBox(v, self.friend_manager), Label(v, text="Hero:"),
             PickBox(v), Checkbutton(v, variable=self.tl_checks[i], onvalue=True, offvalue=False)] for i, v in enumerate(left_frames)]
        for i in left_pick_widgets :
            for j in (i if self.draft.tl_draft else i[:-1]) :
                j.pack(side=LEFT)
        right_frames = [Frame(right_frame) for i in range(5)]
        for i in right_frames:
            i.pack(pady=5)
        right_pick_widgets = [[Label(v, text="Enemy Hero {}:".format(i + 1)), PickBox(v)] for i, v in enumerate(right_frames)]
        for i in right_pick_widgets:
            for j in i:
                j.pack(side=LEFT)

        self.all_pick_widgets = [left_pick_widgets, right_pick_widgets]
        self.pick_boxes = [[x[3] for x in left_pick_widgets], [x[1] for x in right_pick_widgets]]
        self.player_boxes = [x[1] for x in left_pick_widgets]

        result_frame = Frame(main_frame)
        result_frame.pack(pady=10)
        self.result_boxes = [Listbox(result_frame, width=20) for i in range(5)]
        self.result_boxes[0].configure(width=40)
        self.result_boxes[0].pack(side=LEFT)
        for i in range(5):
            self.result_boxes[i].bind("<Double-Button-1>", lambda x, i=i, s=self: s.use_listbox_data(i, x))

        button_frame = Frame(main_frame)
        button_frame.pack()

        quick_draft_button = Button(button_frame, text="Quick Draft")
        quick_draft_button.pack(side=LEFT)
        quick_draft_button.bind("<Button-1>", self.quick_draft)

        generate_button = Button(button_frame, text="Generate")
        generate_button.pack(side=LEFT)
        generate_button.bind("<Button-1>", self.generate_result)

        next_button = Button(button_frame, text="Next")
        next_button.pack(side=LEFT)
        next_button.bind("<Button-1>", self.next)

        bottom_frame = Frame(main_frame)
        bottom_frame.pack(side=BOTTOM, fill=X)

        Label(bottom_frame, text="Region: ").pack(side=LEFT)
        self.region = StringVar()
        self.regions = [None, "1-US", "2-EU", "3-KR", "4-CN"]
        self.region.set(self.regions[self.settings_manager.get("region")])
        region_box = OptionMenu(bottom_frame, self.region, *self.regions, command=self.set_region)
        region_box.pack(side=LEFT)

        reset_button = Button(bottom_frame, text="Reset", command=self.clean_up)
        reset_button.pack(side=RIGHT)

        settings_button = Button(bottom_frame, text="Settings", command=self.settings_manager.spawn_window)
        settings_button.pack(side=RIGHT)

        self.update_button = Button(bottom_frame, text="Update Data", command=self.update)
        self.update_button.pack(side=RIGHT)

        friend_button = Button(bottom_frame, text="Friends", command=self.friend_manager.spawn_friends_window)
        friend_button.pack(side=RIGHT)

        self.teamleague_button = Button(bottom_frame, text="Standard", command=self.toggle_teamleague)
        self.teamleague_button.pack(side=RIGHT)

        if self.settings_manager.get("team_league"):
            self.toggle_teamleague()

    def clean_highlights(self):
        self.draft = HotSDraft(self.draft.left_first, self.draft.tl_draft)
        self.tl_picked = set()
        for i in (0, 1):
            for j in range(3):
                for k in self.ban_boxes[i][j]:
                    k.configure(foreground="black", state="normal")
            for j in range(5):
                for k in self.all_pick_widgets[i][j]:
                    if isinstance(k, Checkbutton):
                        k.configure(state="normal")
                    else:
                        k.configure(foreground="black", state="normal")

    def clean_up(self):
        self.clean_highlights()
        for i in (0, 1):
            for j in range(3):
                self.ban_boxes[i][j][1].set("")
            for j in range(5):
                self.all_pick_widgets[i][j][1].set("")
                self.all_pick_widgets[i][j][3].set("") if i == 0 else None

    def result_box_single(self):
        self.result_boxes[0].configure(width=40)
        for i in range(1, 5):
            self.result_boxes[i].pack_forget()

    def result_box_double(self):
        self.result_boxes[0].configure(width=20)
        self.result_boxes[1].pack(side=LEFT)
        for i in range(2, 5):
            self.result_boxes[i].pack_forget()

    def result_box_five(self):
        self.result_boxes[0].configure(width=20)
        for i in range(1, 5):
            self.result_boxes[i].pack(side=LEFT)

    def change_sequence(self):
        if self.left_first.get() != self.draft.left_first:
            self.draft.left_first = not self.draft.left_first
            self.clean_highlights()

    def set_highlight(self, position, bans=False, highlight=True):
        if bans:
            for i in self.ban_boxes[position[0]][position[1]]:
                if highlight:
                    i.configure(foreground="red")
                else:
                    i.configure(foreground="black")
        else:
            for i in self.all_pick_widgets[position[0]][position[1]]:
                if isinstance(i, Checkbutton):
                    continue
                if highlight:
                    i.configure(foreground="red")
                else:
                    i.configure(foreground="black")

    def lock_input(self, position, bans=False):
        if bans:
            for i in self.ban_boxes[position[0]][position[1]]:
                i.configure(foreground="blue", state="disabled")
        else:
            for i in self.all_pick_widgets[position[0]][position[1]]:
                if isinstance(i, Checkbutton):
                    i.configure(state="disabled")
                    continue
                i.configure(foreground="blue", state="disabled")

    def get_region(self):
        return int(self.region.get()[0])

    def set_region(self, event):
        self.settings_manager.set_and_save("region", self.get_region())

    def get_heroes(self, draft_positions, ban=False):
        result = []
        for i in draft_positions:
            if ban:
                result.append(self.ban_boxes[i[0]][i[1]][1].get())
            else:
                result.append(self.pick_boxes[i[0]][i[1]].get())
        return result

    def toggle_teamleague(self):
        if self.draft.tl_draft:
            self.teamleague_button.configure(text="Hero League")
            for i in self.all_pick_widgets[0]:
                i[-1].pack_forget()
            self.settings_manager.set_and_save("team_league", False)
        else:
            self.teamleague_button.configure(text="Team League")
            for i in self.all_pick_widgets[0]:
                i[-1].pack(side=LEFT)
            self.settings_manager.set_and_save("team_league", True)
        self.draft.tl_draft = not self.draft.tl_draft
        self.clean_up()

    def validate(self):
        if self.draft.tl_draft and self.draft.side() == 0:
            picked = []
            for i in range(5):
                if self.tl_checks[i].get():
                    if not self.pick_boxes[0][i].check():
                        return False
                    for j in self.left_picks() + self.right_picks() + self.bans() + picked:
                        if j == self.pick_boxes[0][i].get():
                            return False
                    picked.append(self.pick_boxes[0][i].get())
        elif self.draft.draft_position()[0] == "pick":
            picked = []
            for i in self.draft.draft_position()[1:]:
                if not self.pick_boxes[i[0]][i[1]].check():
                    return False
                for j in self.left_picks() + self.right_picks() + self.bans() + picked:
                    if j == self.pick_boxes[i[0]][i[1]].get():
                        return False
                picked.append(self.pick_boxes[i[0]][i[1]].get())
        elif self.draft.draft_position()[0] == "ban":
            pos = self.draft.draft_position()[1]
            if self.settings_manager.get("allow_empty_bans") and self.ban_boxes[pos[0]][pos[1]][1].get() == "":
                return True
            if not self.ban_boxes[pos[0]][pos[1]][1].check():
                return False
            for j in self.left_picks() + self.right_picks() + self.bans():
                if j == self.ban_boxes[pos[0]][pos[1]][1].get():
                    return False
        return True

    def left_picks(self):
        if self.draft.tl_draft:
            return [self.pick_boxes[0][i].get() for i in self.tl_picked if self.pick_boxes[0][i].get() != "IGNORE"]
        else:
            return [self.pick_boxes[0][i[1]].get() for i in self.draft.get_picked_positions(True)
                    if self.pick_boxes[0][i[1]].get() != "IGNORE"]

    def right_picks(self):
        return [self.pick_boxes[1][i[1]].get() for i in self.draft.get_picked_positions(False)
                if self.pick_boxes[1][i[1]].get() != "IGNORE"]

    def bans(self):
        return [self.ban_boxes[i[0]][i[1]][1].get() for i in self.draft.all_banned_positions()
                if self.ban_boxes[i[0]][i[1]][1].get() != "" and self.ban_boxes[i[0]][i[1]][1].get() != "IGNORE"]

    def next(self, event):
        if self.draft.is_tl():
            if self.draft.draft_position() is not None:
                if self.draft.draft_position()[0] == "ban":
                    self.lock_input(self.draft.draft_position()[1], bans=True)
                elif self.draft.side() == 1:
                    if not self.validate():
                        return
                    for i in self.draft.draft_position()[1:]:
                        self.lock_input(i)
                else:
                    count = 0
                    for i in self.tl_checks:
                        if i.get():
                            count += 1
                    if count != len(self.draft.draft_position()) - 1:
                        return
                    if not self.validate():
                        return
                    for i in range(5):
                        if self.tl_checks[i].get():
                            self.lock_input([0, i])
                            self.tl_picked.add(i)
                        elif i not in self.tl_picked:
                            self.set_highlight([0, i], highlight=False)
                    for i in self.tl_checks:
                        i.set(False)
            if self.draft.next() is not None:
                if self.draft.draft_position()[0] == "ban":
                    self.set_highlight(self.draft.draft_position()[1], bans=True)
                elif self.draft.side() == 1:
                    for i in self.draft.draft_position()[1:]:
                        self.set_highlight(i)
                else:
                    for i in range(5):
                        if i not in self.tl_picked:
                            self.set_highlight([0, i])
        else:
            if self.draft.draft_position() is not None:
                if not self.validate():
                    return
                if self.draft.draft_position()[0] == "pick":
                    for i in self.draft.draft_position()[1:]:
                        self.lock_input(i)
                else:
                    self.lock_input(self.draft.draft_position()[1], bans=True)
            if self.draft.next() is not None:
                if self.draft.draft_position()[0] == "pick":
                    for i in self.draft.draft_position()[1:]:
                        self.set_highlight(i)
                else:
                    self.set_highlight(self.draft.draft_position()[1], bans=True)

    def use_listbox_data(self, box_num, event):
        if self.draft.draft_position() is None or self.draft.draft_position()[0] == "ban":
            return
        data = self.result_boxes[box_num].get(int(self.result_boxes[box_num].curselection()[0]))
        if self.draft.tl_draft:
            if box_num in self.tl_picked:
                return
            self.pick_boxes[0][box_num].set(data)
            self.tl_checks[box_num].set(True)
        else:
            self.pick_boxes[0][self.draft.draft_position()[1 + box_num][1]].set(data)

    def popup(self, msg, title="Message"):
        popup = Tk()
        def destroy():
            popup.destroy()
            popup.quit()
        popup.wm_title(title)
        mframe = Frame(popup)
        mframe.pack(fill=BOTH, expand=True)
        Label(mframe, text=msg).pack()
        Button(mframe, text="OK", command=destroy).pack()
        popup.mainloop()

    def update_thread(self):
        global hero_list, map_list
        self.update_button.configure(text="Updating", command=None)
        update.download()
        update.unzip()
        ctg.generate_counter_lists()
        ctg.export_counter_score()
        update.clear()
        hero_list = sorted([i[1] for i in read_hero_list("data/hero_map.csv")])
        map_list = sorted([i[1] for i in read_map_list("data/hero_map.csv")])
        Ranking.init()
        self.update_button.configure(text="Update Data", command=self.update)

    def update(self):
        t = threading.Thread(target=self.update_thread)
        t.start()

    def quick_draft(self, event):
        formula = self.settings_manager.get("grade_model")
        for i in range(5):
            self.result_boxes[i].delete(0, END)

        if self.map_box.get() == "":
            map = None
        else:
            map = self.map_box.get()

        left_picks = [self.pick_boxes[0][i].get() for i in range(5) if self.pick_boxes[0][i].check()]
        right_picks = [self.pick_boxes[1][i].get() for i in range(5) if self.pick_boxes[1][i].check()]
        bans = [self.ban_boxes[i][j][1].get() for i,j in [[0,0],[0,1],[0,2],[1,0],[1,1],[1,2]] if self.ban_boxes[i][j][1].check()]
        ranking = Ranking.hero_ranking(player_profile=None, map=map, friendly=left_picks, enemy=right_picks, formula=formula)
        if "IGNORE" in left_picks:
            left_picks.remove("IGNORE")
        if "IGNORE" in right_picks:
            right_picks.remove("IGNORE")
        for i in bans:
            if i in ranking:
                ranking.remove(i)
        self.result_box_single()
        for i in ranking:
            self.result_boxes[0].insert(END, i)

    def generate_result(self, event):
        formula = self.settings_manager.get("grade_model")
        for i in range(5):
            self.result_boxes[i].delete(0, END)
        if self.draft.draft_position() is None or self.draft.draft_position()[1][0] == 1:
            return

        # get current map
        if self.map_box.get() == "":
            map = None
        else:
            map = self.map_box.get()

        if self.draft.is_tl():
            self.result_box_five()
            empty_slots = [i for i in range(5) if i not in self.tl_picked]
            left_picks = [self.pick_boxes[0][i] for i in self.tl_picked]
            for i in empty_slots:
                player = self.player_boxes[i].get()
                profile = get_player_profile(player, self.get_region())
                ranking = Ranking.hero_ranking(player_profile=profile, map=map, friendly=left_picks, enemy=self.right_picks(),
                                                formula=formula)
                for j in self.bans():
                    if j in ranking:
                        ranking.remove(j)
                for j in ranking:
                    self.result_boxes[i].insert(END, j)

        # generate two results
        elif len(self.draft.draft_position()) == 3:
            self.result_box_double()
            player1 = self.player_boxes[self.draft.draft_position()[1][1]].get()
            player2 = self.player_boxes[self.draft.draft_position()[2][1]].get()
            p1_profile = get_player_profile(player1, self.get_region())
            p2_profile = get_player_profile(player2, self.get_region())
            r1 = Ranking.hero_ranking(player_profile=p1_profile, map=map, friendly=self.left_picks(), enemy=self.right_picks(),
                                      formula=formula)
            r2 = Ranking.hero_ranking(player_profile=p2_profile, map=map, friendly=self.left_picks(), enemy=self.right_picks(),
                                      formula=formula)
            for i in self.bans():
                if i in r1:
                    r1.remove(i)
                if i in r2:
                    r2.remove(i)
            for i in r1:
                self.result_boxes[0].insert(END, i)
            for i in r2:
                self.result_boxes[1].insert(END, i)
        # generate one result
        else:
            self.result_box_single()
            player = self.player_boxes[self.draft.draft_position()[1][1]].get()
            player_profile = get_player_profile(player)
            ranking = Ranking.hero_ranking(player_profile=player_profile, map=map, friendly=self.left_picks(), enemy=self.right_picks(),
                                           formula=formula)
            for i in self.bans():
                if i in ranking:
                    ranking.remove(i)
            for i in ranking:
                self.result_boxes[0].insert(END, i)

