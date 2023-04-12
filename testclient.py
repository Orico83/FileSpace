import socket
import tkinter as tk
from tkinter import messagebox
# Define the server host and port
SERVER_IP = '127.0.0.1' #'10.100.102.14'
PORT = 8080


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login")

        # Create the username and password labels and entry fields
        tk.Label(self, text="Username").grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(self)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self, text="Password").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        # Create the login and signup buttons
        login_button = tk.Button(self, text="Login", command=self.login)
        login_button.grid(row=2, column=0, padx=5, pady=5)

        signup_button = tk.Button(self, text="Sign Up", command=self.signup)
        signup_button.grid(row=2, column=1, padx=5, pady=5)

    def login(self):
        # Get the username and password from the entry fields
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Create a new socket and connect to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, PORT))

        # Send the username and password to the server for verification
        client_socket.send(f"login {username} ".encode())
        client_socket.send(password.encode())

        # Receive the server's response
        response = client_socket.recv(1024).decode().strip()

        # Close the client socket
        client_socket.close()

        # Check the server's response and show an appropriate message
        if response == "OK":
            tk.messagebox.showinfo("Login Successful", f"Welcome, {username}!")
        else:
            tk.messagebox.showerror("Login Failed", "Invalid username or password")

    def signup(self):
        # Get the username and password from the entry fields
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Create a new socket and connect to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, PORT))

        # Send the username and password to the server for signup
        client_socket.send(f"signup {username} ".encode())
        client_socket.send(password.encode())

        # Receive the server's response
        response = client_socket.recv(1024).decode().strip()

        # Close the client socket
        client_socket.close()

        # Check the server's response and show an appropriate message
        if response == "OK":
            tk.messagebox.showinfo("Signup Successful", f"Welcome, {username}!")
        else:
            tk.messagebox.showerror("Signup Failed", "Username already exists")


if __name__ == "__main__":
    login_window = LoginWindow()
    login_window.mainloop()
