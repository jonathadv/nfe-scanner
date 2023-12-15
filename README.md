# nfe-scanner

Scanner for Brazilian NFe

## Setup
```bash
poetry install
```

## Run as module

```bash
$ python -m nfe_reader 'https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p=00000000000000000000000000000000000000000000|2|1|1|AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'

Fetching NFe NfeUrl(access_key='00000000000000000000000000000000000000000000|2|1|1|AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', host='www.sefaz.rs.gov.br').
=========================RESULT=========================
Access Key: 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000
Issuer: MERCADO
Date: 2023-11-01 11:19:40+00:00

Consumer: identification='Consumidor não identificado'
Total Amount: 42.71

Total Discounts: 0.00

Payment Type: CREDIT_CARD

BETERRABA GRANEL (0.5102 KG * 5.39 = R$2.75)
OVO BRANCO EXTRA NATUROVOS C/30 (1 UNIT * 14.9 = R$14.90)
BEB L YOPRO CHOC Z.L 25 250ML (1 UNIT * 9.98 = R$9.98)
LTE FERM YAKULT 480G (1 UNIT * 12.29 = R$12.29)
SALSA (1 UNIT * 2.79 = R$2.79)
--------------------------------------------------
```

## Use as library

```python
>>> from nfe_scanner.models import Nfe
>>> from nfe_scanner.nfe import scan_nfe
>>> url = 'https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p=00000000000000000000000000000000000000000000|2|1|1|AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
>>> scanned_nfe: Nfe = scan_nfe(url)
Fetching NFe NfeUrl(access_key='00000000000000000000000000000000000000000000|2|1|1|AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', host='www.sefaz.rs.gov.br').
>>> scanned_nfe.access_key
'0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000'
>>> scanned_nfe.issued_date
datetime.datetime(2023, 11, 1, 11, 19, 40, tzinfo=tzutc())
>>> scanned_nfe.payment_type
<PaymentType.CREDIT_CARD: 'CREDIT_CARD'>
>>> scanned_nfe.total_amount
Decimal('42.71')
>>> scanned_nfe.total_discounts
Decimal('0.00')
>>> scanned_nfe.items
[NfeItem(barcode='2044420000002', description='BETERRABA GRANEL', quantity=Decimal('0.5102'), metric_unit=<MetricUnit.KG: 'KG'>, unitary_price=Decimal('5.39'), total_price=Decimal('2.75')), NfeItem(barcode='7896715601129', description='OVO BRANCO EXTRA NATUROVOS C/30', quantity=Decimal('1'), metric_unit=<MetricUnit.UNIT: 'UNIT'>, unitary_price=Decimal('14.9'), total_price=Decimal('14.90')), NfeItem(barcode='7891025118978', description='BEB L YOPRO CHOC Z.L 25 250ML', quantity=Decimal('1'), metric_unit=<MetricUnit.UNIT: 'UNIT'>, unitary_price=Decimal('9.98'), total_price=Decimal('9.98')), NfeItem(barcode='7891156001040', description='LTE FERM YAKULT 480G', quantity=Decimal('1'), metric_unit=<MetricUnit.UNIT: 'UNIT'>, unitary_price=Decimal('12.29'), total_price=Decimal('12.29')), NfeItem(barcode='7898186050048', description='SALSA', quantity=Decimal('1'), metric_unit=<MetricUnit.UNIT: 'UNIT'>, unitary_price=Decimal('2.79'), total_price=Decimal('2.79'))]

```
