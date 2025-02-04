# This file is part of company_bank module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields, ModelSQL
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction
from trytond import backend
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

        bank_accounts = None
        company_id = Transaction().context.get('company')
        if company_id:
            company = Company(company_id)
            company_bank_accounts = (hasattr(company, 'party')
                and company.party.bank_accounts or [])
            if company_bank_accounts:
                bank_accounts = [x.id for x in company_bank_accounts]

        return dict((x.id, bank_accounts) for x in records)

    @classmethod
    def set_company_bank_accounts(cls, records, name, value):
        pass


class PartyBankAccountCompany(ModelSQL, CompanyBankAccountsMixin, CompanyValueMixin):
    'Party Bank Account Company'
    __name__ = 'party.party-bank.account-company'
    party = fields.Many2One('party.party', 'Party', ondelete='CASCADE',
        required=True,
        context={
            'company': Eval('company', -1),
        },
        depends=['company'])
    receivable_bank_account = fields.Many2One('bank.account',
        'Receivable bank account',
        domain=[
            ('owners', '=', Eval('party')),
        ])
    payable_bank_account = fields.Many2One('bank.account',
        'Payable bank account',
        domain=[
            ('owners', '=', Eval('party')),
        ])
    receivable_company_bank_account = fields.Many2One('bank.account',
        'Company Receivable bank account',
        domain=[
            ('id', 'in', Eval('company_bank_accounts', [])),
        ])
    payable_company_bank_account = fields.Many2One('bank.account',
        'Company Payable bank account',
        domain=[
            ('id', 'in', Eval('company_bank_accounts', [])),
        ])

    @classmethod
    def __register__(cls, module_name):
        super().__register__(module_name)
        table = backend.TableHandler(cls, module_name)

        # Drop number_uniq constraint
        table.drop_constraint('party_party-company_company_company_party_uniq')


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
                }))
    receivable_bank_account = fields.MultiValue(fields.Many2One('bank.account',
            'Default Receivable Bank Account',
            domain=[
                ('active', '=', True),
                ('owners', '=', Eval('id')),
                ],
            states={
                'invisible': (~Eval('context', {}).get('company')),
                }))
    payable_company_bank_account = fields.MultiValue(fields.Many2One('bank.account',
            'Default Company Payable Bank Account',
            domain=[
                ('active', '=', True),
                ('id', 'in', Eval('company_bank_accounts', [])),
                ],
            states={
                'invisible': (~Eval('context', {}).get('company')),
                }))
    receivable_company_bank_account = fields.MultiValue(fields.Many2One('bank.account',
            'Default Company Receivable Bank Account',
            domain=[
                ('active', '=', True),
                ('id', 'in', Eval('company_bank_accounts', [])),
                ],
            states={
                'invisible': (~Eval('context', {}).get('company')),
                }))

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
        if company_id:
            company = Company(company_id)
            bank_accounts = (hasattr(company, 'party')
                and company.party.bank_accounts or [])
            return [x.id for x in bank_accounts]

    @classmethod
    def copy(cls, parties, default=None):
        if default is None:
            default = {}
        else:
            default = default.copy()
        # not copy bank accounts
        default.setdefault('party_bank_accounts', None)
        default.setdefault('receivable_bank_account', None)
        default.setdefault('receivable_company_bank_account', None)
        default.setdefault('payable_company_bank_account', None)
        default.setdefault('payable_bank_account', None)
        return super().copy(parties, default=default)

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
