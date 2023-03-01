import socket
from pickle import dumps
from tkinter import *
from tkinter import ttk

SERVER_IP = '127.0.0.1'
PORT = 8080
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, PORT))
username = ""
password = ""
win = Tk()
# Set the geometry of Tkinter frame
win.geometry("750x250")


def get_user():
    global entry, username
    username = entry.get()


def get_password():
    global entry, password
    password = entry.get()


# Initialize a Label to display the User Input
while username == '':
    label = Label(win, text="Enter Username", font="Courier 22 bold")
    label.pack()
    # Create an Entry widget to accept User Input
    entry = Entry(win, width=40)
    entry.focus_set()
    entry.pack()
    ttk.Button(win, text="Okay", width=20, command=get_user()).pack(pady=20)
    win.mainloop()


label = Label(win, text="Enter Password", font="Courier 22 bold")
label.pack()
entry = Entry(win, width=40)
entry.focus_set()
entry.pack()
ttk.Button(win, text="Okay", width=20, command=get_password).pack(pady=20)

win.mainloop()

client_socket.send(dumps([username, password]))

message = client_socket.recv(1024).decode()
print(message)
