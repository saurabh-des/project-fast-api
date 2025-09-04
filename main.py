from fastapi import FastAPI, HTTPException, Path, Query, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# ---------------------- Database Setup ----------------------
DATABASE_URL = "mysql+mysqlclient://root:password@localhost:3306/mydatabase"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ---------------------- Product Model ----------------------
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    price = Column(Float, nullable=False)

Base.metadata.create_all(bind=engine)

# ---------------------- Pydantic Schemas ----------------------
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    price: float = Field(..., gt=0)

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    price: Optional[float] = Field(None, gt=0)

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float

    class Config:
        orm_mode = True

app = FastAPI(title="Product API", version="1.0.0")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


 1️⃣ List all products with pagination
@app.get("/product/list", response_model=List[ProductResponse])
def list_products(page: int = Query(1, ge=1), db: Session = Depends(get_db)):
    page_size = 10
    offset = (page - 1) * page_size
    products = db.query(Product).offset(offset).limit(page_size).all()
    return products

 2️⃣ View product info by ID
@app.get("/product/{pid}/info", response_model=ProductResponse)
def product_info(pid: int = Path(..., ge=1), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == pid).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

 3️⃣ Add new product
@app.post("/product/add", response_model=ProductResponse, status_code=201)
def add_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

 4️⃣ Update existing product
@app.put("/product/{pid}/update", response_model=ProductResponse)
def update_product(
    pid: int = Path(..., ge=1),
    product_data: ProductUpdate = None,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == pid).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for field, value in product_data.dict(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product
