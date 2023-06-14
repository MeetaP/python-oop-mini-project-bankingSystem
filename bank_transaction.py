from sqlalchemy import create_engine
from sqlalchemy import Column, String, Float, ForeignKey, Integer, Date
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import date
import secrets
import logging

Base = declarative_base()
secretsGenerator = secrets.SystemRandom()

"""Bank Transaction system app to create account, deposit and withdraw amount
    Class:
        Customer: To create a new customer in db
        BankAccount: To make deposit and withdraw amount from BankAccount table in db

    """
class Customer(Base):
    """Class Customer: Creates a customer object and corresponding Customer table in db
            Customer class has methods to create object and init and repr methods to instantiate and print object
            Attributes:
                 first_name: first name of customer
                 last_name: last_name of customer
                 password: customer passowrd
                 city: customer city
                 state: customer state
    """
    __tablename__ = 'customer'
    cid = Column('cid', Integer)
    first_name = Column('first_name', String, primary_key=True)
    last_name = Column('last_name', String)
    password = Column('password', String)
    city = Column('city', String)
    state = Column('state', String)
    
    def __init__(self, cid, first_name, last_name, password, city, state):
        self.cid = cid
        self.first_name = first_name
        self.last_name = last_name
        self.city = city
        self.state = state
        self.password = password
    
    def __repr__(self):
        return f'{self.cid} {self.first_name} {self.last_name} {self.city} {self.state}'


class BankAccount(Base):
    """Class BankAccount: Creates a bank account object and corresponding BankAccount table in db
                    BankAccount class has methods to create account, make deposit, withdraw
                    BanckAccount table object has first name as foreign key referncing Customer table
    """
  
    __tablename__ = 'bankaccount'
    account_id = Column('account_id', Integer, primary_key=True)
    fk_cid = Column(Integer, ForeignKey('customer.cid'))
    account_type = Column('account_type', String)
    balance = Column('balance', Float)

    def __init__(self, fk_cid):
        print(f'Welcome back!')
        self.fk_cid = fk_cid

    def create_account(self, account_id, account_type, fk_cid):
        self.account_id = account_id
        self.account_type = account_type
        self.cid = fk_cid
        self.balance = 0

    def __repr__(self):
        return f'{self.account_id} {self.fk_cid} {self.account_type} {self.balance}'

    def deposit(self, amount, account_no):
        # Get the corresponding row for accoint number from bank account table
        result = session.query(BankAccount).filter(BankAccount.account_id == account_no).first()
        print(f'result of bank account object: {result}')
        # Add input amount to current balance
        new_balance = result.balance + amount
        logging.info(f'You have successfully deposited {amount} and your final balance is {new_balance}')
        return new_balance 
    
    def withdraw(self, amount, account_no):
        # Get the corresponding customer record from bank account table
        result = session.query(BankAccount).filter(BankAccount.account_id == account_no).first()
        print(f'result of bank account object in withdraw method: {result}')
        # Check if current balance is gt than requested amount to withdraw
        if result.balance < amount:
            logging.info(f'Please deposit more funds before withdrawal')
            print(f'Please deposit more funds before withdrawal')
        else: 
            new_balance = result.balance - amount
            logging.info(f'You have successfully withdrawn {amount} and your final balance is {new_balance}')
            return new_balance
        
class Transactions(Base):
    __tablename__ = 'transactions'
    transaction_id = Column('transaction_id', Integer, primary_key=True)
    transaction_date = Column('transaction_date', Date)
    account_id = Column('fk_account_id', Integer, ForeignKey('bankaccount.account_id'))
    transaction_name = Column('transaction_name', String)
    debit = Column('debit', Float)


    def __init__(self, transaction_id, transaction_date, account_no, transaction_name, amount):
        self.transaction_id = transaction_id
        self.transaction_date = transaction_date
        self.account_id = account_no
        self.transaction_name = transaction_name
        self.debit = amount

    def update_cc_stmt(self):
        result = session.query(BankAccount, Transactions).filter(Transactions.account_id == BankAccount.account_id).all()
        result[0][0].balance = result[0][1].debit
        session.commit()


    
# Create db connection
engine = create_engine('sqlite:///mp_db.db')
Base.metadata.create_all(bind=engine)
# Create sesison object to access tables in db
Session = sessionmaker(bind=engine) 
session = Session()
#logger object to print messages to a file
logging.basicConfig(filename='banking_system.log', level=logging.INFO)
logging.info('Started')
# Get customer id from user
print('Hi Welcome to Gringrots bank!')
customer_id = input('Please enter your customer id:\n')
# Check if input first_name exists in customer table
check_record = session.query(Customer).filter(Customer.cid.in_([customer_id])).all()

# if record exists ask user for further options else ask user to create account
if len(check_record) == 0:
    print('Account does not exist. Would you like to create a new account?\n')
    logging.warning('Account does not exist')
    response = 1
elif len(check_record) > 0:
    print(f'Welcome, {check_record[0].first_name}\n')
    print('Please select appropriate option below\n')
# Get user input for type of transaction
while True:
    response = int(input('Please enter one of the below options to continue:\n \
                     Please enter 1 to create account\n \
                     Please enter 2 to deposit\n \
                     Please enter 3 to withdraw\n \
                     Please enter 0 to exit\n')
    )
    # if response = 1 then create a new customer record and bank account record in tables
    if response == 1:
        if len(check_record) == 0:
        # get user first_name, last name, password, city, state and account type 
            first_name = input('Please enter your first name:\n')
            last_name = input('Please enter your last name:\n')
            cid = secretsGenerator.randint(1000, 10000)
            password = input('Enter password for your account:\n')
            city = input('Please enter city where you live:\n')
            state = input('Please enter state where you live:\n')
            cust = Customer(cid, first_name, last_name, password, city, state)
            
            session.add(cust)
            session.commit()
            logging.info(f'Customer record created in Customer table')
        account_type = input('What type of account do you want to open?:\n \
                                enter s for saving or\n \
                             c for checking\n \
                             credit for credit card\n \
                             l for loan\n')
        if account_type == 's':
            account_type = 'saving'
        elif account_type == 'c':
            account_type = 'checking'
        elif account_type == 'credit':
            account_type = 'credit_card'
        elif account_type == 'l':
            account_type = 'loan'
 
        # create BankAccount object
        if len(check_record) == 0:
            customer_id = cust.cid
        else:
            customer_id
        cust_name = session.query(Customer).filter(Customer.cid == customer_id).first()
        acct = BankAccount(customer_id)
        # generate random encrypted account id
        account_id = secretsGenerator.randint(1000, 10000)
        # generate random account number and pass account type and first_name parameters
        acct.create_account(account_id, account_type, customer_id)
        # add bankaccount object to table and commit
        session.add(acct)
        session.commit()
        logging.info(f'Account created in BankAccount table')
    elif response == 2:
        # create bankaccount object and request user input to deposit amount
        acct = BankAccount(customer_id)
        no_of_accounts = session.query(BankAccount).filter(BankAccount.fk_cid == customer_id).filter(BankAccount.account_type.in_(['checking','saving'])).all()
        #Check the number of accounts
        # if more than 1 then loop through the list and display all accounts for user to select from
        if len(no_of_accounts) > 1:
            print(f'Which account would you like to access?\n')
            for i in range(len(no_of_accounts)):
                print(f'account {i + 1}, account_id: {no_of_accounts[i].account_id}, account type: {no_of_accounts[i].account_type}')
        #if only single account exists then ask the user to withdraw fomr that account
        elif len(no_of_accounts) == 1:
            print(f'account 1, account_id: {no_of_accounts[0].account_id}, account type :{no_of_accounts[0].account_type}')
        else:
            print('You do not have an account with us. Please create and then try to withdraw')
            response = int(input('Please enter one of the below options to continue:\n \
                     Please enter 1 to create account\n \
                     Please enter 2 to deposit\n \
                     Please enter 3 to withdraw\n \
                     Please enter 0 to exit\n'))

        account_no = int(input('Please enter account id in which you would like to deposit today\n'))
        amount = int(input('Please enter amount to deposit\n'))
        # call deposit method and pass amount and first_name
        new_amount = acct.deposit(amount, account_no)
        # get corresponding customer record from backaccount table where firstname matches foreign key in bankaccount
        value = session.query(BankAccount).filter(BankAccount.account_id == account_no).first()
        # update balance from the result of query to new balance
        value.balance = new_amount
        session.commit()
    elif response == 3:
        # create bankaccount object and request user input to deposit amount
        acct = BankAccount(customer_id)
        no_of_accounts = session.query(BankAccount).filter(BankAccount.fk_cid == customer_id).filter(BankAccount.account_type.in_(['checking','saving'])).all()
        print(f'no_of_accounts {no_of_accounts}')
        if len(no_of_accounts) > 1:
            print(f'Which account would you like to access?\n')
            for i in range(len(no_of_accounts)):
                print(f'account {i + 1}, account_id: {no_of_accounts[i].account_id}, account type: {no_of_accounts[i].account_type}')
        elif len(no_of_accounts) == 1:
            print(f'account 1, account_id: {no_of_accounts[0].account_id}, account type :{no_of_accounts[0].account_type}')
        else:
            print('You do not have an account with us. Please create and then try to withdraw')
            response = int(input('Please enter one of the below options to continue:\n \
                     Please enter 1 to create account\n \
                     Please enter 2 to deposit\n \
                     Please enter 3 to withdraw\n \
                     Please enter 0 to exit\n'))

        account_no = int(input('Please enter account id from which you would like to withdraw today\n'))
        amount = int(input('Please enter amount to withdraw\n'))
        withdrawn_amount = acct.withdraw(amount, account_no)
        # check if returned values is not None
        if withdrawn_amount:
            # get corresponding customer record from backaccount table where firstname matches foreign key in bankaccount
            withdraw_query = session.query(BankAccount).filter(BankAccount.account_id == account_no).first()
            # update balance from the result of query to new balance
            withdraw_query.balance = withdrawn_amount
            session.commit()
    else:
        # break loop
        response = 0
        logging.info('Finished!')
        print('Thank you for using Gringots bank!')
        break



    
# Manually inserted transactions to Transactions table for credit card transactions
# t1 = Transactions(secretsGenerator.randint(10001, 20000), date.today(), 1346, 'Shoes', 30)
# session.add(t1)
# session.commit()


# Transactions.__table__.drop(engine)




