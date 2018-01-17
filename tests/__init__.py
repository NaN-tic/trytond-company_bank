# This file is part company_bank module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
try:
    from trytond.modules.company_bank.tests.test_company_bank import suite
except ImportError:
    from .test_company_bank import suite

__all__ = ['suite']
