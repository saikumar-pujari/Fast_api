#depends is used to inject dependencies into the route functions, allowing us to manage database sessions and other resources efficiently.
from fastapi import FastAPI,Depends
#this to allow the froted data to use the backend api without any cors error
from fastapi.middleware.cors import CORSMiddleware
#products is a Pydantic model that defines the structure of the product data we will be working with in our API.
from models import products
#SessionLocal is a SQLAlchemy session factory that we will use to create database sessions for interacting with our database. engine is the SQLAlchemy engine that connects to our database.
from database import SessionLocal,engine
#custom build query to match the models and database tables, allowing us to perform CRUD operations on the product data stored in the database.
import database_model

#the app object is an instance of the FastAPI class, which serves as the main entry point  for our API. We will define our route handlers and other configurations on this app object.
app=FastAPI()

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"],  # Allow all origins (for development only) #it means that any frontend application, regardless of its domain, can make requests to this API. This is useful during development when you might be running the frontend and backend on different local servers.if the fronted url is http://localhost:3000, you can set allow_origins=["http://localhost:3000"] to restrict access to only that origin.   
    allow_methods=["*"],  # Allow all HTTP methods (POST, GET, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers (including Authorization, Content-Type, etc.)
)

#just a simple route to check if the API is running, returning a JSON response with a status message.
product = [
    products(name="skipper", quantity=56, quality="medium", decs="the skipper is a medium quality product with a quantity of 56"),
]

#This line creates the database tables based on the models defined in database_model. It uses SQLAlchemy's metadata to create the necessary tables in the database if they do not already exist.
database_model.Base.metadata.create_all(bind=engine)

#get_db is a dependency function that creates a new database session for each request and ensures that the session is properly closed after the request is processed. This allows us to manage database connections efficiently and avoid potential issues with open connections.
def get_db():
   db = SessionLocal()
   try:
       yield db
   finally:
       db.close()

#init_db is a function that initializes the database with some initial data. It creates a new database session, adds the products defined in the product list to the database, and commits the changes. Finally, it ensures that the database session is closed properly.
def init_db():
    db = SessionLocal()
    try:
        for pro in product:
            #pro.model_dump() is a method provided by Pydantic models that returns a dictionary representation of the model's data. **upacks the dictionary returned by model_dump() and passes it as keyword arguments to the Product constructor, allowing us to create a new Product instance with the data from the Pydantic model. 
            db.add(database_model.Product(**pro.model_dump()))
        db.commit()
    finally:
        db.close()
#we need to call the init_db() function to populate the database with the initial product data when the application starts. This ensures that we have some data to work with when we test our API endpoints.
init_db()

#just a example
@app.get('/')
def gree():
    return "Hello, World!"

#gets all products from the database and returns them as a JSON response. It uses the get_db dependency to create a database session and queries the Product table to retrieve all products.
@app.get('/value')
def value(db:SessionLocal=Depends(get_db)):
    db_products=db.query(database_model.Product).all()
    return db_products

#gets a specific product by its ID from the database. 
@app.get('/value/{id}')
def value_id(id:int, db:SessionLocal=Depends(get_db)):
    db_product=db.query(database_model.Product).filter(database_model.Product.id==id).first()
    return db_product if db_product else {"error": "Product not found"}

#adds a new product to the database. or take a input to new product
@app.post('/value ')
def add_pro(new_product:products, db:SessionLocal=Depends(get_db)):
    db_product = database_model.Product(**new_product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

#updates the exisitng product
@app.put('/value/{id}')
def update_pro(id:int, updated_product:products, db:SessionLocal=Depends(get_db)):
    db_product = db.query(database_model.Product).filter(database_model.Product.id==id).first()
    if db_product:
        for key, value in updated_product.model_dump().items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
        return db_product
    return {"error": "Product not found"}   

#delets the exisiting specific product
@app.delete('/value/{id}')
def delete_pro(id:int, db:SessionLocal=Depends(get_db)):
    db_product = db.query(database_model.Product).filter(database_model.Product.id==id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return {"message": "Product deleted successfully"}
    return {"error": "Product not found"}