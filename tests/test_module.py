
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool

from trytond.modules.company.tests import (CompanyTestMixin, create_company,
    set_company)


class CompanyBankTestCase(CompanyTestMixin, ModuleTestCase):
    'Test CompanyBank module'
    module = 'company_bank'

    @with_transaction()
    def test_default_bank_accounts(self):
        'Test Default Bank Accounts'
        pool = Pool()
        Party = pool.get('party.party')
        Bank = pool.get('bank')
        Account = pool.get('bank.account')
        AccountNumber = pool.get('bank.account.number')

        company = create_company()
        with set_company(company):
            party = Party(name='Test')
            party.save()
            bank = Bank(party=party)
            bank.save()
            account, = Account.create([{
                        'bank': bank.id,
                        'numbers': [('create', [{
                                        'type': 'other',
                                        'number': 'not IBAN',
                                        }])],
                        }])
            owner = Party(name='Owner')
            owner.save()
            self.assertIsNone(owner.payable_bank_account)
            self.assertIsNone(owner.receivable_bank_account)
            account.owners = [owner]
            account.save()
            owner = Party(owner.id)
            self.assertEqual(owner.payable_bank_account, account)
            self.assertEqual(owner.receivable_bank_account, account)
            new_account, = Account.create([{
                        'bank': bank.id,
                        'owners': [('add', [owner.id])],
                        'numbers': [('create', [{
                                        'type': 'other',
                                        'number': 'Another not IBAN',
                                        }])],
                        }])
            owner = Party(owner.id)
            self.assertEqual(owner.payable_bank_account, account)
            self.assertEqual(owner.receivable_bank_account, account)
            Account.delete([account])
            owner = Party(owner.id)
            self.assertEqual(owner.payable_bank_account, new_account)
            self.assertEqual(owner.receivable_bank_account, new_account)
            new_account.owners = []
            new_account.save()
            self.assertIsNone(owner.payable_bank_account)
            self.assertIsNone(owner.receivable_bank_account)
            new_account.owners = [owner]
            new_account.save()
            account, = Account.create([{
                        'bank': bank.id,
                        'owners': [('add', [owner.id])],
                        'numbers': [('create', [{
                                        'type': 'other',
                                        'number': 'Yet Another not IBAN',
                                        }])],
                        }])
            self.assertEqual(owner.payable_bank_account, new_account)
            self.assertEqual(owner.receivable_bank_account, new_account)

            AccountNumber.write([n for n in new_account.numbers], {'active': False})
            new_account.active = False
            new_account.save()
            self.assertEqual(owner.payable_bank_account, account)
            self.assertEqual(owner.receivable_bank_account, account)

            AccountNumber.write([n for n in account.numbers], {'active': False})
            account.active = False
            account.save()
            self.assertIsNone(owner.payable_bank_account)
            self.assertIsNone(owner.receivable_bank_account)


del ModuleTestCase
