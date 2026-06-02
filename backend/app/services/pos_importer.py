import pandas as pd
import datetime
import logging
import os
from sqlalchemy.orm import Session
from app.models.transaction import Transaction

logger = logging.getLogger(__name__)

def import_pos_csv(file_path: str, db: Session) -> dict:
    """
    Import transactions from POS CSV file.
    """
    if not os.path.exists(file_path):
        logger.error(f"POS CSV file {file_path} not found.")
        return {"status": "error", "message": "File not found"}

    try:
        # Load CSV using pandas
        df = pd.read_csv(file_path)
        
        # Normalize column names in case of whitespace/casing
        df.columns = [col.strip() for col in df.columns]
        
        # Clear existing transactions to prevent duplicates in demo env
        db.query(Transaction).delete()
        db.commit()

        imported_count = 0
        total_amount = 0.0
        unique_orders = set()
        min_date = None
        max_date = None

        for _, row in df.iterrows():
            try:
                order_id = str(row.get("order_id", ""))
                if not order_id or order_id == "nan":
                    continue
                
                unique_orders.add(order_id)
                
                # Parse date (Format: DD-MM-YYYY)
                date_str = str(row.get("order_date", ""))
                try:
                    order_date = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
                except Exception:
                    order_date = datetime.date.today()
                
                if min_date is None or order_date < min_date:
                    min_date = order_date
                if max_date is None or order_date > max_date:
                    max_date = order_date

                # Parse time (Format: HH:MM:SS)
                time_str = str(row.get("order_time", "12:00:00"))
                try:
                    order_time = datetime.datetime.strptime(time_str, "%H:%M:%S").time()
                except Exception:
                    try:
                        order_time = datetime.datetime.strptime(time_str, "%H:%M").time()
                    except Exception:
                        order_time = datetime.time(12, 0, 0)

                qty = int(row.get("qty", 1))
                gmv = float(row.get("GMV", 0.0))
                nmv = float(row.get("NMV", 0.0))
                item_total = float(row.get("total_amount", nmv))
                total_amount += item_total

                txn = Transaction(
                    order_id=order_id,
                    invoice_number=str(row.get("invoice_number", "")),
                    order_date=order_date,
                    order_time=order_time,
                    store_id=str(row.get("store_id", "ST1008")),
                    store_name=str(row.get("store_name", "Brigade_Bangalore")),
                    city=str(row.get("city", "Bangalore")),
                    customer_name=str(row.get("customer_name", "Guest")),
                    customer_number=str(row.get("customer_number", "")),
                    sku=str(row.get("sku", "")),
                    product_name=str(row.get("product_name", "")),
                    brand_name=str(row.get("brand_name", "")),
                    department=str(row.get("dep_name", "makeup")),
                    sub_category=str(row.get("sub_category", "")),
                    quantity=qty,
                    gmv=gmv,
                    nmv=nmv,
                    total_amount=item_total,
                    salesperson_name=str(row.get("salesperson_name", "")),
                    employee_code=str(row.get("employee_code", ""))
                )
                db.add(txn)
                imported_count += 1
            except Exception as row_error:
                logger.error(f"Error parsing row: {row_error}")
                continue

        db.commit()
        logger.info(f"Successfully imported {imported_count} POS records")
        
        return {
            "status": "success",
            "records_imported": imported_count,
            "unique_orders": len(unique_orders),
            "total_revenue": round(total_amount, 2),
            "date_range": {
                "start": min_date.isoformat() if min_date else None,
                "end": max_date.isoformat() if max_date else None
            }
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to import POS CSV: {e}")
        return {"status": "error", "message": str(e)}
