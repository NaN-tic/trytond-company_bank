# This file is part of company_bank module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields, ModelSQL, ModelView, MatchMixin,\
    sequence_ordered
from trytond.pool import PoolMeta
from trytond.pyson import Eval, Len
from trytond.transaction import Transaction

__all__ = ['PartyDefaultBankAccount', 'Party']


class PartyDefaultBankAccount(sequence_ordered(), ModelSQL, ModelView,
        MatchMixin):
    'Party Default Bank Account'
    __name__ = 'party.party.default.bank_account'

    party = fields.Many2One('party.party', 'Party', required=True,
        ondelete='CASCADE')
    company = fields.Many2One('company.company', 'Company')
    kind = fields.Selection([
            (None, ''),
            ('payable', 'Payable'),
            ('receivable', 'Receivable'),
            ], 'Kind')
    bank_account_owner = fields.Function(fields.Many2One(
            'party.party', 'Bank Account Owner'),
        'on_change_with_bank_account_owner')
    bank_account = fields.Many2One('bank.account', 'Bank Account',
        required=True, ondelete='CASCADE',
        domain=[
            ('owners', '=', Eval('bank_account_owner')),
        ],
        depends=['bank_account_owner'])
    active = fields.Function(fields.Boolean('Active'),
        'get_active', searcher='search_active')

    @classmethod
    def default_company(cls):
        return Transaction().context.get('company')

    @fields.depends('party')
    def on_change_with_bank_account_owner(self, name=None):
        if self.party:
            return self.party.id

    def get_active(self, name):
        return self.bank_account.active

    @classmethod
    def search_active(cls, name, clause):
        return [('bank_account.active',) + tuple(clause[1:])]


class Party:
    __metaclass__ = PoolMeta
    __name__ = 'party.party'
    default_bank_accounts = fields.One2Many('party.party.default.bank_account',
        'party', 'Default Bank Accounts',
        states={
            'invisible': Len(Eval('bank_accounts', [])) < 2,
            },
        depends=['bank_accounts'])
    company_default_bank_accounts = fields.Function(
        fields.One2Many('party.party.default.bank_account',
            'party', 'Default Bank Accounts',
            domain=[
                ('company', 'in',
                    [None, Eval('context', {}).get('company', -1)]),
                ],
            states={
                'invisible': Len(Eval('bank_accounts', [])) < 2,
                },
            depends=['bank_accounts']),
        'get_company_default_bank_accounts',
        setter='set_company_default_bank_accounts')

    def get_company_default_bank_accounts(self, name):
        company = Transaction().context.get('company', -1)
        return [d.id for d in self.default_bank_accounts if
            (not d.company or d.company.id == company)]

    @classmethod
    def set_company_default_bank_accounts(cls, parties, name, value):
        cls.write(parties, {'default_bank_accounts': value})

    def get_default_bank_account(self, pattern=None):
        'Get the default bank account of a party'
        context = Transaction().context
        if pattern is None:
            pattern = {}

        pattern = pattern.copy()
        if 'company' in context:
            pattern.setdefault('company', context['company'])

        bank_account = None
        for line in self.default_bank_accounts:
            if line.match(pattern):
                bank_account = line.bank_account
                break
        if not bank_account and len(self.bank_accounts) == 1:
            bank_account = self.bank_accounts[0]
            if 'bank_account_owner' in pattern:
                owner = pattern['bank_account_owner']
                # Clear if owner is not applicable
                if owner not in [o.id for o in bank_account.owners]:
                    bank_account = None
        return bank_account
