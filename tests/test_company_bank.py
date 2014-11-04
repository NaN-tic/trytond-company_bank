#!/usr/bin/env python
# This file is part company_bank module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import test_view, test_depends


class CompanyBankTestCase(unittest.TestCase):
    'Test Company Bank module'

    def setUp(self):
        trytond.tests.test_tryton.install_module('company_bank')

    def test0005views(self):
        'Test views'
        test_view('company_bank')

    def test0006depends(self):
        'Test depends'
        test_depends()


def suite():
    suite = trytond.tests.test_tryton.suite()
    from trytond.modules.company.tests import test_company
    for test in test_company.suite():
        if test not in suite:
            suite.addTest(test)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        CompanyBankTestCase))
    return suite
