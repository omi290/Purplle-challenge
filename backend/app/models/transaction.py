from sqlalchemy import Column, Integer, String, Date, Time, Float, DateTime, func
from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(64), index=True, nullable=False)
    invoice_number = Column(String(64), index=True, nullable=True)
    order_date = Column(Date, index=True, nullable=False)
    order_time = Column(Time, nullable=False)
    store_id = Column(String(32), index=True, nullable=True)
    store_name = Column(String(128), nullable=True)
    city = Column(String(64), nullable=True)
    customer_name = Column(String(256), nullable=True)
    customer_number = Column(String(32), nullable=True)
    sku = Column(String(64), nullable=True)
    product_name = Column(String(512), nullable=True)
    brand_name = Column(String(128), nullable=True)
    department = Column(String(64), nullable=True)
    sub_category = Column(String(128), nullable=True)
    quantity = Column(Integer, default=1)
    gmv = Column(Float, default=0.0)
    nmv = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    salesperson_name = Column(String(128), nullable=True)
    employee_code = Column(String(32), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
