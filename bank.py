# This file is part of company_bank module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction

__all__ = ['BankAccount', 'BankAccountParty']


class BankAccount(metaclass=PoolMeta):
    __name__ = 'bank.account'

    @classmethod
    def write(cls, *args):
        pool = Pool()
        Party = pool.get('party.party')
        actions = iter(args)
        parties = set([])
        for accounts, values in zip(actions, actions):
            if 'active' in values and not values['active']:
                for account in accounts:
                    parties |= set(account.owners)
        super(BankAccount, cls).write(*args)
        if parties:
            Party.set_default_bank_accounts(list(parties))


class BankAccountParty(metaclass=PoolMeta):
    __name__ = 'bank.account-party.party'
    company = fields.Many2One('company.company', 'Company', ondelete='CASCADE',
        required=True)
    payable_bank_account = fields.Boolean('Default Payable Bank Account')
    receivable_bank_account = fields.Boolean('Default Receivable Bank Account')

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @classmethod
    def create(cls, vlist):
        pool = Pool()
        Party = pool.get('party.party')
        records = super(BankAccountParty, cls).create(vlist)
        parties = set([r.owner for r in records])
        Party.set_default_bank_accounts(list(parties))
        return records

    @classmethod
    def delete(cls, bank_account_parties):
        pool = Pool()
        Party = pool.get('party.party')
        company = Transaction().context.get('company')
        parties = set()
        for bank_account_party in bank_account_parties:
            if (bank_account_party.company
                    and (bank_account_party.company.id != company)):
                bank_account_parties.remove(bank_account_party)
            parties.add(bank_account_party.owner)
        super(BankAccountParty, cls).delete(bank_account_parties)
        Party.set_default_bank_accounts(list(parties))
