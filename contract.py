"""
CSC148, Winter 2019
Assignment 1

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2019 Bogdan Simion, Diane Horton, Jacqueline Smith
"""
import datetime
from typing import Optional
from math import ceil
from bill import Bill
from call import Call


# Constants for the month-to-month contract monthly fee and term deposit
MTM_MONTHLY_FEE = 50.00
TERM_MONTHLY_FEE = 20.00
TERM_DEPOSIT = 300.00

# Constants for the included minutes and SMSs in the term contracts (per month)
TERM_MINS = 100

# Cost per minute and per SMS in the month-to-month contract
MTM_MINS_COST = 0.05

# Cost per minute and per SMS in the term contract
TERM_MINS_COST = 0.1

# Cost per minute and per SMS in the prepaid contract
PREPAID_MINS_COST = 0.025


class Contract:
    """ A contract for a phone line

    This is an abstract class. Only subclasses should be instantiated.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.date
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        self.start = start
        self.bill = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        raise NotImplementedError

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        return self.bill.get_cost()


class TermContract(Contract):
    """A Term contract for a phone line


    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    end: ending date for the contract
    year: current year of the contract
    month: current month of the contract
    """
    start: datetime.date
    bill: Optional[Bill]
    end: datetime.date
    month: int
    year: int

    def __init__(self, start: datetime.date, end: datetime.date) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        Contract.__init__(self, start)
        self.end = end
        self.year = self.start.year
        self.month = self.start.month

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
            <year>. This may be the first month of the contract.
            Store the <bill> argument in this contract and set the appropriate
            rate per minute and fixed cost.
            """

        self.year = year
        self.month = month

        if self.start is not None:
            if month == self.start.month and year == self.start.year:
                bill.add_fixed_cost(TERM_DEPOSIT)
            bill.free_min = 0
            bill.add_fixed_cost(TERM_MONTHLY_FEE)
            bill.set_rates("TERM", TERM_MINS_COST)
        self.bill = bill

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        bill_m = ceil(call.duration / 60.0) + self.bill.free_min - TERM_MINS

        if bill_m > 0:
            self.bill.free_min = TERM_MINS
            self.bill.add_billed_minutes(bill_m)
        else:
            if bill_m == 0:
                self.bill.free_min = TERM_MINS
            elif bill_m < 0:
                self.bill.add_free_minutes(ceil(call.duration / 60.0))

            self.bill.add_billed_minutes(0)

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        new_date = datetime.date(self.year, self.month, 1)
        self.start = None

        if new_date > self.end:
            self.bill.add_fixed_cost(-TERM_DEPOSIT)
        return self.bill.get_cost()


class MTMContract(Contract):
    """A Term contract for a phone line

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    year: current year of the contract
    month: current month of the contract
    """
    start: datetime.date
    bill: Optional[Bill]
    month: int
    year: int

    def __init__(self, start: datetime.date) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        Contract.__init__(self, start)
        self.year = self.start.year
        self.month = self.start.month

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
            <year>. This may be the first month of the contract.
            Store the <bill> argument in this contract and set the appropriate
            rate per minute and fixed cost.
            """

        self.year = year
        self.month = month
        if self.start is not None:
            bill.add_fixed_cost(MTM_MONTHLY_FEE)
            bill.set_rates("MTM", MTM_MINS_COST)
        self.bill = bill

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """

        self.start = None
        return self.bill.get_cost()


class PrepaidContract(Contract):
    """A Term contract for a phone line

        === Public Attributes ===
        start:
             starting date for the contract
        bill:
             bill for this contract for the last month of call records loaded
             from the input dataset
        balance: the associated balance of the contract
        year: current year of the contract
        month: current month of the contract

        """
    start: datetime.date
    bill: Optional[Bill]
    balance: int
    month: int
    year: int
    count: int

    def __init__(self, start: datetime.date, balance: int) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        Contract.__init__(self, start)
        self.balance = -1 * balance
        self.year = self.start.year
        self.month = self.start.month
        self.count = 0

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
            <year>. This may be the first month of the contract.
            Store the <bill> argument in this contract and set the appropriate
            rate per minute and fixed cost.
            """

        self.year = year
        self.month = month
        if self.start is not None:
            self.count += 1
            if self.count == 1:
                bill.add_fixed_cost(self.balance)
            else:
                if self.balance > -10:
                    self.balance -= 25
                bill.add_fixed_cost(self.balance)
            self.balance = bill.get_summary()['total']
            bill.set_rates("PREPAID", PREPAID_MINS_COST)
        self.bill = bill

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        bill_m = ceil(call.duration / 60.0)
        self.bill.add_billed_minutes(bill_m)
        self.balance += bill_m * PREPAID_MINS_COST

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        bill_summary = self.bill.get_summary()
        if bill_summary['total'] < 0:
            self.balance = 0
            bill_summary['total'] = 0
        return bill_summary['total']


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'bill', 'call'
        ],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })
