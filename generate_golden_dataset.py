import pandas as pd
from decimal import Decimal
from pathlib import Path
from datetime import datetime
import calendar
import os

# ==========================================================
# PATHS
# ==========================================================
BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "input"
GOLDEN_DIR = BASE_DIR / "tests" / "golden_dataset" / "expected"

GOLDEN_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================================
# FILES
# ==========================================================
TAX_FILE = INPUT_DIR / "Tax Ready Report.csv"
ORDER_FILE = INPUT_DIR / "Order Reconciliation Report.csv"
RAZORPAY_FILE = INPUT_DIR / "razorpay Settlement Reconciliation Report.csv"
COD_FILE = INPUT_DIR / "COD Settlement Report.csv"

# ==========================================================
# LEDGER NAMES
# ==========================================================
LEDGER = {
    "SALES": "Sales - ShopDeck",
    "SALES_RETURN": "Sales Return - ShopDeck",
    "ONLINE_RECEIVABLE": "Razorpay Receivable",
    "COD_RECEIVABLE": "ShopDeck Receivable",
    "CGST": "Output CGST",
    "SGST": "Output SGST",
    "IGST": "Output IGST",
    "ROUND_OFF": "Round Off",
    "BANK": "Axis Bank Current Account",
    "PG_CHARGES": "Payment Gateway Charges",
    "INPUT_CGST": "Input CGST",
    "INPUT_SGST": "Input SGST"
}

VOUCHER = {
    "DATE": "",
    "TYPE": "Journal"
}

OPENING = {
    "ONLINE": Decimal("0"),
    "COD": Decimal("0")
}

def money(value):
    if pd.isna(value):
        return Decimal("0")
    value = str(value).strip()
    if value in ("", "-", "--", "nan", "None"):
        return Decimal("0")
    value = value.replace(",", "")
    value = value.replace("₹", "")
    try:
        return Decimal(value)
    except Exception:
        return Decimal("0")

def get_voucher_date(razorpay):
    date_text = str(razorpay["settled_at"].dropna().iloc[0]).strip()
    date_text = date_text.split(" ")[0]
    dt = datetime.strptime(date_text, "%d/%m/%Y")
    last_day = calendar.monthrange(dt.year, dt.month)[1]
    return f"{last_day:02d}-{dt.month:02d}-{dt.year}"

def load_reports():
    print("\nReading reports...\n")
    tax = pd.read_csv(TAX_FILE)
    orders = pd.read_csv(ORDER_FILE, header=2)
    razorpay = pd.read_csv(RAZORPAY_FILE)
    cod = pd.read_csv(COD_FILE)
    return tax, orders, razorpay, cod

def validate_reports(tax, orders):
    tax_required = ["Order ID", "Invoice/CN No.", "Document Type", "Base Price", "Tax", "CGST", "SGST", "IGST", "Selling Price"]
    order_required = ["Order ID", "Payment Method", "Order Status", "Customer Invoice ID"]
    for col in tax_required:
        if col not in tax.columns:
            raise Exception(f"Tax Ready Report missing column: {col}")
    for col in order_required:
        if col not in orders.columns:
            raise Exception(f"Order Report missing column: {col}")
    print("Validation Successful")

def build_master(tax, orders):
    print("\nBuilding Master Dataset...\n")
    order_info = orders[["Order ID", "Payment Method", "Order Status", "Customer Invoice ID", "Invoice Total (Incl. Tax)"]].drop_duplicates(subset="Order ID")
    master = tax.merge(order_info, on="Order ID", how="left", validate="many_to_one")
    money_columns = ["Base Price", "Tax", "CGST", "SGST", "IGST", "Selling Price"]
    for col in money_columns:
        master[col] = master[col].apply(money)
    print(f"Master rows: {len(master)}")
    return master

def split_transactions(master):
    invoices = master[master["Document Type"].astype(str).str.upper().str.contains("INVOICE", na=False)].copy()
    credit_notes = master[master["Document Type"].astype(str).str.upper().str.contains("CREDIT", na=False)].copy()
    return invoices, credit_notes

def payment_split(df):
    online = df[df["Payment Method"].astype(str).str.upper() == "ONLINE"].copy()
    cod = df[df["Payment Method"].astype(str).str.upper().isin(["COD", "PARTIAL-COD"])].copy()
    return online, cod

def totals(df):
    return {
        "base": df["Base Price"].sum(),
        "cgst": df["CGST"].sum(),
        "sgst": df["SGST"].sum(),
        "igst": df["IGST"].sum(),
        "gross": df["Selling Price"].sum()
    }

def float_money(val):
    return float(val) if isinstance(val, Decimal) else val

def sales_journal(master):
    invoices, _ = split_transactions(master)
    online, cod = payment_split(invoices)
    online_total = totals(online)
    cod_total = totals(cod)
    journal = []
    
    if online_total["gross"] != 0:
        journal.append({"Ledger": LEDGER["ONLINE_RECEIVABLE"], "Debit": float_money(online_total["gross"]), "Credit": 0.0})
    if cod_total["gross"] != 0:
        journal.append({"Ledger": LEDGER["COD_RECEIVABLE"], "Debit": float_money(cod_total["gross"]), "Credit": 0.0})
    
    taxable = online_total["base"] + cod_total["base"]
    cgst = online_total["cgst"] + cod_total["cgst"]
    sgst = online_total["sgst"] + cod_total["sgst"]
    igst = online_total["igst"] + cod_total["igst"]
    
    journal.append({"Ledger": LEDGER["SALES"], "Debit": 0.0, "Credit": float_money(taxable)})
    if cgst != 0: journal.append({"Ledger": LEDGER["CGST"], "Debit": 0.0, "Credit": float_money(cgst)})
    if sgst != 0: journal.append({"Ledger": LEDGER["SGST"], "Debit": 0.0, "Credit": float_money(sgst)})
    if igst != 0: journal.append({"Ledger": LEDGER["IGST"], "Debit": 0.0, "Credit": float_money(igst)})
    
    total_debit = sum(row["Debit"] for row in journal)
    total_credit = sum(row["Credit"] for row in journal)
    difference = Decimal(str(total_debit)) - Decimal(str(total_credit))
    
    if difference > Decimal("0"):
        journal.append({"Ledger": LEDGER["ROUND_OFF"], "Debit": 0.0, "Credit": float(difference)})
    elif difference < Decimal("0"):
        journal.append({"Ledger": LEDGER["ROUND_OFF"], "Debit": float(abs(difference)), "Credit": 0.0})
        
    return pd.DataFrame(journal)

def credit_note_journal(master):
    _, credit_notes = split_transactions(master)
    online, cod = payment_split(credit_notes)
    online_total = totals(online)
    cod_total = totals(cod)
    journal = []
    
    taxable = abs(online_total["base"] + cod_total["base"])
    cgst = abs(online_total["cgst"] + cod_total["cgst"])
    sgst = abs(online_total["sgst"] + cod_total["sgst"])
    igst = abs(online_total["igst"] + cod_total["igst"])
    online_receivable = abs(online_total["gross"])
    cod_receivable = abs(cod_total["gross"])
    
    journal.append({"Ledger": LEDGER["SALES_RETURN"], "Debit": float_money(taxable), "Credit": 0.0})
    if cgst != 0: journal.append({"Ledger": LEDGER["CGST"], "Debit": float_money(cgst), "Credit": 0.0})
    if sgst != 0: journal.append({"Ledger": LEDGER["SGST"], "Debit": float_money(sgst), "Credit": 0.0})
    if igst != 0: journal.append({"Ledger": LEDGER["IGST"], "Debit": float_money(igst), "Credit": 0.0})
    if online_receivable != 0: journal.append({"Ledger": LEDGER["ONLINE_RECEIVABLE"], "Debit": 0.0, "Credit": float_money(online_receivable)})
    if cod_receivable != 0: journal.append({"Ledger": LEDGER["COD_RECEIVABLE"], "Debit": 0.0, "Credit": float_money(cod_receivable)})
    
    total_debit = sum(row["Debit"] for row in journal)
    total_credit = sum(row["Credit"] for row in journal)
    difference = Decimal(str(total_debit)) - Decimal(str(total_credit))
    
    if difference > Decimal("0"):
        journal.append({"Ledger": LEDGER["ROUND_OFF"], "Debit": 0.0, "Credit": float(difference)})
    elif difference < Decimal("0"):
        journal.append({"Ledger": LEDGER["ROUND_OFF"], "Debit": float(abs(difference)), "Credit": 0.0})
        
    return pd.DataFrame(journal)

def export_sales_journals(master):
    sales = sales_journal(master)
    credit = credit_note_journal(master)
    sales.to_json(GOLDEN_DIR / "golden_sales_journal.json", orient="records", indent=2)
    credit.to_json(GOLDEN_DIR / "golden_credit_note_journal.json", orient="records", indent=2)

def settlement_journal(razorpay, cod):
    payments = razorpay[razorpay["transaction_entity"].astype(str).str.strip().str.lower() == "payment"].copy()
    rp_amount = payments["amount"].apply(money).sum()
    rp_bank = payments["credit"].apply(money).sum()
    rp_fee = payments["fee (exclusive tax)"].apply(money).sum()
    rp_tax = payments["tax"].apply(money).sum()
    input_cgst = rp_tax / Decimal("2")
    input_sgst = rp_tax / Decimal("2")
    
    cod_amount = cod["Total COD Sales Amount"].apply(money).sum()
    rows = []
    
    bank_total = rp_bank + cod_amount
    rows.append({"Date": VOUCHER["DATE"], "Voucher Type": VOUCHER["TYPE"], "Ledger": LEDGER["BANK"], "Debit": float_money(bank_total), "Credit": 0.0, "Narration": "Monthly Settlement"})
    
    if rp_fee != 0: rows.append({"Date": VOUCHER["DATE"], "Voucher Type": VOUCHER["TYPE"], "Ledger": LEDGER["PG_CHARGES"], "Debit": float_money(rp_fee), "Credit": 0.0, "Narration": "Gateway Charges"})
    if input_cgst != 0: rows.append({"Date": VOUCHER["DATE"], "Voucher Type": VOUCHER["TYPE"], "Ledger": LEDGER["INPUT_CGST"], "Debit": float_money(input_cgst), "Credit": 0.0, "Narration": "GST on Gateway Charges"})
    if input_sgst != 0: rows.append({"Date": VOUCHER["DATE"], "Voucher Type": VOUCHER["TYPE"], "Ledger": LEDGER["INPUT_SGST"], "Debit": float_money(input_sgst), "Credit": 0.0, "Narration": "GST on Gateway Charges"})
    if rp_amount != 0: rows.append({"Date": VOUCHER["DATE"], "Voucher Type": VOUCHER["TYPE"], "Ledger": LEDGER["ONLINE_RECEIVABLE"], "Debit": 0.0, "Credit": float_money(rp_amount), "Narration": "Razorpay Settlement"})
    if cod_amount != 0: rows.append({"Date": VOUCHER["DATE"], "Voucher Type": VOUCHER["TYPE"], "Ledger": LEDGER["COD_RECEIVABLE"], "Debit": 0.0, "Credit": float_money(cod_amount), "Narration": "COD Settlement"})
    
    total_debit = sum(r["Debit"] for r in rows)
    total_credit = sum(r["Credit"] for r in rows)
    difference = Decimal(str(total_debit)) - Decimal(str(total_credit))
    
    if abs(difference) <= Decimal("0.05"):
        if difference > 0: rows.append({"Date": VOUCHER["DATE"], "Voucher Type": VOUCHER["TYPE"], "Ledger": LEDGER["ROUND_OFF"], "Debit": 0.0, "Credit": float(difference), "Narration": "Round Off"})
        elif difference < 0: rows.append({"Date": VOUCHER["DATE"], "Voucher Type": VOUCHER["TYPE"], "Ledger": LEDGER["ROUND_OFF"], "Debit": float(abs(difference)), "Credit": 0.0, "Narration": "Round Off"})
    
    return pd.DataFrame(rows)

def export_settlement_journal(razorpay, cod):
    journal = settlement_journal(razorpay, cod)
    journal.to_json(GOLDEN_DIR / "golden_settlement_journal.json", orient="records", indent=2)

if __name__ == "__main__":
    tax, orders, razorpay, cod = load_reports()
    validate_reports(tax, orders)
    master = build_master(tax, orders)
    VOUCHER["DATE"] = get_voucher_date(razorpay)
    export_sales_journals(master)
    export_settlement_journal(razorpay, cod)
    print("Golden dataset successfully generated in 'golden/' directory.")
