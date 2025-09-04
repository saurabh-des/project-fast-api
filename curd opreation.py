# 1️⃣ List all products with pagination
@app.get("/product/list", response_model=List[ProductResponse])
def list_products(page: int = Query(1, ge=1), db: Session = Depends(get_db)):
    page_size = 10
    offset = (page - 1) * page_size
    products = db.query(Product).offset(offset).limit(page_size).all()
    return products

# 2️⃣ View product info by ID
@app.get("/product/{pid}/info", response_model=ProductResponse)
def product_info(pid: int = Path(..., ge=1), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == pid).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# 3️⃣ Add new product
@app.post("/product/add", response_model=ProductResponse, status_code=201)
def add_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

# 4️⃣ Update existing product
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
