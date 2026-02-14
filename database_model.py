from sqlalchemy import Column, Integer, String
from database import Base

#we need to use the same class from model and map it to the database table and give a name to DB using the Base from DB file
#this is for the mapping of int to db int and str to db varchar and so on
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    quantity=Column(Integer)
    quality=Column(String)
    decs=Column(String)


   