#This file is part of company_bank module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction

__all__ = ['BankAccountParty']
__metaclass__ = PoolMeta


class BankAccountParty:
    __name__ = 'bank.account-party.party'
    company = fields.Many2One('company.company', 'Company', ondelete='CASCADE',
        required=True)
    payable_bank_account = fields.Boolean('Default Payable Bank Account')
    receivable_bank_account = fields.Boolean('Default Receivable Bank Account')

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @classmethod
    def delete(cls, bank_account_parties):
        company = Transaction().context.get('company')
        for bank_account_party in bank_account_parties:
            if bank_account_party.company.id != company:
                bank_account_parties.remove(bank_account_party)
        return super(BankAccountParty, cls).delete(bank_account_parties)
