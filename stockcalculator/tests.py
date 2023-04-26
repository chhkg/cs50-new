from django.test import TestCase

# Create your tests here.

""""""
"""Create Transaction"""
""""""

"""PASS"""
# If asset is Stock, and type is Deposit or Withdrawal
    # Show an error message "Error: Type cannot be Deposit/Withdrawal for Stock"

"""PASS"""
# If asset is Stock, and type is Buy
    # Create a Transaction object, basis is negative number, currency and symbol are required
    # Create a StockHolidng object
    # Create a FiatHolding object to deduct fiat money

"""PASS"""
# If asset is Stock, and type is Sell, but selling a stock more than the user owns
    # Show an error message

"""PASS"""
# If asset is Stock, and type is Sell, but selling a stock the user does not own
    # Show an error message

"""PASS"""
# If asset is Stock, and type is Sell
    # Create a Transaction object, including the PL, PL% and relatedbuytransaction fields, basis is positive number, currency and symbol are required
    # Update the related StockHolidng objects to reduce quantity and add the selltransaction
    # Create a FiatHolding object to increase fiat money

"""PASS"""
# If asset is Stock, and type is Dividend or Interest
    # Create a Transaction object, currency and symbol are required
    # Create a FiatHolding object to increase fiat money

"""PASS"""
# If asset is Stock, and type is Deduction
    # Create a Transaction object, basis is negative number, currency and symbol are required
    # Create a FiatHolding object to deduct fiat money

"""PASS"""
# If asset is FiatMoney, and type is Buy
    # Create a Transaction object, quantity is positive number, basis is negative number, Buy Currency and Sell Currency are required
    # Create a FiatHolding object to deduct the sold fiat money
    # Create a FiatHolding object to increase the bought fiat money

"""PASS"""
# If asset is FiatMoney, and type is Dividend or Interest
    # Create a Transaction object, currency is required
    # Create a FiatHolding object to increase fiat money

"""PASS"""
# If asset is FiatMoney, and type is Deduction
    # Create a Transaction object, basis is negative number, currency is required
    # Create a FiatHolding object to deduct fiat money

"""PASS"""
# If asset is FiatMoney, and type is Deposit
    # Create a Transaction object, basis is positive number, currency is required
    # Create a FiatHolding object to increase fiat money

"""PASS"""
# If asset is FiatMoney, and type is Withdrawal
    # Create a Transaction object, basis is negative number, currency is required
    # Create a FiatHolding object to decrease fiat money

"""PASS"""
# If asset is Crypto, and type is Buy
    # Create a Transaction object, quantity is positive number, basis is negative number, Buy and Sell crypto symbol are required
    # Create a CryptoHolding object to deduct the sold fiat money
    # Create a CryptoHolding object to increase the bought fiat money

"""PASS"""
# If asset is Crypto, and type is Dividend or Interest
    # Create a Transaction object, basis is positive number, symbol is required
    # Create a CryptoHolding object to increase fiat money

"""PASS"""
# If asset is Crypto, and type is Deduction
    # Create a Transaction object, basis is negative number, symbol is required
    # Create a CryptoHolding object to deduct fiat money

"""PASS"""
# If asset is Crypto, and type is Deposit
    # Create a Transaction object, basis is positive number, symbol is required
    # Create a CryptoHolding object to increase fiat money

"""PASS"""
# If asset is Crypto, and type is Withdrawal
    # Create a Transaction object, basis is negative number, symbol is required
    # Create a CryptoHolding object to decrease fiat money



""""""
"""Delete Transaction"""
""""""

"""PASS"""
# Delete a crypto transaction, type is not Buy
    # Transaction deleted
    # 1 related Cryptoholding deleted

"""PASS"""
# Delete a crypto transaction, type is Buy
    # Transaction deleted
    # 2 related Cryptoholding deleted (Buy and sell holding)

"""PASS"""
# Delete a stock transaction, type is Buy
    # Transaction deleted
    # 1 related Stockholding deleted
    # 1 related Fiatholding deleted

"""PASS"""
# Delete a stock transaction, type is Buy, and a part or this transaction is sold
    # Return JSONResponse, asking the user to delete the related sell transaction first

"""PASS"""
# Delete a stock transaction, type is Sell
    # Transaction deleted
    # All related Stockholding deleted
    # 1 related Fiatholding deleted

"""PASS"""
# Delete a stock transaciton, type is not Buy or Sell
    # Transaction deleted
    # 1 related Fiatholding deleted

"""PASS"""
# Delete a fiat transaction, type is Buy
    # Transaction deleted
    # 2 related Fiattoholding deleted (Buy and sell holding)

"""PASS"""
# Delete a fiat transaction, type is not Buy
    # Transaction deleted
    # 1 related Fiatholding deleted