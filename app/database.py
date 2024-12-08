from sqlmodel import Session, create_engine
from app.config import settings as s

SQLMODEL_DATABASE_URL = f'postgresql://{s.database_username}:{s.database_password}@{s.database_hostname}:{s.database_port}/{s.database_name}'

engine = create_engine(SQLMODEL_DATABASE_URL, echo=True)

#def create_db_and_tables():
    #SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
