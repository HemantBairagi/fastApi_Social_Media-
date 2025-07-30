from typing import List, Optional

from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, Enum, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, Text, UniqueConstraint, Uuid, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime
import uuid

class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        CheckConstraint('followers >= 0', name='chk_followers_nonnegative'),
        CheckConstraint('following >= 0', name='chk_following_nonnegative'),
        PrimaryKeyConstraint('id', name='users_pkey'),
        UniqueConstraint('email', name='users_email_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(40))
    email: Mapped[str] = mapped_column(String(50))
    phone: Mapped[Optional[int]] = mapped_column(BigInteger)
    bio: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_online: Mapped[Optional[bool]] = mapped_column(Boolean)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    profile_picture: Mapped[Optional[str]] = mapped_column(Text)
    followers: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    following: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))

    conversations: Mapped[List['Conversations']] = relationship('Conversations', back_populates='creator')
    follow: Mapped[List['Follow']] = relationship('Follow', foreign_keys='[Follow.follower_id]', back_populates='follower')
    follow_: Mapped[List['Follow']] = relationship('Follow', foreign_keys='[Follow.following_id]', back_populates='following')
    posts: Mapped[List['Posts']] = relationship('Posts', back_populates='user')
    comment: Mapped[List['Comment']] = relationship('Comment', back_populates='user')
    conversation_participants: Mapped[List['ConversationParticipants']] = relationship('ConversationParticipants', back_populates='user')
    likes: Mapped[List['Likes']] = relationship('Likes', back_populates='user')
    messages: Mapped[List['Messages']] = relationship('Messages', back_populates='sender')


class Conversations(Base):
    __tablename__ = 'conversations'
    __table_args__ = (
        ForeignKeyConstraint(['creator_id'], ['users.id'], name='conversations_creator_id_fkey'),
        PrimaryKeyConstraint('room_id', name='conversations_pkey')
    )

    room_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    is_group: Mapped[Optional[bool]] = mapped_column(Boolean)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    creator_id: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    creator: Mapped[Optional['Users']] = relationship('Users', back_populates='conversations')
    conversation_participants: Mapped[List['ConversationParticipants']] = relationship('ConversationParticipants', back_populates='room')
    messages: Mapped[List['Messages']] = relationship('Messages', back_populates='room')


class Follow(Base):
    __tablename__ = 'follow'
    __table_args__ = (
        CheckConstraint('follower_id <> following_id', name='not_same_follower'),
        ForeignKeyConstraint(['follower_id'], ['users.id'], name='follow_follower_id_fkey'),
        ForeignKeyConstraint(['following_id'], ['users.id'], name='follow_following_id_fkey'),
        PrimaryKeyConstraint('follower_id', 'following_id', name='follow_pkey')
    )

    follower_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    following_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    follower: Mapped['Users'] = relationship('Users', foreign_keys=[follower_id], back_populates='follow')
    following: Mapped['Users'] = relationship('Users', foreign_keys=[following_id], back_populates='follow_')


class Posts(Base):
    __tablename__ = 'posts'
    __table_args__ = (
        CheckConstraint('likes >= 0', name='chk_likes_nonnegative'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='posts_user_id_fkey'),
        PrimaryKeyConstraint('id', name='posts_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    post_type: Mapped[Optional[str]] = mapped_column(Enum('text', 'image', 'video', name='posttype'))
    post_text: Mapped[Optional[str]] = mapped_column(String(1000))
    likes: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    user: Mapped[Optional['Users']] = relationship('Users', back_populates='posts')
    comment: Mapped[List['Comment']] = relationship('Comment', back_populates='post')
    likes_: Mapped[List['Likes']] = relationship('Likes', back_populates='post')


class Comment(Base):
    __tablename__ = 'comment'
    __table_args__ = (
        ForeignKeyConstraint(['post_id'], ['posts.id'], ondelete='CASCADE', name='comment_post_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='comment_user_id_fkey'),
        PrimaryKeyConstraint('id', name='comment_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    post_id: Mapped[Optional[int]] = mapped_column(Integer)
    comment_type: Mapped[Optional[str]] = mapped_column(Enum('GIF', 'TEXT', name='commenttype'))
    comment: Mapped[Optional[str]] = mapped_column(Text)
    likes: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    post: Mapped[Optional['Posts']] = relationship('Posts', back_populates='comment')
    user: Mapped[Optional['Users']] = relationship('Users', back_populates='comment')


class ConversationParticipants(Base):
    __tablename__ = 'conversation_participants'
    __table_args__ = (
        ForeignKeyConstraint(['room_id'], ['conversations.room_id'], ondelete='CASCADE', name='conversation_participants_room_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='conversation_participants_user_id_fkey'),
        PrimaryKeyConstraint('id', name='conversation_participants_pkey'),
        UniqueConstraint('room_id', 'user_id', name='conversation_participants_room_id_user_id_key')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    room_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    user_id: Mapped[int] = mapped_column(Integer)

    room: Mapped['Conversations'] = relationship('Conversations', back_populates='conversation_participants')
    user: Mapped['Users'] = relationship('Users', back_populates='conversation_participants')


class Likes(Base):
    __tablename__ = 'likes'
    __table_args__ = (
        ForeignKeyConstraint(['post_id'], ['posts.id'], ondelete='CASCADE', name='likes_post_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='likes_user_id_fkey'),
        PrimaryKeyConstraint('user_id', 'post_id', name='likes_pkey')
    )

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    post: Mapped['Posts'] = relationship('Posts', back_populates='likes_')
    user: Mapped['Users'] = relationship('Users', back_populates='likes')


class Messages(Base):
    __tablename__ = 'messages'
    __table_args__ = (
        ForeignKeyConstraint(['room_id'], ['conversations.room_id'], ondelete='CASCADE', name='messages_room_id_fkey'),
        ForeignKeyConstraint(['sender_id'], ['users.id'], name='messages_sender_id_fkey'),
        PrimaryKeyConstraint('message_id', name='messages_pkey')
    )

    message_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    room_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    sender_id: Mapped[int] = mapped_column(Integer)
    content: Mapped[Optional[str]] = mapped_column(Text)
    sent_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    room: Mapped['Conversations'] = relationship('Conversations', back_populates='messages')
    sender: Mapped['Users'] = relationship('Users', back_populates='messages')
