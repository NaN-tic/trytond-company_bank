#This file is part of company_bank module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction

__all__ = ['Party']
__metaclass__ = PoolMeta


class Party:
    __name__ = 'party.party'
    payable_bank_account = fields.Function(fields.Many2One('bank.account',
            'Default payable bank account', domain=[
                ('owners', '=', Eval('id')),
                ], depends=['id']),
        'get_bank_account', setter='set_bank_accounts')
    receivable_bank_account = fields.Function(fields.Many2One('bank.account',
            'Default receivable bank account', domain=[
                ('owners', '=', Eval('id')),
                ], depends=['id']),
        'get_bank_account', setter='set_bank_accounts')

    def get_bank_account(self, name):
        BankAccountParty = Pool().get('bank.account-party.party')
        company = Transaction().context.get('company')
        if company:
            accounts = BankAccountParty.search([
                ('company', '=', company),
                ('owner', '=', self.id),
                (name, '=', True),
                ])
            for account in accounts:
                return account.account.id

    @classmethod
    def set_bank_accounts(cls, parties, name, value):
        BankAccountParty = Pool().get('bank.account-party.party')
        BankAccount = Pool().get('bank.account')
        company = Transaction().context.get('company')
        if company:
            for party in parties:
                accounts = BankAccountParty.search([
                    ('company', '=', company),
                    ('owner', '=', party.id),
                    ])
                bank_accounts = [x.account.id for x in accounts]
                if value and (not accounts or value not in bank_accounts):
                    account, = BankAccount.search([
                            ('id', '=', value),
                            ])
                    vlist = [{
                            'account': account,
                            'owner': party,
                            'company': company,
                            name: True,
                            }]
                    BankAccountParty.create(vlist)
                for account in accounts:
                    if account.account.id == value:
                        vals = {name: True}
                    else:
                        vals = {name: False}
                    BankAccountParty.write([account], vals)

    def get_payable_bank_account(self):
        BankAccount = Pool().get('bank.account')
        return BankAccount(self.payable_bank_account)

    def get_receivable_bank_account(self):
        BankAccount = Pool().get('bank.account')
        return BankAccount(self.receivable_bank_account)
