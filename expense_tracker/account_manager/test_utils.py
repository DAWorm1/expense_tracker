from django.test import TestCase
from decimal import Decimal
from account_manager.models import Account,Transaction
from datetime import date
from django.db.models import Sum
from account_manager.utils import get_total_expenses_from_transactions, get_total_income_from_transactions
from account_manager.filters import Period,get_transactions_filter_by_period

class UtilsTestCase(TestCase):
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

    def test_get_total_income_from_transactions_this_month(self):
        today = date(2023,10,5)

        correct_income = Transaction.objects.filter(
            transaction_date__gte=date(2023,10,1).isoformat(),
            transaction_date__lte=date(2023,10,31).isoformat()
        ).aggregate(Sum("credit_amount"))["credit_amount__sum"]
        
        calc_income = get_total_income_from_transactions(
            get_transactions_filter_by_period(Period.THIS_MONTH,
                                              today=today)
        )

        self.assertAlmostEqual(correct_income,calc_income)

    def test_get_total_expenses_from_transactions_this_month(self):
        today = date(2023,10,5)

        tr = Transaction.objects.filter(
            transaction_date__gte=date(2023,10,1).isoformat(),
            transaction_date__lte=date(2023,10,31).isoformat()
        )

        correct_expenses = abs(tr.aggregate(Sum("debit_amount"))["debit_amount__sum"])
        
        calc_expenses = get_total_expenses_from_transactions(
            get_transactions_filter_by_period(Period.THIS_MONTH,
                                              today=today)
        )

        self.assertAlmostEqual(correct_expenses,calc_expenses)

    def test_get_total_expenses_from_transactions_none(self):
        #Purposefully set up so no Transactions will be found. 
        tr = Transaction.objects.filter(
            debit_amount=Decimal(0),
            credit_amount=Decimal(0)
        )

        self.assertEqual(0,tr.count())

        correct_expenses = Decimal(0)
        
        calc_expenses = get_total_expenses_from_transactions(tr)
        
        self.assertAlmostEqual(correct_expenses,calc_expenses)