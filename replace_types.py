import os
import glob
import re

# Update schemas
for filepath in glob.glob("src/domains/inventory/schemas/*.py"):
    with open(filepath, "r") as f:
        content = f.read()
    
    # Replace int fields
    content = re.sub(r'quantity: int', 'quantity: float', content)
    content = re.sub(r'scrap_quantity: int', 'scrap_quantity: float', content)
    content = re.sub(r'issued_quantity: int', 'issued_quantity: float', content)
    content = re.sub(r'consumed_quantity: int', 'consumed_quantity: float', content)
    content = re.sub(r'returned_quantity: int', 'returned_quantity: float', content)
    content = re.sub(r'pending_quantity: int', 'pending_quantity: float', content)
    content = re.sub(r'quantity_produced: int', 'quantity_produced: float', content)
    content = re.sub(r'system_quantity: int', 'system_quantity: float', content)
    content = re.sub(r'expected_quantity: int', 'expected_quantity: float', content)
    content = re.sub(r'actual_quantity: int', 'actual_quantity: float', content)
    content = re.sub(r'difference: int', 'difference: float', content)
    content = re.sub(r'quantity_on_hand: int', 'quantity_on_hand: float', content)
    
    with open(filepath, "w") as f:
        f.write(content)

# Update models
for filepath in glob.glob("src/domains/inventory/models/*.py"):
    with open(filepath, "r") as f:
        content = f.read()
    
    # Make sure Numeric is imported
    if "from sqlalchemy import" in content and "Numeric" not in content:
        content = re.sub(r'from sqlalchemy import (.*)', r'from sqlalchemy import Numeric, \1', content)
    elif "from sqlalchemy import" not in content:
        content = "from sqlalchemy import Numeric\n" + content
        
    content = re.sub(r'quantity: Mapped\[int\] = mapped_column\(Integer,', 'quantity: Mapped[float] = mapped_column(Numeric(15, 3),', content)
    content = re.sub(r'quantity: Mapped\[int\] = mapped_column\(nullable=False\)', 'quantity: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False)', content)
    
    content = re.sub(r'scrap_quantity: Mapped\[int\] = mapped_column\(Integer,', 'scrap_quantity: Mapped[float] = mapped_column(Numeric(15, 3),', content)
    content = re.sub(r'issued_quantity: Mapped\[int\] = mapped_column\(Integer,', 'issued_quantity: Mapped[float] = mapped_column(Numeric(15, 3),', content)
    content = re.sub(r'consumed_quantity: Mapped\[int\] = mapped_column\(Integer,', 'consumed_quantity: Mapped[float] = mapped_column(Numeric(15, 3),', content)
    content = re.sub(r'returned_quantity: Mapped\[int\] = mapped_column\(Integer,', 'returned_quantity: Mapped[float] = mapped_column(Numeric(15, 3),', content)
    content = re.sub(r'pending_quantity: Mapped\[int\] = mapped_column\(Integer,', 'pending_quantity: Mapped[float] = mapped_column(Numeric(15, 3),', content)
    content = re.sub(r'quantity_produced: Mapped\[int\] = mapped_column\(Integer,', 'quantity_produced: Mapped[float] = mapped_column(Numeric(15, 3),', content)
    
    content = re.sub(r'quantity_on_hand: Mapped\[int\] = mapped_column\(Integer,', 'quantity_on_hand: Mapped[float] = mapped_column(Numeric(15, 3),', content)
    
    with open(filepath, "w") as f:
        f.write(content)

print("Updated types!")
