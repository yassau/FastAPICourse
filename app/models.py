from datetime import datetime
from typing import Optional
from pydantic import EmailStr
from sqlalchemy.sql.expression import text
from sqlalchemy import TIMESTAMP
from sqlmodel import SQLModel, Field, Column, Relationship


class PostBase(SQLModel):
    title: str
    content: str
    published: bool = Field(default=True)
    owner_id : int | None = Field(default=None, foreign_key="users.id", ondelete="CASCADE")

class Post(PostBase, table=True):
    __tablename__ = "posts"
    id: int | None = Field(default=None, primary_key=True)
    created_at : datetime | None = Field(default=None, 
                                         sa_column=Column(TIMESTAMP(timezone=True),
                                                          nullable=False, 
                                                          server_default=text('now()')))
    owner: Optional["User"] = Relationship(back_populates="posts")

class PostCreate(PostBase):
    pass

class PostUpdate(SQLModel):
    title: str | None = None
    content: str | None = None
    published: bool

class PostPublic(PostBase):
    id: int
    created_at: datetime

class PostLikes(SQLModel):
    Post: Post
    likes: int | None = None
    #class Config:
    #    orm_mode = True

class PostPublicWithUser(PostPublic):
    owner: "UserPublic"

class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, nullable=False)
    password: str = Field(nullable=False)


class User(UserBase, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    created_at : datetime | None = Field(default=None, 
                                         sa_column=Column(TIMESTAMP(timezone=True), 
                                                          nullable=False, 
                                                          server_default=text('now()')))
    posts: list[Post] = Relationship(back_populates="owner", cascade_delete=True)
    
class UserCreate(UserBase):
    pass

class UserLogin(UserBase):
    pass

class UserPublic(SQLModel):
    id: int
    email: EmailStr
    created_at: datetime

class UserPublicWithPosts(UserPublic):
    posts: list[PostPublic] = []

class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    userem: str | None = None
    id: int | None = None


class PostsUsersLike(SQLModel, table=True):
    __tablename__ = "likes"
    post_id: int | None  = Field(default=None, foreign_key="posts.id",
                                 primary_key=True, ondelete="CASCADE")
    user_id: int | None = Field(default=None, foreign_key="users.id",
                                primary_key=True, ondelete="CASCADE")
    liked_at : datetime | None = Field(default=None, 
                                         sa_column=Column(TIMESTAMP(timezone=True),
                                                          nullable=False, 
                                                          server_default=text('now()')))
    
class Like(SQLModel):
    post_id: int
    dir: int




