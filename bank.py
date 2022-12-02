# This file is part of company_bank module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta


class BankAccount(metaclass=PoolMeta):
    __name__ = 'bank.account'

    @classmethod
    def create(cls, vlist):
        Party = Pool().get('party.party')

        records = super(BankAccount, cls).create(vlist)

        parties = set([])
        for r in records:
            parties |= set(r.owners)

        if parties:
            Party.set_default_bank_accounts(parties)
        return records

    @classmethod
    def write(cls, *args):
        Party = Pool().get('party.party')

        parties = set([])
        actions = iter(args)
        to_default_bank_accounts = []
        for accounts, values in zip(actions, actions):
            if ('active' in values and not values['active']) or ('owners' in values):
                to_default_bank_accounts += accounts
                if values.get('owners'):
                    for a in values.get('owners'):
                        if a[0] == 'remove':
                            parties |= set(Party.browse(a[1]))

        super(BankAccount, cls).write(*args)

        if to_default_bank_accounts:
            bank_accounts = cls.browse(to_default_bank_accounts)


            for r in bank_accounts:
                parties |= set(r.owners)

            parties = list(parties)
            if parties:
                Party.set_default_bank_accounts(parties)

    @classmethod
    def delete(cls, bank_accounts):
        Party = Pool().get('party.party')

        parties = set([])
        for r in bank_accounts:
            parties |= set(r.owners)

        super(BankAccount, cls).delete(bank_accounts)

        parties = list(parties)
        if parties:
            Party.set_default_bank_accounts(parties)
