# This file is part of the company_bank module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool

from trytond.modules.company.tests import create_company, set_company


class CompanyBankTestCase(ModuleTestCase):
    'Test Company Bank module'
    module = 'company_bank'

    @with_transaction()
    def test_default_bank_accounts(self):
        'Test Default Bank Accounts'
        pool = Pool()
        Party = pool.get('party.party')
        Bank = pool.get('bank')
        Account = pool.get('bank.account')

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
            new_account.active = False
            new_account.save()
            self.assertEqual(owner.payable_bank_account, account)
            self.assertEqual(owner.receivable_bank_account, account)
            account.active = False
            account.save()
            self.assertIsNone(owner.payable_bank_account)
            self.assertIsNone(owner.receivable_bank_account)


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        CompanyBankTestCase))
    return suite
