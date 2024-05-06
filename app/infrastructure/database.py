from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = "postgresql://mlingo_user:RXiGZ7rE2eOnErs2b3uuXmgc64ILmAcB@dpg-cmocq4821fec73cvn300-a.oregon-postgres.render.com/mlingo"
SQLALCHEMY_DATABASE_URL = "postgresql://mlingo_vakq_user:EswdMUL4HuxAV22lsC82jE5xqn0vncmJ@dpg-cos5ami1hbls73fee8ng-a.oregon-postgres.render.com/mlingo_vakq"  # Aditi's local instance


engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
