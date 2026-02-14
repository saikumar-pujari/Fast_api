# FastAPI Complete Guide 🚀

A comprehensive guide to building a full-stack application with FastAPI, covering everything from setup to deployment.

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Database Configuration](#database-configuration)
- [Models & Schemas](#models--schemas)
- [CRUD Operations](#crud-operations)
- [API Endpoints](#api-endpoints)
- [Frontend Integration](#frontend-integration)
- [Running the Application](#running-the-application)
- [Testing](#testing)

---

## 🎯 Overview

This FastAPI application provides a complete backend solution with:
- RESTful API endpoints (GET, POST, PUT, DELETE)
- Database integration with SQLAlchemy ORM
- Pydantic models for data validation
- Custom database operations
- Frontend connectivity support
- Automatic API documentation

---

## 📁 Project Structure

```
fastapi-project/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── database.py             # Database connection and session
│   ├── models.py               # SQLAlchemy ORM models
│   ├── schemas.py              # Pydantic schemas for validation
│   ├── crud.py                 # Database operations (CRUD)
│   ├── db_custom.py            # Custom database queries
│   │
│   └── routers/
│       ├── __init__.py
│       └── items.py            # API route handlers
│
├── requirements.txt
├── .env                        # Environment variables
└── README.md
```

---

## 🔧 Installation & Setup

### 1. Prerequisites

- Python 3.8+
- PostgreSQL/MySQL/SQLite
- pip or poetry

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install packages
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv pydantic
```

### 3. Create `requirements.txt`

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
```

### 4. Environment Variables

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/dbname
# For SQLite (development)
# DATABASE_URL=sqlite:///./test.db

# For MySQL
# DATABASE_URL=mysql+pymysql://username:password@localhost:3306/dbname

SECRET_KEY=your-secret-key-here
DEBUG=True
```

---

## 🗄️ Database Configuration

### `app/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# Database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine
engine = create_engine(
    DATABASE_URL,
    # For SQLite only:
    # connect_args={"check_same_thread": False}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Creating Tables

```python
# Run this once to create all tables
from app.database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)
```

---

## 📊 Models & Schemas

### `app/models.py` - SQLAlchemy ORM Models

```python
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    owner = relationship("User", back_populates="items")
```

### `app/schemas.py` - Pydantic Schemas

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# Item Schemas
class ItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    is_available: bool = True

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    is_available: Optional[bool] = None

class Item(ItemBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    items: List[Item] = []
    
    class Config:
        from_attributes = True
```

---

## 🔄 CRUD Operations

### `app/crud.py` - Standard Database Operations

```python
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app import models, schemas

# ============= USER CRUD =============

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """GET single user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """GET user by email"""
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """GET all users with pagination"""
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """POST - Create new user"""
    # Hash password here (use bcrypt or passlib)
    hashed_password = user.password + "_hashed"  # Placeholder
    
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    """PUT - Update user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """DELETE user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True


# ============= ITEM CRUD =============

def get_item(db: Session, item_id: int) -> Optional[models.Item]:
    """GET single item by ID"""
    return db.query(models.Item).filter(models.Item.id == item_id).first()

def get_items(db: Session, skip: int = 0, limit: int = 100) -> List[models.Item]:
    """GET all items with pagination"""
    return db.query(models.Item).offset(skip).limit(limit).all()

def get_items_by_user(db: Session, user_id: int) -> List[models.Item]:
    """GET all items for a specific user"""
    return db.query(models.Item).filter(models.Item.owner_id == user_id).all()

def create_item(db: Session, item: schemas.ItemCreate, user_id: int) -> models.Item:
    """POST - Create new item"""
    db_item = models.Item(**item.model_dump(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_item(db: Session, item_id: int, item_update: schemas.ItemUpdate) -> Optional[models.Item]:
    """PUT - Update item"""
    db_item = get_item(db, item_id)
    if not db_item:
        return None
    
    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int) -> bool:
    """DELETE item"""
    db_item = get_item(db, item_id)
    if not db_item:
        return False
    
    db.delete(db_item)
    db.commit()
    return True
```

### `app/db_custom.py` - Custom Database Queries

```python
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from app import models

class CustomQueries:
    """Custom database queries for complex operations"""
    
    @staticmethod
    def search_items(
        db: Session, 
        query: str, 
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[models.Item]:
        """Search items by title/description with price filtering"""
        filters = [
            or_(
                models.Item.title.ilike(f"%{query}%"),
                models.Item.description.ilike(f"%{query}%")
            )
        ]
        
        if min_price is not None:
            filters.append(models.Item.price >= min_price)
        if max_price is not None:
            filters.append(models.Item.price <= max_price)
        
        return db.query(models.Item).filter(and_(*filters)).all()
    
    @staticmethod
    def get_user_statistics(db: Session, user_id: int) -> Dict:
        """Get statistics for a user"""
        total_items = db.query(func.count(models.Item.id))\
            .filter(models.Item.owner_id == user_id).scalar()
        
        available_items = db.query(func.count(models.Item.id))\
            .filter(
                and_(
                    models.Item.owner_id == user_id,
                    models.Item.is_available == True
                )
            ).scalar()
        
        total_value = db.query(func.sum(models.Item.price))\
            .filter(models.Item.owner_id == user_id).scalar() or 0
        
        avg_price = db.query(func.avg(models.Item.price))\
            .filter(models.Item.owner_id == user_id).scalar() or 0
        
        return {
            "total_items": total_items,
            "available_items": available_items,
            "total_value": float(total_value),
            "average_price": float(avg_price)
        }
    
    @staticmethod
    def get_recent_items(db: Session, days: int = 7) -> List[models.Item]:
        """Get items created in the last N days"""
        date_threshold = datetime.utcnow() - timedelta(days=days)
        return db.query(models.Item)\
            .filter(models.Item.created_at >= date_threshold)\
            .order_by(models.Item.created_at.desc())\
            .all()
    
    @staticmethod
    def get_expensive_items(db: Session, threshold: float = 100.0) -> List[models.Item]:
        """Get items above a price threshold"""
        return db.query(models.Item)\
            .filter(models.Item.price >= threshold)\
            .order_by(models.Item.price.desc())\
            .all()
    
    @staticmethod
    def bulk_update_availability(
        db: Session, 
        item_ids: List[int], 
        is_available: bool
    ) -> int:
        """Bulk update availability status for multiple items"""
        result = db.query(models.Item)\
            .filter(models.Item.id.in_(item_ids))\
            .update({"is_available": is_available}, synchronize_session=False)
        db.commit()
        return result
    
    @staticmethod
    def get_items_with_owner_info(db: Session) -> List[Dict]:
        """Get items with their owner information using JOIN"""
        results = db.query(
            models.Item.id,
            models.Item.title,
            models.Item.price,
            models.User.username,
            models.User.email
        ).join(models.User).all()
        
        return [
            {
                "item_id": r.id,
                "title": r.title,
                "price": r.price,
                "owner_username": r.username,
                "owner_email": r.email
            }
            for r in results
        ]
```

---

## 🛣️ API Endpoints

### `app/routers/items.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app import crud, schemas, models
from app.database import get_db
from app.db_custom import CustomQueries

router = APIRouter(
    prefix="/api/items",
    tags=["items"]
)

# ============= GET ENDPOINTS =============

@router.get("/", response_model=List[schemas.Item])
def read_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    GET all items with pagination
    
    - **skip**: Number of items to skip (default: 0)
    - **limit**: Maximum number of items to return (default: 100)
    """
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


@router.get("/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    """
    GET single item by ID
    
    - **item_id**: The ID of the item to retrieve
    """
    item = crud.get_item(db, item_id=item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    return item


@router.get("/user/{user_id}", response_model=List[schemas.Item])
def read_user_items(user_id: int, db: Session = Depends(get_db)):
    """
    GET all items for a specific user
    
    - **user_id**: The ID of the user
    """
    items = crud.get_items_by_user(db, user_id=user_id)
    return items


@router.get("/search/query")
def search_items(
    q: str = Query(..., min_length=1),
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    CUSTOM QUERY - Search items by keyword with price filtering
    
    - **q**: Search query string
    - **min_price**: Minimum price filter (optional)
    - **max_price**: Maximum price filter (optional)
    """
    items = CustomQueries.search_items(db, q, min_price, max_price)
    return items


@router.get("/recent/{days}")
def get_recent_items(days: int = 7, db: Session = Depends(get_db)):
    """
    CUSTOM QUERY - Get items created in the last N days
    
    - **days**: Number of days to look back (default: 7)
    """
    items = CustomQueries.get_recent_items(db, days=days)
    return items


# ============= POST ENDPOINTS =============

@router.post("/", response_model=schemas.Item, status_code=status.HTTP_201_CREATED)
def create_item(
    item: schemas.ItemCreate,
    user_id: int = Query(..., description="ID of the item owner"),
    db: Session = Depends(get_db)
):
    """
    POST - Create a new item
    
    - **item**: Item data (title, description, price, is_available)
    - **user_id**: ID of the user who owns this item
    """
    # Check if user exists
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    return crud.create_item(db=db, item=item, user_id=user_id)


# ============= PUT ENDPOINTS =============

@router.put("/{item_id}", response_model=schemas.Item)
def update_item(
    item_id: int,
    item_update: schemas.ItemUpdate,
    db: Session = Depends(get_db)
):
    """
    PUT - Update an existing item
    
    - **item_id**: ID of the item to update
    - **item_update**: Fields to update (all optional)
    """
    updated_item = crud.update_item(db, item_id=item_id, item_update=item_update)
    if updated_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    return updated_item


@router.put("/bulk/availability")
def bulk_update_availability(
    item_ids: List[int],
    is_available: bool,
    db: Session = Depends(get_db)
):
    """
    CUSTOM QUERY - Bulk update availability for multiple items
    
    - **item_ids**: List of item IDs to update
    - **is_available**: New availability status
    """
    count = CustomQueries.bulk_update_availability(db, item_ids, is_available)
    return {
        "message": f"Updated {count} items",
        "updated_count": count
    }


# ============= DELETE ENDPOINTS =============

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """
    DELETE an item
    
    - **item_id**: ID of the item to delete
    """
    success = crud.delete_item(db, item_id=item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    return None
```

### `app/main.py` - Main Application

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import items

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="FastAPI Complete Guide",
    description="A comprehensive FastAPI application with full CRUD operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React
        "http://localhost:5173",  # Vite
        "http://localhost:8080",  # Vue
        "http://localhost:4200",  # Angular
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(items.router)

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to FastAPI Complete Guide",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

---

## 🌐 Frontend Integration

### JavaScript/TypeScript (Fetch API)

```javascript
const API_BASE_URL = "http://localhost:8000/api";

// ============= GET REQUESTS =============

// Get all items
async function getItems() {
    const response = await fetch(`${API_BASE_URL}/items?skip=0&limit=100`);
    const data = await response.json();
    console.log(data);
    return data;
}

// Get single item
async function getItem(itemId) {
    const response = await fetch(`${API_BASE_URL}/items/${itemId}`);
    if (!response.ok) {
        throw new Error(`Item not found: ${response.status}`);
    }
    const data = await response.json();
    return data;
}

// Search items
async function searchItems(query, minPrice, maxPrice) {
    const params = new URLSearchParams({
        q: query,
        ...(minPrice && { min_price: minPrice }),
        ...(maxPrice && { max_price: maxPrice })
    });
    
    const response = await fetch(`${API_BASE_URL}/items/search/query?${params}`);
    const data = await response.json();
    return data;
}

// ============= POST REQUESTS =============

// Create new item
async function createItem(itemData, userId) {
    const response = await fetch(`${API_BASE_URL}/items?user_id=${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(itemData)
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail);
    }
    
    const data = await response.json();
    return data;
}

// Example usage:
const newItem = {
    title: "New Product",
    description: "Product description",
    price: 29.99,
    is_available: true
};
createItem(newItem, 1);

// ============= PUT REQUESTS =============

// Update item
async function updateItem(itemId, updateData) {
    const response = await fetch(`${API_BASE_URL}/items/${itemId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData)
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail);
    }
    
    const data = await response.json();
    return data;
}

// Example usage:
const updates = {
    price: 39.99,
    is_available: false
};
updateItem(1, updates);

// ============= DELETE REQUESTS =============

// Delete item
async function deleteItem(itemId) {
    const response = await fetch(`${API_BASE_URL}/items/${itemId}`, {
        method: 'DELETE'
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail);
    }
    
    return true;
}

// Example usage:
deleteItem(1);
```

### React Example (with Axios)

```javascript
import axios from 'axios';
import { useState, useEffect } from 'react';

const API_BASE_URL = "http://localhost:8000/api";

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    }
});

function ItemsComponent() {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // GET - Fetch items
    useEffect(() => {
        fetchItems();
    }, []);

    const fetchItems = async () => {
        setLoading(true);
        try {
            const response = await api.get('/items');
            setItems(response.data);
            setError(null);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    // POST - Create item
    const handleCreateItem = async (itemData, userId) => {
        try {
            const response = await api.post(`/items?user_id=${userId}`, itemData);
            setItems([...items, response.data]);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        }
    };

    // PUT - Update item
    const handleUpdateItem = async (itemId, updateData) => {
        try {
            const response = await api.put(`/items/${itemId}`, updateData);
            setItems(items.map(item => 
                item.id === itemId ? response.data : item
            ));
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        }
    };

    // DELETE - Remove item
    const handleDeleteItem = async (itemId) => {
        try {
            await api.delete(`/items/${itemId}`);
            setItems(items.filter(item => item.id !== itemId));
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        }
    };

    return (
        <div>
            {loading && <p>Loading...</p>}
            {error && <p>Error: {error}</p>}
            
            {items.map(item => (
                <div key={item.id}>
                    <h3>{item.title}</h3>
                    <p>{item.description}</p>
                    <p>Price: ${item.price}</p>
                    <button onClick={() => handleUpdateItem(item.id, { price: 50 })}>
                        Update Price
                    </button>
                    <button onClick={() => handleDeleteItem(item.id)}>
                        Delete
                    </button>
                </div>
            ))}
        </div>
    );
}
```

### Python Client Example

```python
import requests

API_BASE_URL = "http://localhost:8000/api"

# GET request
response = requests.get(f"{API_BASE_URL}/items")
items = response.json()

# POST request
new_item = {
    "title": "New Item",
    "description": "Description",
    "price": 29.99,
    "is_available": True
}
response = requests.post(
    f"{API_BASE_URL}/items?user_id=1",
    json=new_item
)
created_item = response.json()

# PUT request
update_data = {"price": 39.99}
response = requests.put(
    f"{API_BASE_URL}/items/1",
    json=update_data
)
updated_item = response.json()

# DELETE request
response = requests.delete(f"{API_BASE_URL}/items/1")
```

---

## 🚀 Running the Application

### Development Server

```bash
# Standard run
uvicorn app.main:app --reload

# Custom host and port
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# With auto-reload on file changes
uvicorn app.main:app --reload --reload-dir app
```

### Access the Application

- **API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **API Base URL**: http://localhost:8000/api

### Create Database Tables

```python
# Run this Python script once to create tables
from app.database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)
```

Or create a migration script:

```bash
# alembic_init.py
from app.database import engine
from app.models import Base

if __name__ == "__main__":
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
```

---

## 🧪 Testing

### Manual Testing with cURL

```bash
# GET all items
curl -X GET "http://localhost:8000/api/items" -H "accept: application/json"

# GET single item
curl -X GET "http://localhost:8000/api/items/1" -H "accept: application/json"

# POST create item
curl -X POST "http://localhost:8000/api/items?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Item",
    "description": "A test item",
    "price": 19.99,
    "is_available": true
  }'

# PUT update item
curl -X PUT "http://localhost:8000/api/items/1" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 29.99,
    "is_available": false
  }'

# DELETE item
curl -X DELETE "http://localhost:8000/api/items/1"
```

### Automated Testing (pytest)

```python
# tests/test_main.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_items():
    response = client.get("/api/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_item():
    response = client.post(
        "/api/items?user_id=1",
        json={
            "title": "Test",
            "description": "Test item",
            "price": 9.99,
            "is_available": True
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test"
```

---

## 📝 Common Operations Summary

### Database Connection Flow

```
1. Client Request → 2. FastAPI Endpoint → 3. get_db() Dependency
                                                    ↓
4. CRUD/Custom Function ← 5. SQLAlchemy Session ← SessionLocal
                                                    ↓
6. Database Query/Operation → 7. Database (PostgreSQL/MySQL/SQLite)
```

### Request Flow

```
Frontend (React/Vue/etc)
    ↓ HTTP Request (JSON)
FastAPI Router (/api/items)
    ↓ Dependency Injection
Database Session (get_db)
    ↓
CRUD Operations (crud.py) or Custom Queries (db_custom.py)
    ↓
SQLAlchemy Models (models.py)
    ↓
Database (PostgreSQL/MySQL/SQLite)
    ↓ Response
Pydantic Schema (schemas.py) - Validation & Serialization
    ↓ HTTP Response (JSON)
Frontend receives data
```

---

## 🎯 Key Concepts

### 1. **Models vs Schemas**
- **Models** (`models.py`): SQLAlchemy ORM - defines database table structure
- **Schemas** (`schemas.py`): Pydantic - validates request/response data

### 2. **CRUD Operations**
- **Create** → POST
- **Read** → GET
- **Update** → PUT/PATCH
- **Delete** → DELETE

### 3. **Database Session**
- `get_db()` dependency provides database session
- Automatically closes connection after request
- Use with `Depends(get_db)` in endpoint functions

### 4. **Custom Queries**
- Use `db_custom.py` for complex queries
- Implement joins, aggregations, and business logic
- Keep CRUD operations simple and focused

---

## 🔒 Security Best Practices

```python
# Add authentication
from fastapi.security import HTTPBearer

security = HTTPBearer()

@router.get("/protected")
def protected_route(credentials = Depends(security)):
    # Validate token
    return {"message": "Protected data"}
```

---

## 📚 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org
- **Pydantic Documentation**: https://docs.pydantic.dev

---

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

---

## 📄 License

This project is open source and available under the MIT License.

---

**Happy Coding! 🚀**
