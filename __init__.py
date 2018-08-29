# This file is part of company_bank module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import bank
from . import party


def register():
    Pool.register(
        bank.BankAccount,
        bank.BankAccountParty,
        party.PartyCompanyBankAccount,
        party.Party,
        module='company_bank', type_='model')
