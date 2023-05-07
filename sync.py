import os
import shutil
import time
import socket
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Define the server host and port
SERVER_IP = '127.0.0.1'
PORT = 8080

# Define the directory to monitor
WATCH_DIR = 'C:\\Users\\orico\\OneDrive\\שולחן העבודה\\FS'  # 'C:\\Users\\cyber\\Desktop\\FS\\'


# Define the directory on the server to upload files to


class Watcher:
    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, WATCH_DIR, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except Exception as err:
            self.observer.stop()
            print(err)

        self.observer.join()


class Handler(FileSystemEventHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.deleted_folders = set()

    def on_created(self, event):
        if event.is_directory:
            print(f"Folder created: {event.src_path}")
            upload_folder(event.src_path)

    def on_modified(self, event):
        if event.is_directory:
            print(f"Folder modified: {event.src_path}")
            upload_folder(event.src_path)

"""    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            pass

        elif event.event_type == 'moved':
            print(f"File moved: {event.dest_path}")
            upload_file(event.src_path, event.dest_path)
        elif event.event_type == 'modified':
            # Handle file modification
            print(f"File modified: {event.src_path}")
            upload_file(event.src_path, event.src_path)
        elif event.event_type == 'deleted':
            print(f"File deleted: {event.src_path}")
            delete_file(event.src_path)"""

"""
        def on_deleted(self, event):
            if event.is_directory:
                print(f"Folder deleted: {event.src_path}")
                if event.src_path not in self.deleted_folders:
                    self.deleted_folders.add(event.src_path)
                    delete_folder(event.src_path)"""


def upload_file(old_path, new_path):
    # Create a socket connection to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, PORT))

    # Get the file name and size
    file_name = os.path.basename(new_path)
    old_name = os.path.basename(old_path)
    file_size = os.path.getsize(new_path)

    # Send the file name and size to the server
    client_socket.send(f"upload_file old name: {old_name} new name: {file_name} size: {file_size}".encode())

    # Open the file and send its contents to the server in chunks of 1024 bytes
    with open(new_path, "rb") as f:
        while True:
            chunk = f.read(1024)
            if not chunk:
                break
            client_socket.send(chunk)

    # Wait for the server's response
    response = client_socket.recv(1024).decode().strip()

    # Show the server's response
    print(response)
    client_socket.close()


def delete_file(src_path):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, PORT))

    # Get the file name and size
    file_name = os.path.basename(src_path)
    client_socket.send(f"delete {file_name}".encode())
    response = client_socket.recv(1024).decode().strip()

    # Show the server's response
    print(response)
    client_socket.close()


def upload_folder(path):
    # Create a socket connection to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, PORT))

    # Send the folder name and "start" flag to the server
    folder_name = os.path.basename(path)
    client_socket.send(f"upload_folder {folder_name}\n".encode())
    client_socket.recv(1024)

    # Iterate over all the files in the folder and its subfolders
    for root, dirs, files in os.walk(path):
        for file in files:
            # Get the full path of the file
            file_path = os.path.join(root, file)

            # Get the relative path of the file within the folder
            rel_path = os.path.relpath(file_path, path)

            # Get the file size
            file_size = os.path.getsize(file_path)

            # Send the file name, size, and relative path to the server
            client_socket.send(f"{rel_path} size: {file_size}".encode())
            client_socket.recv(1024)

            # Open the file and send its contents to the server in chunks of 1024 bytes
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(1024)
                    if not chunk:
                        break
                    client_socket.send(chunk)

            # Wait for the server's response
            response = client_socket.recv(1024).decode().strip()

            # Show the server's response
            print(response)

    # Send the "end" flag to the server
    client_socket.send(f"upload_folder {folder_name} end".encode())

    # Wait for the server's response
    response = client_socket.recv(1024).decode().strip()

    # Show the server's response
    print(response)

    client_socket.close()


if __name__ == '__main__':
    w = Watcher()
    w.run()
