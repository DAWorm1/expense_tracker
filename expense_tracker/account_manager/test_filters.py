from django.test import TestCase
from account_manager.models import Transaction,Account
from account_manager.filters import get_transactions_filter_by_period,Period
from decimal import Decimal
from datetime import date

class FilterTestCase(TestCase):
    def setUp(self) -> None:
        self.checking = Account.objects.create(name="Bank of America", type=1) #Checking Account
        self.credit = Account.objects.create(name="Discover", type=2) #Credit Card Account

        self.checking_transactions = [
            Transaction.objects.create(
                transaction_date="2023-10-01",
                posted_date="2023-10-01",
                account=self.checking,
                description="Transaction",
                category="",
                category_certainty=None,
                debit_amount=Decimal(20),
                credit_amount=Decimal(0)
            ),
            Transaction.objects.create(
                transaction_date="2023-11-12",
                posted_date="2023-11-14",
                account=self.checking,
                description="Transaction",
                category="",
                category_certainty=None,
                debit_amount=Decimal(50),
                credit_amount=Decimal(0)
            ),
            Transaction.objects.create(
                transaction_date="2023-12-01",
                posted_date="2023-12-02",
                account=self.checking,
                description="Deposit",
                category="",
                category_certainty=None,
                debit_amount=Decimal(0),
                credit_amount=Decimal(4000)
            ),   
        ]

        self.credit_card_transactions = [
            Transaction.objects.create(
                transaction_date="2023-10-10",
                posted_date="2023-10-11",
                account=self.credit,
                description="Transaction",
                category="",
                category_certainty=None,
                debit_amount=Decimal(5),
                credit_amount=Decimal(0)
            ),
            Transaction.objects.create(
                transaction_date="2023-12-15",
                posted_date="2023-12-16",
                account=self.credit,
                description="Transaction",
                category="",
                category_certainty=None,
                debit_amount=Decimal(20),
                credit_amount=Decimal(0)
            ),

            Transaction.objects.create(
                transaction_date="2023-12-30",
                posted_date="2024-01-02",
                account=self.checking,
                description="Transaction",
                category="",
                category_certainty=None,
                debit_amount=Decimal(0),
                credit_amount=Decimal(25)
            ),
        ]

    def test_is_value_valid_filter(self):
        query = "THIS_MONTH"
        self.assertTrue(Period.is_period(query))
        self.assertEqual(Period[query],1)
        query = "LAST_MONTH"
        self.assertTrue(Period.is_period(query))
        self.assertEqual(Period[query],2)
        query = "THIS_QUARTER"
        self.assertTrue(Period.is_period(query))
        self.assertEqual(Period[query],3)
        query = "THIS_YEAR"
        self.assertTrue(Period.is_period(query))
        self.assertEqual(Period[query],4)
        query = "YTD"
        self.assertTrue(Period.is_period(query))
        self.assertEqual(Period[query],5)


    def test_get_transactions_this_month(self):
        today = date(2023,10,5)
        correct_transactions = list(Transaction.objects.filter(
            transaction_date__gte=date(2023,10,1).isoformat(),
            transaction_date__lte=date(2023,10,31).isoformat()
        ))

        qs = list(get_transactions_filter_by_period(Period.THIS_MONTH,today=today))

        self.assertListEqual(correct_transactions,qs)

    def test_get_transactions_last_month(self):
        today = date(2023,11,5)
        correct_transactions = list(Transaction.objects.filter(
            transaction_date__gte=date(2023,10,1).isoformat(),
            transaction_date__lte=date(2023,10,31).isoformat()
        ))

        qs = list(get_transactions_filter_by_period(Period.LAST_MONTH,today=today))

        self.assertListEqual(correct_transactions,qs)
        pass

    def test_get_transactions_this_quarter(self):
        today = date(2023,11,15)
        correct_transactions = list(Transaction.objects.filter(
            transaction_date__gte=date(2023,10,1).isoformat(),
            transaction_date__lte=date(2023,12,31).isoformat()
        ))

        qs = list(get_transactions_filter_by_period(Period.THIS_QUARTER,today=today))

        self.assertListEqual(correct_transactions,qs)
    
    def test_get_transactions_this_year(self):
        today = date(2023,11,15)
        correct_transactions = list(Transaction.objects.filter(
            transaction_date__gte=date(2023,1,1).isoformat(),
            transaction_date__lte=date(2023,12,31).isoformat()
        ))

        qs = list(get_transactions_filter_by_period(Period.THIS_YEAR,today=today))

        self.assertListEqual(correct_transactions,qs)
    
    def test_get_transactions_ytd(self):
        today = date(2023,11,15)
        correct_transactions = list(Transaction.objects.filter(
            transaction_date__gte=date(2022,11,15).isoformat(),
            transaction_date__lte=date(2023,11,15).isoformat()
        ))

        qs = list(get_transactions_filter_by_period(Period.YTD,today=today))

        self.assertListEqual(correct_transactions,qs)
