from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import Boolean, Column, Float, String, Integer
import sqlite3

app = FastAPI()

# SqlAlchemy Setup
SQLALCHEMY_DATABASE_URL = 'sqlite:///./test.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# A SQLAlchemny ORM Place
class DBPlace(Base):
    __tablename__ = 'places'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    lat = Column(Float)
    lng = Column(Float)

Base.metadata.create_all(bind=engine)

# A Pydantic Place
class Place(BaseModel):
    name: str
    lat: float
    lng: float

    class Config:
        orm_mode = True

# Methods for interacting with the database
def get_place(db: Session, lat:float, lng:float):
    return db.query(DBPlace).where(DBPlace.lat == lat and DBPlace.lng == lng).first()

def put_place(db: Session, lat:float, lng:float, place: Place):
    data = db.query(DBPlace).where(DBPlace.lat == lat and DBPlace.lng == lng).first()
    conn = sqlite3.connect('test.db')
    conn.execute('''UPDATE places SET name='%s' WHERE lat = %d AND lng = %d''' % (place, lat, lng))
    conn.commit()
    return data

def delete_place(db: Session, place_id: int):
    data = db.query(DBPlace).where(DBPlace.id == place_id).first()
    conn = sqlite3.connect('test.db')
    conn.execute('''DELETE FROM places WHERE id = %d''' % (place_id))
    conn.commit()
    return data

def get_places(db: Session):
    return db.query(DBPlace).all()

def create_place(db: Session, place: Place):
    db_place = DBPlace(**place.dict())
    db.add(db_place)
    db.commit()
    db.refresh(db_place)

    return db_place



# Routes for interacting with the API
@app.post('/places/', response_model=Place)
def create_places_view(place: Place, db: Session = Depends(get_db)):
    db_place = create_place(db, place)
    return db_place

@app.get('/places/', response_model=List[Place])
def get_places_view(db: Session = Depends(get_db)):
    return get_places(db)

@app.get('/place/{lat},{lng}')
def get_place_view(lat: float, lng:float, db: Session = Depends(get_db)):
    return get_place(db, lat, lng)

@app.put('/place/{lat},{lng}', response_model=Place)
def put_place_view(lat: float, lng:float, name:str, db: Session = Depends(get_db)):
    return put_place(db, lat, lng, name)

@app.delete('/place/{place_id}')
def delete_place_view(place_id: int, db: Session = Depends(get_db)):
    return delete_place(db, place_id)

@app.get('/')
async def root():
    return {'message': 'Hello World!'}
