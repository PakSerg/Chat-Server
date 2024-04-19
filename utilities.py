import datetime
import socket
import json

from config import MSG_SIZE


def get_current_time() -> str:
    dt = datetime.datetime.now()

    hours_str =  f'0{dt.hour}' if len(str(dt.hour)) == 1 else dt.hour
    minutes_str = f'0{dt.minute}' if len(str(dt.minute)) == 1 else dt.minute
    time_now = f'{hours_str}:{minutes_str}'

    return time_now


def send_json_to_client(client: socket.socket, data: dict) -> None:
    client.sendall(json.dumps(data).encode('utf-8'))


def get_json_from_client(client: socket.socket, data_size: int = MSG_SIZE) -> dict:
    data: dict = json.loads(client.recv(data_size).decode('utf-8'))
    return data 


def send_string_to_client(client: socket.socket, string: str) -> None:
    client.sendall(string.encode('utf-8'))