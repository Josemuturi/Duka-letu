from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)
    stock = Column(Integer)
    sales = relationship("Sale", back_populates="product")

class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity_sold = Column(Integer)
    sale_date = Column(DateTime, default=datetime.utcnow)
    product = relationship("Product", back_populates="sales")