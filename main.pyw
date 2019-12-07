from tkinter import *
from threading import Thread
import webbrowser
import importlib

import client as main
import json


class config:
    def __init__(self, file="config.json"):
        self.file = file

        try:
            with open(self.file, "r") as f:
                try:
                    self.data = json.load(f)
                except:
                    self.data = {}
        except FileNotFoundError:
            print("making config file")
            open(self.file, "a").close()
            self.data = {}

        try:
            self.channel = self.data["channel"]
        except KeyError:
            self.channel = None

        try:
            self.key = self.data["key"]
        except KeyError:
            self.key = None

        try:
            self.token = self.data["token"]
        except KeyError:
            self.token = None

    def get(self):
        return self.data

    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.data, f)




class runner(Thread):
    def __init__(self, caller, program, *args, **kwords):
        super().__init__(*args, **kwords)
        self.program = program
        self.caller = caller

    def run(self):
        print("start")
        self.caller.msg.config(text="Loading...")
        try:
            self.program()
        except Exception as e:
            print(e)
        self.caller.msg.config(text="Invalid token")
        self.caller.b.config(state="normal")
        print("end")



class customLabel(Frame):
    def __init__(self, root, a, b, c, *args, **kwords):
        super().__init__(root, *args, **kwords)
        self.l1 = Label(self, text=a)
        self.l1.pack(fill=X, side=LEFT)

        self.l2 = Label(self, text=b, fg="#0000ff")
        self.l2.pack(fill=X, side=LEFT)

        self.l2.bind("<Button-1>", lambda x: webbrowser.open(c, new=1))

class login(Thread):
    def __init__(self, *args, **kwords):
        super().__init__(*args, **kwords)
        self.uconfig = config()

    def run(self):
        self.r = Tk()
        self.r.title("Discord secret - Login")
        self.r.iconbitmap("icons/icon.ico")

        self.msg = Label(self.r, text="")
        self.msg.pack(fill=X)

        self.label = customLabel(self.r, "Discord token", "(howto)", "https://discordhelp.net/discord-token")
        self.label.pack(fill=X)

        self.token = Entry(self.r, width=50)
        if self.uconfig.token != None:
            self.token.insert(0, self.uconfig.token)
        self.token.pack(fill=X)

        self.b = Button(self.r, text="Login", command=self.login)
        self.b.pack()

        self.r.mainloop()

    def login(self):
        self.uconfig.data["token"] = self.token.get()
        self.uconfig.token = self.uconfig.data["token"]
        self.uconfig.save()
        try:
            importlib.reload(main)
            runner(self, lambda : main.start(self, self.uconfig.token, self.uconfig)).start()
        except Exception as e:
            importlib.reload(main)

        self.b.config(state="disabled")

    def close(self):
        self.r.destroy()




if __name__ == '__main__':
    l = login()

    l.start()
