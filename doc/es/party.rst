#:inside:party/party:section:terceros-multicompania#

* |payable_bank_account|
* |receivable_bank_account|
* |payable_company_bank_account|
* |receivable_company_bank_account|

.. |payable_bank_account| field:: party.party/payable_bank_account
.. |receivable_bank_account| field:: party.party/receivable_bank_account
.. |payable_company_bank_account| field:: party.party/payable_company_bank_account
.. |receivable_company_bank_account| field:: party.party/receivable_company_bank_account


#:after:party/party:paragraph:bank#


Además podemos definir las cuentas bancarias que se utilizarán por defecto
para las transacciones con ese tercero utilizando los siguiente campos:

* |receivable_bank_account|: Cuenta del tercero para girar cobros.
* |payable_bank_account|: Cuenta del tercero para girar pagos.
* |receivable_company_bank_account|: Cuenta de la empresa dónde queremos
  recibir los cobros.
* |payable_company_bank_account|: Cuenta de la empresa desde dónde queremos
  mandar los pagos.
