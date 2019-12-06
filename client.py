import discord
import time
import asyncio
import json

import cryptography

from tkinter import *
from threading import Thread
from discord.ext.commands import Bot
from discord.ext.tasks import loop

import base64
import os
import sys
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet


asyncio.set_event_loop(asyncio.new_event_loop())
client = client = Bot(
    command_prefix="",
    description="Encryption bot",
    owner_id=391109829755797514,
    case_insensitive=True
)

client.todo = []
client.channel_id = None


@client.event
async def on_message(message):
    if not client.gui.setup:
        return
    if client.channel_id == None:
        return

    if message.channel.id == client.channel_id.id:
        client.gui.recieve(str(message.author) + ": " + str(message.content))


@client.event
async def on_ready():
    print(time.time())
    print(client.user.name)
    print(client.user.id)
    print("=====================")

    client.gui.start()

    while not client.gui.setup:
        pass

    t = time.time()
    client.get_user(616980460756795394).send("Initialised anonymouse encrypted mesenger. %s"%t)
    client.get_user(616980460756795394).send("Initialised anonymouse encrypted mesenger. %s"%t)


    client.gui._recieve("Loading config...")
    if client.gui.uconfig.channel != None:
        client.gui.set_channel(client.gui.uconfig.channel)
    if client.gui.uconfig.key != None:
        client.gui.set_key(client.gui.uconfig.key)
    client.gui._recieve("Loaded config!\n")


async def background_loop():
    await client.wait_until_ready()
    while True:
        while len(client.todo) > 0:
            await client.todo.pop(0)
        await asyncio.sleep(0.5)


class key:
    def __init__(self, password, salt):
        password = password.encode()
        salt = salt.encode() #os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password)) # Can only use kdf once

        self.key = key.decode()

    def encrypt(self, data):
        return Fernet(self.key).encrypt(data.encode())

    def decrypt(self, data):
        return Fernet(self.key).decrypt(data.encode())


class popupWindow(object):
    def __init__(self, master, label="Label Text", custom_event = lambda x: x):
        self.custom_event = custom_event
        top=self.top=Toplevel(master)
        top.title(label)
        top.resizable(True, False)
        self.l=Label(top,text=label)
        self.l.pack(fill=X, expand=True)
        self.en=Entry(top)
        self.en.pack(fill=X, expand=True)
        self.b=Button(top,text='Ok',command=self.cleanup)
        self.b.pack(fill=X)

    def cleanup(self):
        self.value=self.en.get()
        self.top.destroy()

        self.custom_event(self.value)



class main(Thread):
    def __init__(self, *args, **kwords):
        super().__init__(*args, **kwords)
        self.encrypted = False
        self.setup = False
        self.ucaller = None

    def _delete_window(self):
        try:
            self.root.destroy()
        except:
            pass


    def _destroy(self, event):
        if self.ucaller != None:
            self.ucaller.msg.config(text="Ready")
            self.ucaller.b.config(state="normal")


    def send(self, event):
        inp = self.e.get("1.0", END).strip()
        if inp.strip() == "":
            return
        self.root.after(1, lambda : self.e.delete("1.0", END))

        if self.encrypted:
            try:
                inp = "<encrypted>" + client.en_key.encrypt(inp).decode()
            except AttributeError:
                self._recieve("Error: No key set!")
                return

        try:
            client.todo.append(client.channel_id.send(inp))
        except AttributeError:
            self._recieve("Error: Channel not set!")

    def _recieve(self, text):
        self.text.config(state="normal")
        self.text.insert(END, str(text)+"\n")
        self.text.config(state="disabled")


    def recieve(self, data):
        if len(data.split("<encrypted>")) == 2:
            user = str(data.split(":")[0].strip())
            data = data.split("<encrypted>")[1].strip()
            new_data = client.en_key.decrypt(data).decode()
            data = "%s: %s"%(user, new_data)
            self._recieve("Encrypted    " + data)
            return

        self._recieve("Unencrypted  " + data)


    def set_channel(self, data):
        try:
            data = int(data)
            c = client.get_channel(id=data)
        except ValueError:
            self._recieve("Error: Invalid id")
            return
        if c != None:
            client.channel_id = c
            self._recieve("Success: Set channel to: #%s"%client.channel_id)
            self.uconfig.data["channel"] = client.channel_id.id
            self.uconfig.channel= self.uconfig.data["channel"]
            self.uconfig.save()
            return
        self.recieve("Error: Invalid id")

    def set_key(self, data):
        try:
            client.en_key = key(str(data), "pumpkin")
        except:
            self._recieve("Error: Invalid key!")
            return
        self._recieve("Success: Set key!")
        self.uconfig.data["key"] = str(data)
        self.uconfig.key = self.uconfig.data["key"]
        self.uconfig.save()


    def set_encrypt(self):
        self.encrypted = not self.encrypted

        if self.encrypted:
            self.menubar.entryconfigure(3, label="Encrypted")
        else:
            self.menubar.entryconfigure(3, label="Unencrypted")


    def run(self):
        self.root = Tk()
        self.root.title("Discord secret - by PaulN07")
        self.root.protocol("WM_DELETE_WINDOW", self._delete_window)
        self.root.bind("<Destroy>", self._destroy)

        self.t = Frame(self.root)
        self.t.pack(fill=BOTH, expand=True)


        self.text=Text(self.t, state="disabled", width=32, height=15)
        self.text.pack(side=LEFT, fill=BOTH, expand = YES)

        self.yscrollbar = Scrollbar(self.t, orient=VERTICAL, command=self.text.yview)
        self.yscrollbar.pack(side=RIGHT, fill=Y)
        self.text["yscrollcommand"]=self.yscrollbar.set

        self.e = Text(self.root, height=3)
        self.e.pack(side=BOTTOM, fill=X)

        self.e.bind("<Return>", lambda x: self.send(x))



        # create a toplevel menu
        self.menubar = Menu(self.root)
        self.menubar.add_command(label="Set Channel", command=lambda : popupWindow(self.root, label="Set channel id", custom_event = lambda x : self.set_channel(x)))
        self.menubar.add_command(label="Set Key", command=lambda : popupWindow(self.root, label="Set encryption key password", custom_event = lambda x : self.set_key(x)))
        self.menubar.add_command(label="Unencrypted", command=lambda : self.set_encrypt())

        # display the menu
        self.root.config(menu=self.menubar)

        self.setup = True

        if self.ucaller != None:
            self.ucaller.msg.config(text="Loaded!")

        self.root.mainloop()



def start(caller, token, config):
    m = main()
    m.ucaller = caller
    m.uconfig = config

    client.gui = m

    client.loop.create_task(background_loop())

    try:
        client.run(token, bot=False)
    except:
        raise RuntimeError("Error")


if __name__ == '__main__':
    try:
        start(None, input("token: "))
    except:
        print("Bad Tokin")
        input("Press Enter to continue...")
    finally:
        sys.exit("Bad token")
