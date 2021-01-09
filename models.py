# users -> userid, username, usertype, password
# ticketprice -> userid, count, price
# movies -> movieid, moviename, director

from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Unicode,
    Boolean,
    Text,
    DateTime,
    VARCHAR,
    Numeric,
    BigInteger,
    Float,
)

engine = create_engine(
    r"mysql+mysqldb://root:root@localhost:3306/ticketsystem", echo=False
)

Base = declarative_base()


class User(Base):

    __tablename__ = "users"
    userid = Column(Integer, primary_key=True)
    username = Column(String(15), unique=True)
    usertype = Column(Boolean)
    password_hash = Column(VARCHAR(128))

    @classmethod
    def create_password(cls, password):
        cls.password_hash = generate_password_hash(password)
        return cls.password_hash

    @classmethod
    def check_password_after_signup(cls, password, password_hash):
        return check_password_hash(password_hash, password)

    @classmethod
    def check_password_before_signup(cls, password):
        return check_password_hash(cls.password_hash, password)

    def __repr__(self):
        return str(self.userid) + ":" + self.username


class customer(Base):
    __tablename__ = "customer"
    userid = Column(Integer, primary_key=True)
    username = Column(String(15))
    name = Column(String(15))
    gender = Column(String(1))
    age = Column(Integer)
    phone = Column(VARCHAR(15))
    tickets_bought = Column(Integer)
    totalspent = Column(Integer)


class Tickets_price(Base):
    __tablename__ = "ticket_price"
    userid = Column(Integer, primary_key=True)
    amount = Column(Integer)
    price = Column(Integer)


class movies(Base):
    __tablename__ = "movies"
    movieid = Column(Integer, primary_key=True)
    name = Column(Text)
    director = Column(String(30))

    def __repr__(self):
        return self.name + " directed by " + self.director


class seats(Base):
    __tablename__ = "seats"
    seatid = Column(Integer, primary_key=True)
    seat_row = Column(Integer)
    seat_column = Column(Integer)
    status = Column(String(1))


Base.metadata.create_all(bind=engine)