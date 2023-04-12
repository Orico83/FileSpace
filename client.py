import socket
from pickle import dumps
from tkinter import *
from tkinter import ttk

SERVER_IP = '127.0.0.1' #'10.100.102.14'
PORT = 8080
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, PORT))
username = ""
password = ""
win = Tk()
# Set the geometry of Tkinter frame
win.geometry("750x250")


def login():
    global username, password
    username = username_entry.get()
    password = password_entry.get()
    print(username)
    print(password)
    client_socket.send(dumps([username, password]))


username_label = Label(win, text="Username:")
username_label.pack()
username_entry = Entry(win)
username_entry.pack()

password_label = Label(win, text="Password:")
password_label.pack()
password_entry = Entry(win, show="*")
password_entry.pack()

button = Button(win, text="Log In", command=login)
button.pack()

win.mainloop()

