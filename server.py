import socket
import traceback
from pickle import loads
from threading import Thread
import mysql.connector as mysql
import hashlib

SERVER_IP = '0.0.0.0'
PORT = 8080
QUEUE_LEN = 10

db = mysql.connect(host="localhost", user="root", passwd="OC8305", database="test")
cursor = db.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255)"
               ", password VARCHAR(255))")


print(f"server listening on {SERVER_IP}: {PORT}")


def handle_client(client_socket, addr):
    try:
        print(f"connected by {addr}")
        while True:
            data = loads(client_socket.recv(1024))
            print(data)
            username = data[0]
            password = hashlib.md5(data[1].encode()).hexdigest()
            query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            values = [(username, password)]
            cursor.executemany(query, values)

            ## to make final output we have to run the 'commit()' method of the database object
            db.commit()

            print(cursor.rowcount, "records inserted")
            if not data:
                break
    except EOFError as err:
        print(err)
    finally:
        print(f"Connection closed by {addr}")
        client_socket.close()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, PORT))
    server_socket.listen()
    while True:
        client_socket, addr = server_socket.accept()
        thread = Thread(target=handle_client, args=(client_socket, addr))
        thread.start()


if __name__ == '__main__':
    main()
