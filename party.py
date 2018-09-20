# This file is part of company_bank module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields, ModelSQL, Unique
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction

__all__ = ['PartyCompanyBankAccount', 'Party']


class PartyCompanyBankAccount(ModelSQL):
    'Company Bank Account per Party'
    __name__ = 'party.party-company.company'

    company = fields.Many2One('company.company', 'Company', required=True,
        ondelete='CASCADE')
    company_party = fields.Function(fields.Many2One('party.party',
            'Company Party'), 'get_company_party')
    party = fields.Many2One('party.party', 'Party', required=True,
        ondelete='CASCADE')
    receivable_bank_account = fields.Many2One('bank.account',
        'Receivable bank account',
        domain=[
            ('owners', '=', Eval('company_party')),
        ],
        depends=['company_party'])
    payable_bank_account = fields.Many2One('bank.account',
        'Payable bank account',
        domain=[
            ('owners', '=', Eval('company_party')),
        ],
        depends=['company_party'])

    @classmethod
    def __setup__(cls):
        super(PartyCompanyBankAccount, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints += [
            ('company_party_uniq', Unique(t, t.company, t.party),
                'Party must be unique per company.')
            ]

    def get_company_party(self, name=None):
        return self.company.party.id

    @classmethod
    def delete_when_empty(cls, accounts):
        accounts_to_delete = []
        for account in accounts:
            if (not account.payable_bank_account
                    and not account.receivable_bank_account):
                accounts_to_delete.append(account)
        if accounts_to_delete:
            cls.delete(accounts_to_delete)


class Party(metaclass=PoolMeta):
    __name__ = 'party.party'
    company_party = fields.Function(fields.Many2One('party.party',
            'Company Party'), 'get_company_party')
    payable_bank_account = fields.Function(fields.Many2One('bank.account',
            'Default payable bank account',
            domain=[
                ('active', '=', True),
                ('owners', '=', Eval('id')),
                ],
            depends=['id']),
        'get_bank_account', setter='set_bank_accounts')
    receivable_bank_account = fields.Function(fields.Many2One('bank.account',
            'Default receivable bank account',
            domain=[
                ('active', '=', True),
                ('owners', '=', Eval('id')),
                ],
            depends=['id']),
        'get_bank_account', setter='set_bank_accounts')
    payable_company_bank_account = fields.Function(
        fields.Many2One('bank.account',
            'Default company payable bank account', domain=[
                ('owners', '=', Eval('company_party')),
                ], depends=['company_party']),
        'get_company_bank_account', setter='set_company_bank_accounts')
    receivable_company_bank_account = fields.Function(
        fields.Many2One('bank.account',
            'Default company receivable bank account', domain=[
                ('owners', '=', Eval('company_party')),
                ], depends=['company_party']),
        'get_company_bank_account', setter='set_company_bank_accounts')

    @classmethod
    def default_company_party(cls):
        Company = Pool().get('company.company')
        company_id = Transaction().context.get('company')
        if company_id:
            company = Company(company_id)
            return company.party.id

    def get_company_party(self, name):
        return self.default_company_party()

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

    @classmethod
    def get_company_bank_account(cls, parties, names):
        CompanyBankAccount = Pool().get('party.party-company.company')
        company = Transaction().context.get('company')
        party_ids = [p.id for p in parties]
        res = {}
        res['receivable_company_bank_account'] = {}.fromkeys(party_ids)
        res['payable_company_bank_account'] = {}.fromkeys(party_ids)
        if company:
            accounts = CompanyBankAccount.search([
                ('company', '=', company),
                ('party', 'in', party_ids),
                ])
            for account in accounts:
                party_id = account.party.id
                for name in ['receivable', 'payable']:
                    value = getattr(account, '%s_bank_account' % name)
                    if value:
                        res['%s_company_bank_account' % name][party_id] = (
                            value.id)
        for key in list(res.keys()):
            if key not in names:
                del res[key]
        return res

    @classmethod
    def set_company_bank_accounts(cls, parties, name, value):
        CompanyBankAccount = Pool().get('party.party-company.company')
        company = Transaction().context.get('company')
        to_create = []
        name = name.replace('_company', '')
        if company:
            for party in parties:
                accounts = CompanyBankAccount.search([
                        ('company', '=', company),
                        ('party', '=', party),
                        ])
                if accounts:
                    CompanyBankAccount.write(accounts, {name: value})
                    CompanyBankAccount.delete_when_empty(accounts)
                else:
                    to_create.append({
                            'company': company,
                            'party': party.id,
                            name: value,
                            })
        if to_create:
            CompanyBankAccount.create(to_create)

    @classmethod
    def set_default_bank_accounts(cls, parties):
        for party in parties:
            if (party.receivable_bank_account
                    and not party.receivable_bank_account.active):
                party.receivable_bank_account = None
            if (party.payable_bank_account
                    and not party.payable_bank_account.active):
                party.payable_bank_account = None
            active_accounts = [ba for ba in party.bank_accounts if ba.active]
            if not active_accounts:
                party.receivable_bank_account = None
                party.payable_bank_account = None
            elif len(active_accounts) == 1:
                account, = active_accounts
                party.receivable_bank_account = account
                party.payable_bank_account = account
        cls.save(parties)
