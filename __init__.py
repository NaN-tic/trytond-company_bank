# This file is part of company_bank module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from .bank import *
from .party import *


def register():
    Pool.register(
        BankAccount,
        BankAccountParty,
        PartyCompanyBankAccount,
        Party,
        module='company_bank', type_='model')
