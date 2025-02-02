from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from uuid import uuid4
from datetime import datetime
import math

app = FastAPI()

receipts_db: Dict[str, int] = {}

class Item(BaseModel):
    shortDescription: str
    price: str

class Receipt(BaseModel):
    retailer: str
    purchaseDate: str
    purchaseTime: str
    items: List[Item]
    total: str

def calculate_points(receipt: Receipt) -> int:
    points = 0
    
    points += sum(c.isalnum() for c in receipt.retailer)
    
    total = float(receipt.total)
    if total.is_integer():
        points += 50
    if total % 0.25 == 0:
        points += 25
    
    points += (len(receipt.items) // 2) * 5
    
    for item in receipt.items:
        desc_length = len(item.shortDescription.strip())
        if desc_length % 3 == 0:
            points += math.ceil(float(item.price) * 0.2)
    
    purchase_date = datetime.strptime(receipt.purchaseDate, "%Y-%m-%d")
    if purchase_date.day % 2 == 1:
        points += 6
    
    purchase_time = datetime.strptime(receipt.purchaseTime, "%H:%M")
    if 14 <= purchase_time.hour < 16:
        points += 10
    
    return points

@app.post("/receipts/process")
def process_receipt(receipt: Receipt):
    receipt_id = str(uuid4())
    points = calculate_points(receipt)
    receipts_db[receipt_id] = points
    return {"id": receipt_id}

@app.get("/receipts/{id}/points")
def get_points(id: str):
    if id not in receipts_db:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return {"points": receipts_db[id]}
