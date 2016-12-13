# This file is part of company_bank module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from sql import Literal
from sql.functions import CurrentTimestamp

from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond import backend

__all__ = ['BankAccountParty']


class BankAccountParty:
    __metaclass__ = PoolMeta
    __name__ = 'bank.account-party.party'

    @classmethod
    def __register__(cls, module_name):
        pool = Pool()
        DefaultBank = pool.get('party.party.default.bank_account')
        cursor = Transaction().connection.cursor()
        TableHandler = backend.get('TableHandler')
        sql_table = cls.__table__()
        default_bank = DefaultBank.__table__()
        table = TableHandler(cls, module_name)

        super(BankAccountParty, cls).__register__(module_name)

        # Migration from 4.2: drop required on company
        table.not_null_action('company', action='remove')
        # Migration from 4.2: Move default bank accounts to new model
        for kind in ['payable', 'receivable']:
            column = '%s_bank_account' % kind
            if table.column_exist(column):
                select = sql_table.select(Literal(0), CurrentTimestamp(),
                            sql_table.id, Literal(kind),
                            sql_table.owner, sql_table.company,
                            where=getattr(sql_table, column))
                cursor.execute(*default_bank.insert(
                        columns=[default_bank.create_uid,
                            default_bank.create_date,
                            default_bank.bank_account, default_bank.kind,
                            default_bank.party, default_bank.company],
                        values=select))
                table.drop_column(column)
