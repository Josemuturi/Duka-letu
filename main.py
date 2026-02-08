from datetime   import datetime
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import SessionLocal, engine

# Step 1: Initialize the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Step 2: Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Step 3: The "Recording a Sale" Logic (The Foundation for Analytics)
@app.post("/sales/")
def create_sale(product_id: int, quantity: int, db: Session = Depends(get_db)):
    # 1. Fetch the product
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 2. Check stock
    if product.stock < quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    # 3. Update stock (Software Engineering)
    product.stock -= quantity

    # 4. Log the sale (Data Science Foundation)
    new_sale = models.Sale(product_id=product_id, quantity_sold=quantity)
    db.add(new_sale)
    db.commit()
    
    return {"message": f"Sold {quantity} of {product.name}. Remaining: {product.stock}"}
import pandas as pd # Make sure to 'pip install pandas'

@app.get("/analytics/forecast/{product_id}")
def get_inventory_forecast(product_id: int, db: Session = Depends(get_db)):
    # 1. Get all sales for this product
    sales = db.query(models.Sale).filter(models.Sale.product_id == product_id).all()
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if not sales:
        return {"message": "Not enough sales data to predict yet."}

    # 2. Convert database data to a Pandas DataFrame (Data Science Step)
    df = pd.DataFrame([{"date": s.sale_date, "qty": s.quantity_sold} for s in sales])
    df['date'] = pd.to_datetime(df['date'])
    
    # 3. Calculate Average Daily Sales
    total_days = (df['date'].max() - df['date'].min()).days or 1
    avg_daily_sales = df['qty'].sum() / total_days
    
    # 4. Predict Days Remaining
    if avg_daily_sales == 0:
        return {"message": "No daily sales recorded."}
        
    days_left = product.stock / avg_daily_sales
    
    return {
        "product": product.name,
        "current_stock": product.stock,
        "avg_daily_velocity": round(avg_daily_sales, 2),
        "estimated_days_remaining": round(days_left, 1)
    }
    
@app.get("/analytics/restock-report/")
def get_restock_report(days_threshold: int = 3, db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    report = []

    for product in products:
        sales = db.query(models.Sale).filter(models.Sale.product_id == product.id).all()
        
        if len(sales) > 1: # We need at least 2 sales to find a "trend"
            df = pd.DataFrame([{"date": s.sale_date, "qty": s.quantity_sold} for s in sales])
            df['date'] = pd.to_datetime(df['date'])
            
            total_days = (df['date'].max() - df['date'].min()).days or 1
            avg_daily_sales = df['qty'].sum() / total_days
            
            if avg_daily_sales > 0:
                days_left = product.stock / avg_daily_sales
                
                # Only add to report if it's running out soon (e.g., within 3 days)
                if days_left <= days_threshold:
                    report.append({
                        "product": product.name,
                        "current_stock": product.stock,
                        "days_remaining": round(days_left, 1),
                        "status": "URGENT" if days_left <= 1 else "WARNING"
                    })

    return {
        "report_generated_at": datetime.utcnow(),
        "urgent_restocks": report,
        "total_items_monitored": len(products)
    }
@app.get("/analytics/raw-sales/{product_id}")
def get_raw_sales(product_id: int, db: Session = Depends(get_db)):
    sales = db.query(models.Sale).filter(models.Sale.product_id == product_id).all()
    return [{"date": s.sale_date.strftime("%Y-%m-%d"), "quantity": s.quantity_sold} for s in sales]
@app.post("/products/restock/{product_id}")
def restock_product(product_id: int, quantity: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.stock += quantity
    db.commit()
    return {"message": f"Successfully added {quantity} units. New stock: {product.stock}"}
    