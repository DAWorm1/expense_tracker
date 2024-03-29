import math
from enum import IntEnum
from datetime import date,timedelta
from dateutil.relativedelta import relativedelta
from .models import Transaction
import calendar
from dataclasses import dataclass
from decimal import Decimal

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import QuerySet

@dataclass
class Category():
    name: str
    amount: Decimal
    total_amount: int
    verified_amount: int
    
    @property
    def verified_percentage(self):
        return Decimal((self.verified_amount / self.total_amount)*100)

class Period(IntEnum):
    THIS_MONTH = 1
    LAST_MONTH = 2
    THIS_QUARTER = 3
    THIS_YEAR = 4
    YTD = 5

    @classmethod
    def is_period(cls, period):
        return (period in cls.__members__)
    
    @classmethod
    def get_start_end_date_of_period(cls, period,today: date = date.today()) -> tuple[date,date]:
        match period:
            case cls.THIS_MONTH:
                start_value = date(today.year,today.month,1)
                end_value = date(today.year,today.month,calendar.monthrange(today.year,today.month)[1]) 
            case cls.LAST_MONTH:
                last_month = (today.replace(day=1) - timedelta(days=1))
                start_value = last_month.replace(day=1)
                end_value = date(last_month.year,last_month.month,calendar.monthrange(last_month.year,last_month.month)[1])
            case cls.THIS_QUARTER:
                start_value = _get_dates_quarter_first_day(today)
                end_value = start_value + relativedelta(months=+3)
            case cls.THIS_YEAR:
                start_value = date(today.year,1,1)
                end_value = date(today.year,12,31)
            case cls.YTD:
                start_value = today - relativedelta(years=1)
                end_value = today
            case _:
                raise NotImplementedError("Haven't implemented this period type yet.")

        return (start_value, end_value)

def _get_dates_quarter_first_day(day_to_check: date):
    quarter=math.ceil(day_to_check.month/3.)

    if quarter==1:
        return date(day_to_check.year,1,1)
    if quarter==2:
        return date(day_to_check.year,4,1)
    if quarter==3:
        return date(day_to_check.year,7,1)
    if quarter==4:
        return date(day_to_check.year,10,1)


def _get_transactions_by_date(start_value: date, end_value: date, transaction: bool, **kwargs):    
    period_str = "transaction_date" if transaction else "posted_date"
    date_filter = {}

    if start_value:
        date_filter[str(period_str+"__gte")] = start_value.isoformat()
            
    if end_value:
        date_filter[str(period_str+"__lte")] = end_value.isoformat()

    return Transaction.objects.filter(**date_filter,**kwargs)    


"""
Parameters:
    period: a value from the `Period` enum. 
    transaction: whether we're filtering based on transaction_date or posted_date. If True, filter based on transaction_date.

Returns:
    The string to use to filter by this specified Period. 
"""
def get_transactions_filter_by_period(period: Period, transaction:bool = True, today=date.today(), **kwargs) -> 'QuerySet[Transaction]':
    start_value = None
    start_value,end_value = Period.get_start_end_date_of_period(period,today)

    return _get_transactions_by_date(start_value, end_value, transaction)

    
    
def get_transactions_filter_by_date(start_date: date, end_date: date, transaction:bool = True, **kwargs):
    if type(start_date) is not date and type(end_date) is not date:
        raise Exception("A Date must be passed in order to filter by date. ")

    return _get_transactions_by_date(start_date,end_date,transaction,**kwargs)
    

