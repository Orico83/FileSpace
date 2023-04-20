import os
import socket
import tkinter as tk
from tkinter import messagebox, filedialog
import tkinter.filedialog
import tkinter.simpledialog

# Define the server host and port
SERVER_IP = '127.0.0.1'  # '10.100.102.14'
PORT = 8080


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login")
        self.geometry("250x150")

        # Create the username and password labels and entry fields
        self.username_label = None
        self.password_label = None
        self.username_entry = None
        self.password_entry = None
        self.login_button = None
        self.signup_button = None
        self.upload_button = None
        self.download_button = None

        # Create the username and password labels and entry fields
        self.create_login_widgets()

    def create_file_transfer_widgets(self):
        self.username_label.grid_forget()
        self.password_label.grid_forget()
        self.username_entry.destroy()
        self.password_entry.destroy()
        self.login_button.destroy()
        self.signup_button.destroy()

        self.upload_button = tk.Button(self, text="Upload", command=self.upload_file)
        self.upload_button.grid(row=2, column=0, padx=5, pady=5)

        self.download_button = tk.Button(self, text="Download", command=self.download_file)
        self.download_button.grid(row=2, column=1, padx=5, pady=5)

    def create_login_widgets(self):
        self.username_label = tk.Label(self, text="Username")
        self.username_label.grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(self)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        self.password_label = tk.Label(self, text="Password")
        self.password_label.grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.login_button = tk.Button(self, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, padx=5, pady=5)

        self.signup_button = tk.Button(self, text="Sign Up", command=self.signup)
        self.signup_button.grid(row=2, column=1, padx=5, pady=5)

    def login(self):

        # Get the username and password from the entry fields
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username == '' or password == '':
            return
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
            # Show the download and upload buttons
            self.create_file_transfer_widgets()
        else:
            tk.messagebox.showerror("Login Failed", "Invalid username or password")

    def signup(self):
        # Get the username and password from the entry fields
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username == '' or password == '':
            return
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
            self.create_file_transfer_widgets()

        else:
            tk.messagebox.showerror("Signup Failed", "Username already exists")

    @staticmethod
    def upload_file():
        # Get the path of the file to upload
        # Get the file name using a file dialog
        file_path = filedialog.askopenfilename()
        if not file_path:
            return

        # Get the file name and size
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        # Create a new socket and connect to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, PORT))

        # Send the command to the server to indicate that we want to upload a file
        client_socket.send(b"upload")

        # Send the file metadata (name and size) to the server
        metadata = f" {file_name} {file_size}"
        client_socket.send(metadata.encode())
        client_socket.recv(1024).decode()
        # Send the file data to the server
        with open(file_path, "rb") as file:
            data = file.read()
            client_socket.sendall(data)

        # Receive the server's response
        response = client_socket.recv(1024).decode().strip()

        # Close the client socket
        client_socket.close()

        # Show a message box with the server's response
        if response == "OK":
            messagebox.showinfo("File Uploaded", f"The file '{file_name}' has been uploaded successfully.")
        else:
            messagebox.showerror("Upload Failed", "An error occurred while uploading the file.")

    @staticmethod
    def download_file():
        # Get the filename to download
        file_name = tk.simpledialog.askstring("Download File", "Enter filename:")

        if not file_name:
            return

        # Create a new socket and connect to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, PORT))

        # Send the "download" command and filename to the server
        client_socket.send(f"download {file_name}".encode())

        # Receive the file size from the server
        file_size = client_socket.recv(1024).decode().strip()
        if file_size.isnumeric():
            # Receive the file data from the server in chunks of 1024 bytes
            file_size = int(file_size)
            file_data = b''
            bytes_received = 0
            while bytes_received < file_size:
                chunk = client_socket.recv(min(1024, file_size - bytes_received))
                file_data += chunk
                bytes_received += len(chunk)
                print(chunk)

            # Save the file to the Downloads folder
            downloads_folder = os.path.expanduser("~\\Downloads")
            filepath = os.path.join(downloads_folder, file_name.split('\\')[-1])
            with open(filepath, 'wb') as f:
                f.write(file_data)
            client_socket.send("a".encode())
            file_size = client_socket.recv(1024).decode().strip()

            # Close the client socket
        client_socket.close()

        # Show a message box with the server's response
        if file_size == "OK":
            messagebox.showinfo("File Downloaded", f"The file '{file_name}' has been downloaded successfully.")
        else:
            messagebox.showerror("Upload Failed", file_size)


if __name__ == "__main__":
    login_window = LoginWindow()
    login_window.mainloop()