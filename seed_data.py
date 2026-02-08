from database import SessionLocal
import models
from datetime import datetime, timedelta
import random

db = SessionLocal()

# 1. Create a Product
new_product = models.Product(name="Blue Band 500g", price=250.0, stock=50)
db.add(new_product)
db.commit()
db.refresh(new_product)

# 2. Simulate 5 days of sales (The Data Science training set)
for i in range(5):
    # Create a date for the past 5 days
    sale_date = datetime.utcnow() - timedelta(days=i)
    # Random sales between 2 and 8 units per day
    qty = random.randint(2, 8)
    
    sale = models.Sale(
        product_id=new_product.id,
        quantity_sold=qty,
        sale_date=sale_date
    )
    db.add(sale)

db.commit()
print(f"Successfully seeded {new_product.name} with 5 days of history!")
db.close()