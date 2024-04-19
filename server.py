import socket

from db import ChatDatabase
from functions import *
from config import HOST, PORT

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

db = ChatDatabase()

# clients: list[socket.socket] = []

clients: dict[str: socket.socket] = {}


if __name__ == "__main__":
    receive(server, clients, db)