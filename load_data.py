import pandas as pd

from app.database import SessionLocal
from app.models import Sale

df = pd.read_csv("data/sales.csv")

db = SessionLocal()

for _, row in df.iterrows():
    sale = Sale(
        product=row["product"],
        category=row["category"],
        quantity=row["quantity"],
        revenue=row["revenue"]
    )
    db.add(sale)

db.commit()
db.close()

print("Data loaded successfully!")