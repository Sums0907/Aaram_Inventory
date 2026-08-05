from uuid import UUID
from datetime import date
from typing import Dict, Any, List
from src.domains.accounting.schemas.journal import JournalEntryCreate, JournalLineCreate
from src.domains.accounting.repositories.journal import JournalRepository
from src.domains.accounting.repositories.ledger import LedgerRepository
from src.domains.accounting.services.posting_rule_provider import PostingRuleProvider
from src.foundation.exceptions.base import ValidationException

class AccountingEngineService:
    def __init__(
        self, 
        journal_repository: JournalRepository,
        ledger_repository: LedgerRepository,
        posting_rule_provider: PostingRuleProvider
    ):
        self.journal_repository = journal_repository
        self.ledger_repository = ledger_repository
        self.posting_rule_provider = posting_rule_provider

    async def generate_journal(
        self, 
        event_type: str, 
        reference_type: str, 
        reference_number: str, 
        reference_id: UUID, 
        posting_date: date,
        amounts: Dict[str, float],
        user_id: UUID
    ):
        # 1. Get Rules
        rules = self.posting_rule_provider.get_rules_for_event(event_type)
        if not rules:
            # If no rules exist, we skip posting for now.
            return None

        # 2. Build Lines
        lines: List[JournalLineCreate] = []
        for rule in rules:
            ledger_code = rule["ledger_code"]
            ledger = await self.ledger_repository.get_by_code(ledger_code)
            
            if not ledger:
                raise ValidationException(f"Missing required ledger: {ledger_code}")
                
            amount_field = rule["amount_field"]
            amount = amounts.get(amount_field, 0.0)
            
            if amount == 0.0:
                continue

            if rule["type"] == "DEBIT":
                lines.append(JournalLineCreate(
                    ledger_id=ledger.id,
                    debit_amount=amount,
                    credit_amount=0.0
                ))
            else:
                lines.append(JournalLineCreate(
                    ledger_id=ledger.id,
                    debit_amount=0.0,
                    credit_amount=amount
                ))

        # Calculate Round Off
        total_debit = round(sum(line.debit_amount for line in lines), 2)
        total_credit = round(sum(line.credit_amount for line in lines), 2)
        difference = total_debit - total_credit
        
        if difference != 0.0:
            round_off_ledger = await self.ledger_repository.get_by_code("ROUND_OFF")
            if not round_off_ledger:
                raise ValidationException("Missing ROUND_OFF ledger for balancing.")
                
            if difference > 0:
                lines.append(JournalLineCreate(
                    ledger_id=round_off_ledger.id,
                    debit_amount=0.0,
                    credit_amount=difference
                ))
            else:
                lines.append(JournalLineCreate(
                    ledger_id=round_off_ledger.id,
                    debit_amount=abs(difference),
                    credit_amount=0.0
                ))

        if not lines:
            return None

        # 3. Create Journal
        journal_create = JournalEntryCreate(
            journal_number=f"JNL-{reference_number}",
            journal_date=date.today(),
            posting_date=posting_date,
            source="SYSTEM",
            reference_type=reference_type,
            reference_number=reference_number,
            reference_id=reference_id,
            status="POSTED",
            lines=lines
        )
        
        return await self.journal_repository.create_journal(journal_create, user_id)
