import socket
import os

SERVER_IP = '0.0.0.0'  # Server IP address
PORT = 8080  # Port to listen on
SERVER_DIR = 'C:\\Users\\cyber\\Desktop\\ServerFolder\\'  # 'C:\\Users\\orico\\OneDrive\\שולחן העבודה\\ServerFolder\\'

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
server_socket.bind((SERVER_IP, PORT))

# Listen for incoming connections
server_socket.listen()

print(f"Server listening on {SERVER_IP}:{PORT}...")
# Accept a new connection


while True:
    client_socket, client_address = server_socket.accept()

    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
    # Receive the client's request
    request = client_socket.recv(1024).decode().strip()

    # Process the request
    if request.startswith("upload"):
        # Parse the file name and size from the request
        old_name = request.split(":")[1][:-8].strip()
        file_name = request.split(":")[2][:-4].strip()
        file_size = request.split(":")[-1].strip()
        print(f"received file: {file_name}")
        # Convert the file size to an integer
        file_size = int(file_size)

        # Receive the file data
        data = b""
        while len(data) < file_size:
            packet = client_socket.recv(file_size - len(data))
            if not packet:
                break
            data += packet

        # Write the file to disk
        with open(SERVER_DIR + file_name, "wb") as f:
            f.write(data)
        if old_name != file_name:
            try:
                os.remove(SERVER_DIR + old_name)
            except FileNotFoundError:
                pass

        # Send a response back to the client
        client_socket.send("OK".encode())

    elif request.startswith("download"):
        # Parse the file name from the request
        file_name = request.split()[1]

        # Check if the file exists on the server
        if os.path.isfile(file_name):
            # Read the file from disk
            with open(SERVER_DIR + file_name, "rb") as f:
                data = f.read()

            # Send the file data to the client
            client_socket.send(data)

            # Send a response back to the client
            client_socket.send("OK".encode())

        else:
            # Send a response back to the client
            client_socket.send("ERROR: File not found".encode())

    elif request.startswith("delete"):
        file_name = ' '.join(request.split()[1:])
        try:
            os.remove(SERVER_DIR + file_name)
            print(f"Deleted {file_name}")
        except FileNotFoundError:
            pass
        client_socket.send("OK".encode())
    # Close the client socket
    client_socket.close()
