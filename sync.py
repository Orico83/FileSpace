import os
import time
import socket
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Define the server host and port
SERVER_IP = '127.0.0.1'
PORT = 8080

# Define the directory to monitor
WATCH_DIR = 'C:\\Users\\orico\\OneDrive\\שולחן העבודה\\FileSpace'

# Define the directory on the server to upload files to

# Create a socket connection to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, PORT))


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
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'modified':
            # Handle file modification
            print(f"File modified: {event.src_path}")
            upload_file(event.src_path)


def upload_file(file_path):
    # Get the file name and size
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    # Send the file name and size to the server
    client_socket.send(f"upload {file_name} {file_size}".encode())

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


if __name__ == '__main__':
    w = Watcher()
    w.run()
