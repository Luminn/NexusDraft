
from tkinter import *
from tkinter.ttk import *
import tkinter.font as tkFont
from nexusdraft.hotslogs.crawler import get_personal_hero_table
import nexusdraft.app.cache as cache


def process_player_str(player_str):
    """Get the Battle Tag, number and Role from a player string"""
    if "/" in player_str:
        temp = player_str.split("/")
        player_str = temp[0]
        role_str = temp[1]
    else:
        role_str = None
    temp = player_str.split("#")
    return temp[0], temp[1], role_str


def get_player_profile(player_str, region=1):
    """Get player profile from hotslogs.com"""
    if player_str == "":
        return None
    tag, num, _ = process_player_str(player_str)
    profile = cache.get_data_or_save("{}#{}#{}".format(tag, num, region), lambda: get_personal_hero_table(tag, num, region))
    return profile


def get_friends():
    """Load saved players from file friends.bin"""
    with open("data/friends.bin", "a"):
        pass
    with open("data/friends.bin", "rb") as file:
        data = file.read()
        buffer = []
        for i in data:
            buffer.append(((0xF & i) << 4) + (i >> 4))
    return [i for i in bytes(buffer).decode("utf-8").split("\n") if not i == ""]


def set_friends(friends):
    """Saved players to file friends.bin"""
    with open("data/friends.bin", "wb") as file:
        string = ""
        buffer = []
        for i in friends:
            string += i + "\n"
        byte_str = string.encode("utf-8")
        for i in byte_str:
            buffer.append(((0b1111 & i) << 4) + (i >> 4))
        file.write(bytes(buffer))


class FriendManager:
    """Manage stored player data and spawn the "friends" window."""
    def __init__(self):
        try:
            self.friends = get_friends()
        except FileNotFoundError:
            self.friends = []

    def spawn_friends_window(self):
        """Spawn a "Friends" window."""
        FriendsWindow(self).mainloop()


class FriendsWindow(Tk):

    def __init__(self, manager):
        Tk.__init__(self)
        self.manager = manager
        self.friends = get_friends()
        self.delegates = []
        self.title("Friends")
        main_frame = Frame(self)
        main_frame.pack(expand=True, fill=BOTH)
        title_font = tkFont.Font(family="Helvetica", size=24)
        Label(main_frame, text="Friends", font=title_font).pack(pady=10)
        self.box = Listbox(main_frame)
        self.box.pack(pady=10)
        self.load_friends()
        name_text = Entry(main_frame)
        name_text.pack()
        bottom_frame = Frame(main_frame)
        bottom_frame.pack(pady=10)
        add_button = Button(bottom_frame, text="Add", command=lambda: self.add_friend(name_text.get()))
        remove_button = Button(bottom_frame, text="Remove", command=lambda: self.remove_friend(name_text.get()))
        add_button.pack(side=LEFT)
        remove_button.pack(side=LEFT)

    def load_friends(self):
        """Reload the friends listbox"""
        self.box.delete(0, END)
        for i in self.friends:
            self.box.insert(END, i)

    def remove_friend(self, id):
        """Delete a friend"""
        if id not in self.friends:
            return
        self.friends.remove(id)
        set_friends(self.friends)
        self.load_friends()
        self.manager.friends = self.friends
        self.manager.list_changed()

    def add_friend(self, id):
        """Add a friend"""
        if id in self.friends or id.find("#") == -1:
            return
        self.friends.append(id)
        set_friends(self.friends)
        self.load_friends()
        self.manager.friends = self.friends
        self.manager.list_changed()


role_list = ["tank", "melee", "ranged", "healer"]


class PlayerBox(Combobox):
    """A widget that allows the users to choose from a list of stored players."""
    def __init__(self, parent, friend_manager):
        Combobox.__init__(self, parent)
        self.friend_manager = friend_manager
        self.configure(width=20)
        self.autocomplete()
        self.bind("<Button-1>", self.autocomplete)

    def autocomplete(self, event=None):
        list = [""]
        if not "/" in self.get():
            for r in role_list:
                list.append(self.get() + "/" + r)
        list += self.friend_manager.friends
        self.configure(values=list)


