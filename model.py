class ProductCategory(str, enum.Enum):
    finished = "finished"
    semi_finished = "semi-finished"
    raw = "raw"

class UnitOfMeasure(str, enum.Enum):
    mtr = "mtr"
    mm = "mm"
    ltr = "ltr"
    ml = "ml"
    cm = "cm"
    mg = "mg"
    gm = "gm"
    unit = "unit"
    pack = "pack"


class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(Enum(ProductCategory), nullable=False)
    description = Column(String(250), nullable=True)
    product_image = Column(String(500), nullable=True)  # URL stored as string
    sku = Column(String(100), nullable=False, unique=True)
    unit_of_measure = Column(Enum(UnitOfMeasure), nullable=False)
    lead_time = Column(Integer, nullable=False)  # in days
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

Base.metadata.create_all(bind=engine)


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    category: Literal["finished", "semi-finished", "raw"]
    description: Optional[str] = Field(None, max_length=250)
    product_image: Optional[HttpUrl] = None
    sku: str = Field(..., min_length=2, max_length=100)
    unit_of_measure: Literal["mtr", "mm", "ltr", "ml", "cm", "mg", "gm", "unit", "pack"]
    lead_time: int = Field(..., ge=0, le=999)

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    category: Optional[Literal["finished", "semi-finished", "raw"]]
    description: Optional[str] = Field(None, max_length=250)
    product_image: Optional[HttpUrl]
    sku: Optional[str] = Field(None, min_length=2, max_length=100)
    unit_of_measure: Optional[Literal["mtr", "mm", "ltr", "ml", "cm", "mg", "gm", "unit", "pack"]]
    lead_time: Optional[int] = Field(None, ge=0, le=999)

class ProductResponse(BaseModel):
    id: int
    name: str
    category: str
    description: Optional[str]
    product_image: Optional[str]
    sku: str
    unit_of_measure: str
    lead_time: int
    created_date: datetime
    updated_date: datetime

    class Config:
        orm_mode = True


app = FastAPI(title="Product API", version="1.1.0")


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
