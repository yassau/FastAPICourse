from fastapi import Depends, HTTPException, Query, APIRouter, status
from app.models import PostLikes, PostUpdate, Post, PostCreate, PostPublic, PostsUsersLike, User, PostPublicWithUser
from app.database import get_session
from app.oauth2 import get_current_user
from sqlmodel import Session, select
from typing import Optional
from sqlalchemy import func

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

@router.post("/", response_model=PostPublic)
def create_post(*, session: Session = Depends(get_session), post: PostCreate,
                current_user: User = Depends(get_current_user)):
    post.owner_id = current_user.id
    db_post = Post.model_validate(post)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


@router.get("/", response_model=list[PostLikes])
def get_posts(
    *,
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = Query(default=10, le=100),
    current_user: User = Depends(get_current_user),
    search: Optional[str]  = ""):
    statement = select(Post, func.count(PostsUsersLike.post_id).label("likes")).join(PostsUsersLike, 
        isouter=True).group_by(Post.id).where(Post.title.like('%'+ search + '%')).offset(skip).limit(limit)
    posts = session.exec(statement).all()
    return posts



@router.get("/{id}", response_model=PostPublicWithUser)
def get_post(*, session: Session = Depends(get_session), id: int, 
             current_user: User = Depends(get_current_user)):
    post = session.get(Post, id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post

@router.delete("/{id}")
def delete_post(*, session: Session = Depends(get_session), id: int,
    current_user: User = Depends(get_current_user)):
    post = session.get(Post, id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.owner != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized")
    session.delete(post)
    session.commit()
    return {"ok": True}
    
@router.put("/{id}", response_model=PostPublicWithUser)
def update_post(*, session: Session = Depends(get_session), id: int, post: PostUpdate,
                current_user: User = Depends(get_current_user)):
    db_post = session.get(Post, id)
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if db_post.owner != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized")
    post_data = post.model_dump(exclude_unset=True)
    for key, value in post_data.items():
        setattr(db_post, key, value)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post