import os
import socket
import tkinter as tk
from tkinter import messagebox
import tkinter.filedialog
import tkinter.simpledialog
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

        upload_button = tk.Button(self, text="Upload File", command=self.upload_file)
        upload_button.grid(row=3, column=0, padx=5, pady=5)

        download_button = tk.Button(self, text="Download File", command=self.download_file)
        download_button.grid(row=3, column=1, padx=5, pady=5)

    def login(self):
        # Get the username and password from the entry fields
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Create a new socket and connect to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, PORT))

        # Send the username and password to the server for verification
        client_socket.send(f"login {username} {password}".encode())

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
        client_socket.send(f"signup {username} {password}".encode())

        # Receive the server's response
        response = client_socket.recv(1024).decode().strip()

        # Close the client socket
        client_socket.close()

        # Check the server's response and show an appropriate message
        if response == "OK":
            tk.messagebox.showinfo("Signup Successful", f"Welcome, {username}!")
        else:
            tk.messagebox.showerror("Signup Failed", "Username already exists")

    @staticmethod
    def upload_file():
        # Get the path of the file to upload
        filepath = tk.filedialog.askopenfilename()

        if not filepath:
            return

        # Open the file and read its contents
        with open(filepath, 'rb') as f:
            file_data = f.read()

        # Create a new socket and connect to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, PORT))

        # Send the "upload" command to the server
        client_socket.send(b"upload")

        # Send the filename and file size to the server
        filename = os.path.basename(filepath)
        file_size = len(file_data)
        client_socket.send(f"{filename} {file_size}".encode())

        # Send the file data to the server in chunks of 1024 bytes
        bytes_sent = 0
        while bytes_sent < file_size:
            chunk = file_data[bytes_sent:bytes_sent + 1024]
            client_socket.send(chunk)
            bytes_sent += len(chunk)

        # Receive the server's response
        response = client_socket.recv(1024).decode().strip()

        # Close the client socket
        client_socket.close()

        # Show the server's response
        tk.messagebox.showinfo("File Uploaded", response)

    @staticmethod
    def download_file():
        # Get the filename to download
        filename = tk.simpledialog.askstring("Download File", "Enter filename:")

        if not filename:
            return

        # Create a new socket and connect to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, PORT))

        # Send the "download" command and filename to the server
        client_socket.send(f"download {filename}".encode())

        # Receive the file size from the server
        file_size = int(client_socket.recv(1024).decode().strip())

        # Receive the file data from the server in chunks of 1024 bytes
        file_data = b''
        bytes_received = 0
        while bytes_received < file_size:
            chunk = client_socket.recv(min(1024, file_size - bytes_received))
            file_data += chunk
            bytes_received += len(chunk)
            print(chunk)

        # Save the file to the Downloads folder
        downloads_folder = os.path.expanduser("~\\Downloads")
        filepath = os.path.join(downloads_folder, filename.split('\\')[-1])
        with open(filepath, 'wb') as f:
            f.write(file_data)

        # Close the client socket
        client_socket.close()

        # Show a message that the file has been downloaded
        tk.messagebox.showinfo("File Downloaded", f"{filename} has been downloaded to {downloads_folder}")


if __name__ == "__main__":
    login_window = LoginWindow()
    login_window.mainloop()
