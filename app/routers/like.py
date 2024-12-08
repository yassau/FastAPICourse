from fastapi import Depends, HTTPException, status, APIRouter
from app.models import Like, User, PostsUsersLike, Post
from app.database import get_session
from sqlmodel import Session, select
from app.oauth2 import get_current_user

router = APIRouter(
    prefix="/like",
    tags=['Like']
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def like(like: Like, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    post = session.exec(select(Post).where(Post.id == like.post_id)).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post doesn't exist")

    check_like = session.exec(select(PostsUsersLike).where(PostsUsersLike.post_id == like.post_id,
                                                           PostsUsersLike.user_id == current_user.id)).first()
    if like.dir == 1:
        if check_like:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user {current_user.email} has already liked this post")
        new_like = PostsUsersLike(post_id=like.post_id, user_id=current_user.id)
        session.add(new_like)
        session.commit()
        return {"message": "successfuly liked post"}
    else:
        if not check_like:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user hasn't liked this post yet")
        session.delete(check_like)
        session.commit()
        return {"message": "successfuly unliked post"}
        