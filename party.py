# This file is part of company_bank module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields, ModelSQL, Unique
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction
from trytond.modules.company.model import (
    CompanyMultiValueMixin, CompanyValueMixin)


class CompanyBankAccountsMixin(object):
    __slots__ = ()
    company_bank_accounts = fields.Function(fields.Many2Many(
        'bank.account', None, None, 'Company Bank Accounts'),
        'get_company_bank_accounts', setter='set_company_bank_accounts')

    @classmethod
    def get_company_bank_accounts(cls, records, name):
        Company = Pool().get('company.company')

        company_id = Transaction().context.get('company')
        bank_accounts = ([x.id for x in Company(company_id).party.bank_accounts]
            if company_id else None)

        return dict((x.id, bank_accounts) for x in records)

    @classmethod
    def set_company_bank_accounts(cls, records, name, value):
        pass


class PartyBankAccountCompany(ModelSQL, CompanyBankAccountsMixin, CompanyValueMixin):
    'Party Bank Account Company'
    __name__ = 'party.party-bank.account-company'
    party = fields.Many2One('party.party', 'Party', ondelete='CASCADE',
        required=True, select=True,
        context={
            'company': Eval('company', -1),
        },
        depends=['company'])
    receivable_bank_account = fields.Many2One('bank.account',
        'Receivable bank account',
        domain=[
            ('owners', '=', Eval('party')),
        ], depends=['party'])
    payable_bank_account = fields.Many2One('bank.account',
        'Payable bank account',
        domain=[
            ('owners', '=', Eval('party')),
        ], depends=['party'])
    receivable_company_bank_account = fields.Many2One('bank.account',
        'Company Receivable bank account',
        domain=[
            ('id', 'in', Eval('company_bank_accounts', [])),
        ], depends=['company_bank_accounts'])
    payable_company_bank_account = fields.Many2One('bank.account',
        'Company Payable bank account',
        domain=[
            ('id', 'in', Eval('company_bank_accounts', [])),
        ], depends=['company_bank_accounts'])


class Party(CompanyBankAccountsMixin, CompanyMultiValueMixin, metaclass=PoolMeta):
    __name__ = 'party.party'
    party_bank_accounts = fields.One2Many(
        'party.party-bank.account-company', 'party', "Party Bank Accounts")
    payable_bank_account = fields.MultiValue(fields.Many2One('bank.account',
            'Default Payable Bank Account',
            domain=[
                ('active', '=', True),
                ('owners', '=', Eval('id')),
                ],
            states={
                'invisible': (~Eval('context', {}).get('company')),
                },
            depends=['id']))
    receivable_bank_account = fields.MultiValue(fields.Many2One('bank.account',
            'Default Receivable Bank Account',
            domain=[
                ('active', '=', True),
                ('owners', '=', Eval('id')),
                ],
            states={
                'invisible': (~Eval('context', {}).get('company')),
                },
            depends=['id']))
    payable_company_bank_account = fields.MultiValue(fields.Many2One('bank.account',
            'Default Company Payable Bank Account',
            domain=[
                ('active', '=', True),
                ('id', 'in', Eval('company_bank_accounts', [])),
                ],
            states={
                'invisible': (~Eval('context', {}).get('company')),
                },
            depends=['company_bank_accounts']))
    receivable_company_bank_account = fields.MultiValue(fields.Many2One('bank.account',
            'Default Company Receivable Bank Account',
            domain=[
                ('active', '=', True),
                ('id', 'in', Eval('company_bank_accounts', [])),
                ],
            states={
                'invisible': (~Eval('context', {}).get('company')),
                },
            depends=['company_bank_accounts']))

    @classmethod
    def multivalue_model(cls, field):
        pool = Pool()
        if field in {'payable_bank_account', 'receivable_bank_account',
                'payable_company_bank_account', 'receivable_company_bank_account'}:
            return pool.get('party.party-bank.account-company')
        return super(Party, cls).multivalue_model(field)

    @classmethod
    def default_company_bank_accounts(cls):
        Company = Pool().get('company.company')

        company_id = Transaction().context.get('company')
        return ([x.id for x in Company(company_id).party.bank_accounts]
            if company_id else [])

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
