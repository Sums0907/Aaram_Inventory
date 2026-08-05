from typing import List, Dict, Any
from uuid import UUID

class PostingRuleProvider:
    """
    Provides accounting posting rules for different business events.
    In the future, this can fetch rules from a database.
    """
    def __init__(self):
        self.rules = {
            "SALES_FULFILLMENT": [
                {"ledger_code": "RAZORPAY_RECEIVABLE", "type": "DEBIT", "amount_field": "online_receivable"},
                {"ledger_code": "SHOPDECK_RECEIVABLE", "type": "DEBIT", "amount_field": "cod_receivable"},
                {"ledger_code": "SALES_-_SHOPDECK", "type": "CREDIT", "amount_field": "base_price"},
                {"ledger_code": "OUTPUT_CGST", "type": "CREDIT", "amount_field": "cgst"},
                {"ledger_code": "OUTPUT_SGST", "type": "CREDIT", "amount_field": "sgst"},
                {"ledger_code": "OUTPUT_IGST", "type": "CREDIT", "amount_field": "igst"}
            ],
            "SALES_RETURN": [
                {"ledger_code": "SALES_RETURN_-_SHOPDECK", "type": "DEBIT", "amount_field": "base_price"},
                {"ledger_code": "OUTPUT_CGST", "type": "DEBIT", "amount_field": "cgst"},
                {"ledger_code": "OUTPUT_SGST", "type": "DEBIT", "amount_field": "sgst"},
                {"ledger_code": "OUTPUT_IGST", "type": "DEBIT", "amount_field": "igst"},
                {"ledger_code": "RAZORPAY_RECEIVABLE", "type": "CREDIT", "amount_field": "online_receivable"},
                {"ledger_code": "SHOPDECK_RECEIVABLE", "type": "CREDIT", "amount_field": "cod_receivable"}
            ],
            "SETTLEMENT_RECEIVED": [
                {"ledger_code": "AXIS_BANK_CURRENT_ACCOUNT", "type": "DEBIT", "amount_field": "bank_amount"},
                {"ledger_code": "PAYMENT_GATEWAY_CHARGES", "type": "DEBIT", "amount_field": "gateway_fee"},
                {"ledger_code": "INPUT_CGST", "type": "DEBIT", "amount_field": "input_cgst"},
                {"ledger_code": "INPUT_SGST", "type": "DEBIT", "amount_field": "input_sgst"},
                {"ledger_code": "RAZORPAY_RECEIVABLE", "type": "CREDIT", "amount_field": "online_settled"},
                {"ledger_code": "SHOPDECK_RECEIVABLE", "type": "CREDIT", "amount_field": "cod_settled"}
            ]
        }
        
    def get_rules_for_event(self, event_type: str) -> List[Dict[str, Any]]:
        return self.rules.get(event_type, [])
