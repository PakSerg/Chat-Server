import socket
import json
import threading

from db import ChatDatabase
from utilities import *


def handle_client(client: socket.socket, clients: dict[str, socket.socket], db: ChatDatabase) -> None:  # Прослушивание конкретного пользователя
    user_id: int = None
    while True:
        success, user_id = listen_for_log_in_or_sign_up(client, db)
        if success:
            break
    clients[str(user_id)] = client 
    send_chat_history(client, db, user_id) 

    while True:
        try:
            data: dict = get_json_from_client(client)
            print(data)
            action = data.get('header')

            if action == 'new_message':
                handle_new_message(data, clients, db, user_id)

            elif action == 'new_chat':
                handle_creating_new_chat(data, client, db, user_id)

            elif action == 'new_member':
                handle_new_member(data, clients, db)

        except Exception as e:
            clients.pop(str(user_id))
            client.close()
            break


def broadcast_new_message(message: dict, clients: dict[str, socket.socket], db: ChatDatabase) -> None:
    users = db.get_users_by_chat(message.get('chat_id'))
    print(f'users: {users}\n')

    for user_id in users:
        client: socket.socket = clients.get(str(user_id)) 
        if client:
            print(f'[existing] client: {client}\n')
            send_json_to_client(client, message)
    
    print(f'broadcasted message: {message}')
    
    print('broadcasted')


def send_chat_history(client: socket.socket, db: ChatDatabase, user_id: int) -> None:
    chat_history = db.get_chats_history(user_id)
    print(chat_history)
    send_json_to_client(client, chat_history) 


def receive(server: socket.socket, clients: dict[str, socket.socket], db: ChatDatabase) -> None:
    server.listen() 
    while True:
        new_client, address = server.accept()

        print(f"Новый пользователь подключился {address}")

        thread = threading.Thread(target=handle_client, args=(new_client, clients, db)) 
        thread.start() 


def listen_for_log_in_or_sign_up(new_client: socket.socket, db: ChatDatabase) -> list[bool, int]: 
    while True:
        try:
            recieved_data = new_client.recv(1024)

            if recieved_data:
                print('Получили данные')

                recieved_data = recieved_data.decode('utf-8')
                data: dict = json.loads(recieved_data)  
                signing_up = data.get('header') == 'sign_up'
                logging_in = data.get('header') == 'log_in'

                client_name = data.get('name')
                client_hashed_password = data.get('hashed_password')

                if signing_up:
                    db.create_user(client_name, client_hashed_password)
                    user_id: int = db.get_user_id(client_name, client_hashed_password)
                    send_string_to_client(new_client, str(user_id))

                    return [True, user_id]

                elif logging_in:
                    user_id: int = db.get_user_id(client_name, client_hashed_password)
                    send_string_to_client(new_client, str(user_id))

                    return [False if user_id == -1 else True, user_id]

        except:
            new_client.close()
            break



def handle_new_message(data: dict, 
                       clients: dict[str, socket.socket], 
                       db: ChatDatabase, 
                       user_id: int) -> None:
    sender_id = data.get('sender_id')
    content = data.get('content')
    chat_id = data.get('chat_id')
    author = db.get_username(user_id) 
    time = get_current_time()

    print('сообщение получено')
    print(data)

    db.save_new_message(sender_id, chat_id, content, time)
    data_to_broadcast = {
        'header': 'new_message',
        'time': time, 
        'content': content, 
        'username': author , 
        'chat_id': chat_id
    }
    broadcast_new_message(data_to_broadcast, clients, db)


def handle_creating_new_chat(data: dict, 
                       client: socket.socket, 
                       db: ChatDatabase, 
                       user_id: int):
    chat_name: str = data.get('chat_name') 
    if not chat_name: 
        return
    
    chat_id = db.create_new_chat(chat_name, user_id) 

    print('Проверка')

    data = {
        'header': 'new_chat', 
        
        'name': chat_name, 
        'id': chat_id, 
        'messages': db.get_messages_from_chat(chat_id),
    }
    send_json_to_client(client, data)


def handle_new_member(data: dict, clients: dict[str, socket.socket], db: ChatDatabase):
    chat_id = data.get('chat_id')
    member_id = data.get('member_id')
    if not chat_id or not member_id:
        return 
    db.add_new_membership(chat_id, member_id)
    print('Новый участник добавился')

    client = clients.get(str(member_id)) 
    if client:
        new_chat_data = db.get_single_chat_history(chat_id)
        data['header'] = 'new_chat'
        send_json_to_client(client, new_chat_data) 

    print('\nНовый чат для приглашённого участника')
    print(db.get_single_chat_history(chat_id))


    new_member_message = f'К чату присоединяется пользователь {db.get_username(member_id)}!'
    time_now = get_current_time()
    db.save_new_message(sender_id=1, 
                        chat_id=chat_id, 
                        content=new_member_message, 
                        time=time_now)

    message_about_new_member = {
        'header': 'new_message',
        'time': time_now, 
        'content': new_member_message, 
        'username': 'Чат', 
        'chat_id': chat_id
    }

    broadcast_new_message(message_about_new_member, clients, db)