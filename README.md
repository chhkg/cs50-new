# chhkg


## Project Title:
Trading Performance Calculator


## TLDR:
* This application helps users track their trading performance. The accepted assets include stock, fiat money and cryptocurrency.
* There are 3 main pages: Current Holding, Transaction History, and Performance.
* Current Holding:
    * Listing all current holdings of stocks, fiat money, and cryptocurrencies.
* Transaction History:
    * Displaying all transaction records created by users.
* Performance:
    * Displaying all processed performance statistics generated from the transaction records.


## Distinctiveness and Complexity:
* This application is distinctive from previous projects because none of them tracks trading performance. 
* There are new features which do not exist in previous projects and make this project complex:
    * In django forms, the fields are dynamic according to the input (check the transaction creation form) using javascript
    * Soft delete is implemented instead of deleting an object from DB
    * Users sign up and login by email instead of the default django behaviour to log in by username
    * There are calculations of data from DB which uses syntax like `annotate.()`, `interest = Sum(Case(When(type="Interest", then=F('proceed'))))`
    * There are cases requiring null and not null handling, like `dividend_notnull = Coalesce(Sum(Case(When(type="Dividend", then=F('proceed')))), Value(0, output_field=DecimalField()))`
    * Search form is implemented to filter data in tables
    * Multiple date range search (weekly, monthly, and yearly) is implemented so that users can review the performance of different time intervals.


## What's contained in each file
* static/stockcalculator
    * /images
        * Containing all image files
    * /module.js
        * Containing javascript shared by other js files
    * /performance.js
        * Containing javascript extended to performance.html
    * /transaction.js
        * Containing javascript extended to transaction.html
* templates
    * /currentholding.html
        * Display the existing holding of stocks (grouped by currencies), fiat currency, and cryptocurrency
        * Involve calculation of DB objects to get data such as average/total cost of each stock, total amount of each currency etc
    * /index.html
        * Index page
    * /layout.html
        * Contain the desktop and mobile hanburger menu
    * /login.html
        * Login by email
    * /performance.html
        * Display the performance of stock, fiat money, or cryptocurrency
        * Filter performance by assets and time interval
        * Pagination
    * /register.html
        * Register by email
    * /transaction.html
        * Create transaction (form fields are dynamic)
        * Search transaction
        * Edit transaction (remark of transaction)
        * Delete transaction
        * Clear search
        * Pagination
* authentication.py
    * Contain the email authentication class
* choices.py
    * Contain all choices of forms
* forms.py
    * Contain all forms
* models.py
    * Contain 5 models of User, Transaction, StockHolding, FiatHolding, CryptoHolding
    * Contain a SoftDeleteModelManager
* urls.py
    * Contain 7 pages and 2 APIs
* views.py
    * Contain 7 functions and 2 classes
    * Class LoginView: Manage login
    * Class RegisterView: Manage registration
    * Function logout_view : Manage log out
    * Function index: Render index page
    * Function currentholding:
        * Calculate the current holdings of different assets
        * Return a message if no holding of any asset
        * Render the currenholding page
    * Function performance
        * Calculate the performance of different intervals of different assets
        * Return a message if no holding of any asset
        * Render the performance page
        * Pagination
    * Function transaction
        * Handle transaction search form
        * Handle transaction create form - Create transaction with special handling of different assets and transaction types
        * While creating a transaction, it also add / update objects in other models (e.g. selling a stock will increase the corresponding fiatmoney and deducts the stockholding)
        * There are checking that users cannot sell a stock more than they own before the selling date
        * A user can sell a stock which was bought from multiple transactions, so the selling will be first in first out, which deducts stocks from older transactions first
    * Function edit_transaction
        * Edit the remark field of a transaction object
        * A user can only edit their own transactions
    * Function delete_transaction
        * Delete a transaction with special handling of different assets or transaction types
        * While deleting a transaction, it also delete / update objects in other models
        * A user can only delete their own transactions


## How to run the application
* Download the libraries in requirement.txt
* CD to ../Project 5 Final/project5 and run server
