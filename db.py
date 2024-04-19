from models import *
from contextlib import contextmanager


class ChatDatabase:
    def __init__(self):
        self._engine = create_engine(DB_URL, echo=False)
        self._Session = sessionmaker(bind=self._engine, autoflush=False)

    @contextmanager
    def get_db_session(self) -> Session: # type: ignore
        session = self._Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


    def get_username(self, user_id: int) -> str:
        with self.get_db_session() as db_session:
            user = db_session.query(User).filter_by(id=user_id).first()
            return user.name if user else None
        

    def create_user(self, name: str, hashed_password: str) -> None:
        new_user = User(name=name, hashed_password=hashed_password)
        with self.get_db_session() as db_session:
            db_session.add(new_user)            


    def save_new_message(self, sender_id: int, chat_id: int, content: str, time: str) -> None:
        with self.get_db_session() as db_session:
            message = Message(content=content, time=time, sender_id=sender_id, chat_id=chat_id)
            db_session.add(message)


    def user_exists(self, name: str, hashed_password: str) -> bool:
        with self.get_db_session() as db_session:
            user = db_session.query(User).where(User.name == name).where(User.hashed_password == hashed_password).first()
        return True if user else False
    

    def get_user_id(self, name: str, hashed_password: str) -> int | None:
        with self.get_db_session() as db_session:
            user_id: int | None = db_session.query(User.id).where(User.name == name).where(User.hashed_password == hashed_password).first()
            return user_id[0] if user_id else -1
        

    def get_chats_by_user(self, member_id: int) -> list[int]:
        with self.get_db_session() as db_session:
            chat_ids = [chat_id for (chat_id,) in db_session.query(ChatMember.chat_id).where(ChatMember.user_id == member_id).all()]
            return chat_ids
        

    def get_users_by_chat(self, chat_id: int) -> list[int]:
        with self.get_db_session() as db_session:
            db_session: Session
            users_tuples: list[tuple[int]] = db_session.query(ChatMember.user_id).where(ChatMember.chat_id == chat_id).all()
            users: list[int] = [user_tuple[0] for user_tuple in users_tuples]
            return users
        

    def get_messages_from_chat(self, chat_id: int) -> list[dict]:
        with self.get_db_session() as db_session:
            result = db_session.execute(
                select(Message.content, Message.time, User.name)  
                .select_from(join(Message, User, Message.sender_id == User.id)) 
                .where(Message.chat_id == chat_id)  
            ).all()
        
            messages: list[dict] = [{
                    'time': row[1], 
                    'content': row[0], 
                    'sender_name': row[2]
                } 
                for row in result
            ]

            return messages 
        

    def get_chats_history(self, user_id): 
        chats_and_messages = []
        with self.get_db_session() as db_session:
            user = db_session.query(User).filter(User.id == user_id).first()
            if user:
                # Собираем уникальные идентификаторы чатов
                unique_chat_ids = set()
                for chat_member in user.chatmembers:
                    unique_chat_ids.add(chat_member.chat.id)

                # Обходим все уникальные чаты
                for chat_id in unique_chat_ids:
                    chat_data = {
                        "id": None,
                        "name": None,
                        "messages": []
                    }
                    # Получаем данные о чате
                    chat = db_session.query(Chat).filter(Chat.id == chat_id).first()
                    if chat:
                        chat_data["id"] = chat.id
                        chat_data["name"] = chat.name

                        for message in chat.messages:
                            chat_data["messages"].append({
                                "time": message.time,
                                "content": message.content,
                                "sender_name": message.user.name
                            })
                        chats_and_messages.append(chat_data)
        return chats_and_messages
    

    def get_single_chat_history(self, chat_id: int) -> dict:
        with self.get_db_session() as db_session:
            chat_data = {
                            "id": None,
                            "name": None,
                            "messages": []
                        }
                        # Получаем данные о чате
            chat = db_session.query(Chat).filter(Chat.id == chat_id).first()
            if chat:
                chat_data["id"] = chat.id
                chat_data["name"] = chat.name

                for message in chat.messages:
                    chat_data["messages"].append({
                        "time": message.time,
                        "content": message.content,
                        "sender_name": message.user.name
                    })
            return chat_data


    def create_new_chat(self, chat_name: str, creator_id: int) -> int:
        with self.get_db_session() as db_session:
            new_chat = Chat(name=chat_name)
            db_session.add(new_chat)
            db_session.commit()

            creator_membership = ChatMember(chat_id=new_chat.id, user_id=creator_id)
            db_session.add(creator_membership)

            return new_chat.id
        
    def add_new_membership(self, chat_id: int, user_id: int) -> None:
        with self.get_db_session() as db_session:
            db_session: Session 

            new_membership = ChatMember(user_id=user_id, chat_id=chat_id)
            db_session.add(new_membership) 
            db_session.commit()
            return
        
    def get_chat_name(self, chat_id: int) -> str:
        with self.get_db_session() as db_session:
            db_session: Session 
            chat = db_session.query(Chat).filter_by(id=chat_id).first()

            return chat.name


if __name__ == "__main__":
    db = ChatDatabase()

    print(db.get_single_chat_history(4))