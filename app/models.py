from sqlalchemy import Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Channel(Base):
    __tablename__ = "channels"
    id = Column(String, primary_key=True, index=True, default=func.uuid_generate_v4())
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    client_id = Column(String, nullable=False)
    behaviorist_id = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    posts = relationship("Post", back_populates="channel", cascade="all, delete-orphan")
    events = relationship(
        "Event", back_populates="channel", cascade="all, delete-orphan"
    )


class Post(Base):
    __tablename__ = "posts"
    id = Column(String, primary_key=True, index=True, default=func.uuid_generate_v4())
    title = Column(String, index=True)
    content = Column(Text)
    channel_id = Column(String, ForeignKey("channels.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    author_id = Column(String, nullable=False)

    channel = relationship("Channel", back_populates="posts")
    comments = relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan"
    )


class Comment(Base):
    __tablename__ = "comments"
    id = Column(String, primary_key=True, index=True, default=func.uuid_generate_v4())
    content = Column(Text)
    post_id = Column(String, ForeignKey("posts.id"))
    author_id = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    post = relationship("Post", back_populates="comments")


class Media(Base):
    __tablename__ = "media"
    id = Column(String, primary_key=True, index=True, default=func.uuid_generate_v4())
    post_id = Column(String, ForeignKey("posts.id"), nullable=True)
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(String, nullable=False)

    post = relationship("Post", back_populates="media")


class Event(Base):
    __tablename__ = "events"
    id = Column(String, primary_key=True, index=True, default=func.uuid_generate_v4())
    channel_id = Column(String, ForeignKey("channels.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(String, nullable=False)

    channel = relationship("Channel", back_populates="events")
