from tkinter import *
from tkinter.ttk import *
import tkinter.font as tkFont
from nexusdraft.hotslogs.rawexport.csvreader import read_hero_list, read_map_list
from nexusdraft.draft.draft import HotSDraft
import nexusdraft.draft.ranking as Score
import nexusdraft.hotslogs.rawexport.update as update
from nexusdraft.hotslogs.rawexport.countertableloader import CounterTableGenerator
from nexusdraft.app.player import get_player_profile, FriendManager, PlayerBox
from nexusdraft.app.settings import SettingsManager
import threading

try:
    hero_list = sorted([i[1] for i in read_hero_list("../data/hero_map.csv")])
    map_list = sorted([i[1] for i in read_map_list("../data/hero_map.csv")])
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
        return self.get() in hero_list

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
        for i in left_frames:
            i.pack(pady=5)
        left_pick_widgets = [
            [Label(v, text="Player{} ID:".format(i + 1)), PlayerBox(v, self.friend_manager), Label(v, text="Hero:"), PickBox(v)] for i, v in
            enumerate(left_frames)]
        for i in left_pick_widgets:
            for j in i:
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
        self.result_box_1 = Listbox(result_frame, width=40)
        self.result_box_2 = Listbox(result_frame, width=20)
        self.result_box_1.pack(side=LEFT)
        self.result_box_1.bind("<Double-Button-1>", self.use_listbox1_data)
        self.result_box_2.bind("<Double-Button-1>", self.use_listbox2_data)


        button_frame = Frame(main_frame)
        button_frame.pack()

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
        self.region.set("1-US")
        region_box = OptionMenu(bottom_frame, self.region, None, "1-US", "2-EU", "3-KR", "4-CN")
        region_box.pack(side=LEFT)

        reset_button = Button(bottom_frame, text="Reset", command=self.clean_up)
        reset_button.pack(side=RIGHT)

        settings_button = Button(bottom_frame, text="Settings", command=self.settings_manager.spawn_window)
        settings_button.pack(side=RIGHT)

        self.update_button = Button(bottom_frame, text="Update Data", command=self.update)
        self.update_button.pack(side=RIGHT)

        friend_button = Button(bottom_frame, text="Friends", command=self.friend_manager.spawn_friends_window)
        friend_button.pack(side=RIGHT)

    def clean_highlights(self):
        self.draft = HotSDraft(self.draft.left_first, self.draft.tl_draft)
        for i in (0, 1):
            for j in range(3):
                for k in self.ban_boxes[i][j]:
                    k.configure(foreground="black", state="normal")
            for j in range(5):
                for k in self.all_pick_widgets[i][j]:
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
        self.result_box_1.configure(width=40)
        self.result_box_2.pack_forget()

    def result_box_double(self):
        self.result_box_1.configure(width=20)
        self.result_box_2.pack()

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
                i.configure(foreground="blue", state="disabled")

    def get_region(self):
        return int(self.region.get()[0])

    def get_heroes(self, draft_positions, ban=False):
        result = []
        for i in draft_positions:
            if ban:
                result.append(self.ban_boxes[i[0]][i[1]][1].get())
            else:
                result.append(self.pick_boxes[i[0]][i[1]].get())
        return result

    def validate(self):
        if self.draft.draft_position()[0] == "pick":
            for i in self.draft.draft_position()[1:]:
                if not self.pick_boxes[i[0]][i[1]].check():
                    return False
                for j in self.get_heroes(self.draft.all_picked_positions()):
                    if j == self.pick_boxes[i[0]][i[1]].get():
                        return False
                for j in self.get_heroes(self.draft.all_banned_positions(), ban=True):
                    if j == self.pick_boxes[i[0]][i[1]].get():
                        return False
        if self.draft.draft_position()[0] == "ban":
            pos = self.draft.draft_position()[1]
            if not self.ban_boxes[pos[0]][pos[1]][1].check():
                return False
            for j in self.get_heroes(self.draft.all_picked_positions()):
                if j == self.ban_boxes[pos[0]][pos[1]][1].get():
                    return False
            for j in self.get_heroes(self.draft.all_banned_positions(), ban=True):
                if j == self.ban_boxes[pos[0]][pos[1]][1].get():
                    return False
        return True

    def next(self, event):
        if self.draft.is_tl():
            print("Team League is not implemented!")
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

    def use_listbox1_data(self, event):
        if self.draft.draft_position() is None or self.draft.draft_position()[0] == "ban":
            return
        data = self.result_box_1.get(int(self.result_box_1.curselection()[0]))
        self.pick_boxes[self.draft.draft_position()[1][0]][self.draft.draft_position()[1][1]].set(data)

    def use_listbox2_data(self, event):
        if self.draft.draft_position() is None or len(self.draft.draft_position()) != 3:
            return
        data = self.result_box_2.get(int(self.result_box_2.curselection()[0]))
        self.pick_boxes[self.draft.draft_position()[2][0]][self.draft.draft_position()[2][1]].set(data)

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
        self.update_button.configure(text="Updating", command=None)
        update.download()
        update.unzip()
        ctg.generate_counter_lists()
        ctg.export_counter_score()
        update.clear()
        self.update_button.configure(text="Update Data", command=self.update)

    def update(self):
        t = threading.Thread(target=self.update_thread)
        t.start()

    def generate_result(self, event):
        formula = self.settings_manager.get("grade_model")
        scale = (self.settings_manager.get("duo_scale"),
                 self.settings_manager.get("counter_scale"),
                 self.settings_manager.get("map_scale"))
        self.result_box_1.delete(0, END)
        self.result_box_2.delete(0, END)
        if self.draft.draft_position() is None or self.draft.draft_position()[1][0] == 1:
            return

        left_picks = [self.pick_boxes[0][i[1]].get() for i in self.draft.get_picked_positions(True)]
        right_picks = [self.pick_boxes[1][i[1]].get() for i in self.draft.get_picked_positions(False)]
        bans = [self.ban_boxes[i[0]][i[1]][1].get() for i in self.draft.all_banned_positions()]

        if self.map_box.get() == "":
            map = None
        else:
            map = self.map_box.get()

        if len(self.draft.draft_position()) == 3:
            self.result_box_double()
            player1 = self.player_boxes[self.draft.draft_position()[1][1]].get()
            player2 = self.player_boxes[self.draft.draft_position()[2][1]].get()
            p1_profile = get_player_profile(player1, self.get_region())
            p2_profile = get_player_profile(player2, self.get_region())
            r1 = Score.hero_ranking(player_profile=p1_profile, map=map, friendly=left_picks, enemy=right_picks,
                                    formula=formula, scale=scale)
            r2 = Score.hero_ranking(player_profile=p2_profile, map=map, friendly=left_picks, enemy=right_picks,
                                    formula=formula, scale=scale)
            for i in left_picks + right_picks + bans:
                if i in r1:
                    r1.remove(i)
                if i in r2:
                    r2.remove(i)
            for i in r1:
                self.result_box_1.insert(END, i)
            for i in r2:
                self.result_box_2.insert(END, i)

        else:
            self.result_box_single()
            player = self.player_boxes[self.draft.draft_position()[1][1]].get()
            player_profile = get_player_profile(player)
            ranking = Score.hero_ranking(player_profile=player_profile, map=map, friendly=left_picks, enemy=right_picks)
            for i in left_picks + right_picks + bans:
                if i in ranking:
                    ranking.remove(i)
            for i in ranking:
                self.result_box_1.insert(END, i)

