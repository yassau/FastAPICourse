from fastapi import Depends, HTTPException, status, APIRouter
from app.models import User, UserCreate, UserPublic, UserPublicWithPosts
from app.database import get_session
from sqlmodel import Session
from app.utils import get_password_hash

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserPublicWithPosts)
def create_user(*, session: Session = Depends(get_session), user: UserCreate):
    hashed_password = get_password_hash(user.password)
    user.password = hashed_password
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.get("/{id}", response_model=UserPublicWithPosts)
def get_user(*, id: int, session: Session = Depends(get_session)):
    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} does not exist")
    return user