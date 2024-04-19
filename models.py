from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, select, join
from sqlalchemy.orm import declarative_base, create_session, relationship, Session, sessionmaker

from config import DB_URL

base = declarative_base()


class User(base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False) 

    messages = relationship('Message', back_populates='user')
    chatmembers = relationship('ChatMember', back_populates='user')


class Chat(base):
    __tablename__ = "Chat"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    messages = relationship('Message', back_populates='chat')
    chatmembers = relationship('ChatMember', back_populates='chat')


class Message(base):
    __tablename__ = 'Message'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    content = Column(String, nullable=False)
    time = Column(String, nullable=False)
    sender_id = Column(Integer, ForeignKey(User.id), nullable=False)
    chat_id = Column(Integer, ForeignKey(Chat.id), nullable=False)

    user = relationship('User', back_populates='messages') 
    chat = relationship('Chat', back_populates='messages')


class ChatMember(base):
    __tablename__ = 'ChatMember'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id))
    chat_id = Column(Integer, ForeignKey(Chat.id))

    user = relationship('User', back_populates='chatmembers')
    chat = relationship('Chat', back_populates='chatmembers')
        

if __name__ == "__main__":
    base.metadata.create_all(create_engine(DB_URL, echo=False)) 