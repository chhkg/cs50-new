import json
import datetime

from datetime import timedelta
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Avg, Sum, F, ExpressionWrapper, FloatField, Value, DecimalField, Min, Max, Count, When, Case
from django.db.models.functions import Cast, ExtractWeek, ExtractMonth, ExtractYear, Concat, Coalesce
from django.db import IntegrityError, models
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from .forms import CreateTransaction, TransactionSearch, PerformanceFilter, Login, Registration, EditTransaction
from .models import User, Transaction, StockHolding, FiatHolding, CryptoHolding

class LoginView(auth_views.LoginView):
    form_class = Login
    template_name = 'stockcalculator/login.html'
    next_page = "currentholding"


class RegisterView(generic.CreateView):
    form_class = Registration
    template_name = 'stockcalculator/register.html'
    success_url = reverse_lazy('currentholding')

    def form_valid(self, form):
        # create the user object
        user = form.save()
        login(self.request, user)
        return HttpResponseRedirect(self.success_url)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def index(request):
    return render(request, "stockcalculator/index.html")

@login_required
def currentholding(request):

    # Get the stock current holding
    stockholding = StockHolding.objects.filter(user=request.user, quantity__gt=0).order_by("symbol")
    stockholding_currency = stockholding.values_list('currency', flat=True).distinct()

    no_stock_message = ""
    no_fiat_message = ""
    no_crypto_message = ""
    
    if stockholding.count() == 0:
        no_stock_message = "No stock is added...yet!"
    
    # Create a dictionary to hold the stock holdings for each currency
    stockholding_by_currency_dictionary = {}
    total_amount_by_currency_dictionary = {}
    
    for currency in stockholding_currency:
        stockholding_by_currency = stockholding.filter(currency=currency).values('symbol').annotate(
            totalquantity=Sum(F('quantity')),
            totalamount=Sum(F('quantity') * F('price')),
        ).annotate(
            averageprice=Cast('totalamount', output_field=FloatField()) / Cast('totalquantity', output_field=FloatField())
        )

        stockholding_by_currency_dictionary[currency] = stockholding_by_currency
        total_amount_by_currency_dictionary[currency] = sum(item['totalamount'] for item in stockholding_by_currency)

    print(total_amount_by_currency_dictionary)

    # Create a dictionary to hold the fiat holdings for each currency
    fiatholding_by_currency = FiatHolding.objects.filter(user=request.user).values('currency').annotate(
            totalholding=Sum('amount')
        )
    
    if fiatholding_by_currency.count() == 0:
        no_fiat_message = "No fiat currency is added...yet!"
    
    # Create a dictionary to hold the fiat holdings for each currency
    cryptoholding_by_currency = CryptoHolding.objects.filter(user=request.user).values('currency').annotate(
            totalholding=Sum('amount')
        )
    
    if cryptoholding_by_currency.count() == 0:
        no_crypto_message = "No cryptocurrency is added...yet!"


    context = {
        'stockholding_currency': stockholding_currency,
        'stockholding_by_currency_dictionary': stockholding_by_currency_dictionary,
        'total_amount_by_currency_dictionary': total_amount_by_currency_dictionary,
        'fiatholding_by_currency': fiatholding_by_currency,
        'cryptoholding_by_currency': cryptoholding_by_currency,
        'no_stock_message': no_stock_message,
        'no_fiat_message': no_fiat_message,
        'no_crypto_message': no_crypto_message,
    }
    return render(request, "stockcalculator/currentholding.html", context)


@login_required
def performance(request):

    no_stock_message = ""
    no_fiat_message = ""
    no_crypto_message = ""
    transactions_by_currency_page_obj = ""

    
    # Get the selected time interval from the form
    performancefilterform = PerformanceFilter(request.GET or None)
    
    if 'asset' in request.GET:
        if performancefilterform.is_valid():
            asset = performancefilterform.cleaned_data.get('asset')
            interval = performancefilterform.cleaned_data.get('interval')
    else:
        # By default, show weekly stock performance
        asset = "Stock"
        interval = "Weekly"

    # Group transactions by week, month, or year, depending on the selected interval
    if interval == 'Weekly':
        group_by_args = {'year', 'week'}
        annotate_kwargs = {'year': ExtractYear('date'), 'week': ExtractWeek('date')}
    elif interval == 'Monthly':
        group_by_args = {'year', 'month'}
        annotate_kwargs = {'year': ExtractYear('date'), 'month': ExtractMonth('date')}
    else:
        group_by_args = {'year': 'year'}
        annotate_kwargs = {'year': ExtractYear('date')}

    if asset == "Stock":
        # Query the stock transaction
        transactions = Transaction.objects.filter(user=request.user, asset="Stock").order_by("-date")
        transactions_currency = transactions.values_list('currency', flat=True).distinct()
        transactions_by_currency_dictionary = {}

        if transactions.count() == 0:
            no_stock_message = "No transaction is added...yet!"
            transactions_by_currency_paginator = Paginator(transactions, 2)
            transactions_by_currency_page_number = request.GET.get('page')
            transactions_by_currency_page_obj = transactions_by_currency_paginator.get_page(transactions_by_currency_page_number)

        for currency in transactions_currency:
            transactions_by_currency = transactions.filter(currency=currency).annotate(**annotate_kwargs).values(*group_by_args).annotate(
                min_date=Min('date'),
                max_date=Max('date'),
                realized_pl_sell = Sum('pl'),
                sell_count = Count(Case(When(type="Sell", then=1))),
                buy_count = Count(Case(When(type="Buy", then=1))),
                win_count = Count(Case(When(pl__gt=0, then=1))),
                avg_win_percent = Avg(Case(When(plpercent__gt=0, then=F('plpercent')))),
                avg_loss_percent = Avg(Case(When(plpercent__lt=0, then=F('plpercent')))),
                max_win_percent = Max(Case(When(plpercent__gt=0, then=F('plpercent')))),
                max_loss_percent = Min(Case(When(plpercent__lt=0, then=F('plpercent')))),
                max_win = Max(Case(When(pl__gt=0, then=F('pl')))),
                max_loss = Min(Case(When(pl__lt=0, then=F('pl')))),
                dividend = Sum(Case(When(type="Dividend", then=F('proceed')))),
                interest = Sum(Case(When(type="Interest", then=F('proceed')))),
                deduction = Sum(Case(When(type="Deduction", then=F('proceed')))),
                fees = Sum('fee'),
                realized_pl_sell_notnull = Coalesce(Sum('pl'), Value(0, output_field=DecimalField())),
                dividend_notnull = Coalesce(Sum(Case(When(type="Dividend", then=F('proceed')))), Value(0, output_field=DecimalField())), 
                interest_notnull = Coalesce(Sum(Case(When(type="Interest", then=F('proceed')))), Value(0, output_field=DecimalField())),
                deduction_notnull = Coalesce(Sum(Case(When(type="Deduction", then=F('proceed')))), Value(0, output_field=DecimalField())),
                fee_notnull = Coalesce(Sum('fee'), Value(0, output_field=DecimalField())),
            ).annotate(
                win_rate = Cast('win_count', output_field=FloatField()) / Cast('sell_count', output_field=FloatField()),
                realized_pl = F('realized_pl_sell_notnull') + F('dividend_notnull') + F('interest_notnull') + F('deduction_notnull') + F('fee_notnull'),
            ).order_by('-min_date')

            for interval_data in transactions_by_currency:
                if interval == 'Weekly':
                    interval_data['start_date'] = interval_data['min_date'] - timedelta(days=interval_data['min_date'].weekday())
                    interval_data['end_date'] = interval_data['max_date'] + timedelta(days=6 - interval_data['max_date'].weekday())
                elif interval == 'Monthly':
                    interval_data['start_date'] = interval_data['min_date'].replace(day=1)
                    next_month = interval_data['min_date'].replace(day=28) + timedelta(days=4)
                    interval_data['end_date'] = next_month - timedelta(days=next_month.day)
                else:
                    interval_data['start_date'] = interval_data['min_date'].replace(month=1, day=1)
                    interval_data['end_date'] = interval_data['max_date'].replace(month=12, day=31)
                    
            transactions_by_currency_paginator = Paginator(transactions_by_currency, 2)
            transactions_by_currency_page_number = request.GET.get('page')
            transactions_by_currency_page_obj = transactions_by_currency_paginator.get_page(transactions_by_currency_page_number)
            transactions_by_currency_dictionary[currency] = transactions_by_currency_page_obj

            # transactions_by_currency_dictionary[currency] = transactions_by_currency
    
    else:
        # Query the fiat or crypto holding
        if asset == "FiatMoney":
            transactions = FiatHolding.objects.filter(user=request.user).order_by("-date")
            if transactions.count() == 0:
                no_fiat_message = "No transaction is added...yet!"
        else:
            transactions = CryptoHolding.objects.filter(user=request.user).order_by("-date")
            if transactions.count() == 0:
                no_crypto_message = "No transaction is added...yet!"
        
        transactions_currency = transactions.values_list('currency', flat=True).distinct()
        transactions_by_currency_dictionary = {}

        

        for currency in transactions_currency:
            transactions_by_currency = transactions.filter(currency=currency).annotate(**annotate_kwargs).values(*group_by_args).annotate(
                min_date=Min('date'),
                max_date=Max('date'),
                netchange = Sum('amount'),
                buystock = Sum(Case(When(type="Stockbuy", then=F('amount')))),
                sellstock = Sum(Case(When(type="Stocksell", then=F('amount')))),
                buy = Sum(Case(When(type="Buy", then=F('amount')))),
                sell = Sum(Case(When(type="Sell", then=F('amount')))),
                interest = Sum(Case(When(type="Interest", then=F('amount')))),
                dividend = Sum(Case(When(type="Dividend", then=F('amount')))),
                deduction = Sum(Case(When(type="Deduction", then=F('amount')))),
                deposit = Sum(Case(When(type="Deposit", then=F('amount')))),
                withdrawal = Sum(Case(When(type="Withdrawal", then=F('amount')))),
            ).order_by('-min_date')

            for interval_data in transactions_by_currency:
                if interval == 'Weekly':
                    interval_data['start_date'] = interval_data['min_date'] - timedelta(days=interval_data['min_date'].weekday())
                    interval_data['end_date'] = interval_data['max_date'] + timedelta(days=6 - interval_data['max_date'].weekday())
                elif interval == 'Monthly':
                    interval_data['start_date'] = interval_data['min_date'].replace(day=1)
                    next_month = interval_data['min_date'].replace(day=28) + timedelta(days=4)
                    interval_data['end_date'] = next_month - timedelta(days=next_month.day)
                else:
                    interval_data['start_date'] = interval_data['min_date'].replace(month=1, day=1)
                    interval_data['end_date'] = interval_data['max_date'].replace(month=12, day=31)
            
            transactions_by_currency_paginator = Paginator(transactions_by_currency, 5)
            transactions_by_currency_page_number = request.GET.get('page')
            transactions_by_currency_page_obj = transactions_by_currency_paginator.get_page(transactions_by_currency_page_number)
            transactions_by_currency_dictionary[currency] = transactions_by_currency_page_obj
            
            # transactions_by_currency_dictionary[currency] = transactions_by_currency

    # Get the search parameters in the URL
    search_parameters = request.GET.copy()
    search_parameters_clean = search_parameters.pop('page', True) and search_parameters.urlencode()

    context = {
        'performancefilterform': performancefilterform,
        'transactions_by_currency_dictionary': transactions_by_currency_dictionary,
        'transactions_by_currency_page_obj': transactions_by_currency_page_obj,
        'search_parameters_clean': search_parameters_clean,
        'no_stock_message': no_stock_message,
        'no_fiat_message': no_fiat_message,
        'no_crypto_message': no_crypto_message,
        'asset': asset,
    }
    return render(request, "stockcalculator/performance.html", context)



@login_required
def transaction(request):
    
    # Get the transaction history of the user
    user = request.user
    message = ""

    transactions = Transaction.objects.filter(user=user).order_by('-date')

    if transactions.count() == 0:
        message = "No transaction is added...yet!"

    # Implement the transaction search form
    searchform = TransactionSearch(request.GET or None)
    if searchform.is_valid():
        transactions = searchform.search(user)

        if not transactions:
            message = "No matched transactions."
        

    # Transaction pagination
    transactions_paginator = Paginator(transactions, 10)
    transactions_page_number = request.GET.get('page')
    transactions_page_obj = transactions_paginator.get_page(transactions_page_number)

    # Get the search parameters in the URL
    search_parameters = request.GET.copy()
    search_parameters_clean = search_parameters.pop('page', True) and search_parameters.urlencode()


    

    # Implement the transaction create form
    createform = CreateTransaction(request.POST or None)
    if request.method == 'POST':       
        if createform.is_valid():
            
            # Extract the user's input
            asset = request.POST["asset"]
            currency = request.POST["currency"]
            date = request.POST["date"]
            type = request.POST["type"]
            symbol = request.POST["symbol"].upper()
            buyfiatsymbol = createform.cleaned_data["buyfiatsymbol"].upper()
            sellfiatsymbol = createform.cleaned_data["sellfiatsymbol"].upper()
            buycryptosymbol = request.POST["buycryptosymbol"].upper()
            sellcryptosymbol = request.POST["sellcryptosymbol"].upper()
            quantity = request.POST["quantity"]
            if quantity:
                quantity = Decimal(quantity)
            else:
                quantity = None
            price = request.POST["price"]
            if price:
                price = Decimal(price)
            else:
                price = None
            proceed = request.POST["proceed"]
            if proceed:
                proceed = Decimal(proceed)
            else:
                proceed = None
            fee = request.POST["fee"]
            if fee:
                fee = Decimal(fee)
            else:
                fee = None
            basis = Decimal(request.POST["basis"])
            remark = request.POST["remark"]
            pl = None
            plpercent = None
            related_stockholding_dic = None
            selling_is_valid = False

            # If Asset=Stock, and Type=Deposit/Withdrawal
            if asset=="Stock" and (type=="Deposit" or type=="Withdrawal"):
                messages.error(request, 'Error: Type cannot be Deposit/Withdrawal for Stock')
                return redirect('transaction')

            # Calculate the Profit/Loss if the user sells Stock
            if asset=="Stock" and type=="Sell":
                # Match the sold stock with current holding, order by -date, Sell by First In First Out
                related_current_holding = StockHolding.objects.filter(user=request.user, currency=currency, symbol__iexact=symbol, buydate__lte=date, quantity__gt=0).order_by('buydate')
                related_current_holding_count = 0
                
                # Count the total holdings of that stock
                for holding in related_current_holding:
                    related_current_holding_count = related_current_holding_count + holding.quantity
                #"Related holding count:" + str(related_current_holding_count))

                
                # If user sells a non-existing holding
                if not related_current_holding.exists():
                    # return an alert
                    messages.error(request, 'You cannot sell a stock you do not own on or before the selling date. Make sure you have inserted the correct currency and symbol.')
                    return redirect('transaction')
                # Else if the user sells more than the current holdings
                elif quantity > related_current_holding_count:
                    messages.error(request, 'You cannot sell a stock more than what you own on or before the selling date. Make sure you have inserted the correct currency and symbol.')
                    return redirect('transaction')
                # Else, calculate the PL and update the current holdings
                else:
                    pl = 0
                    cost = 0
                    non_deducted_quantity = quantity

                    # Creating a dictionary to insert in the relatedbuytransaction field
                    related_stockholding_dic = {'transactions': []}
                    
                    for holding in related_current_holding:
                        if non_deducted_quantity > 0:
                            # Get the lesser of the sold quantity and the quantity of each holding 
                            sell_quantity = min(non_deducted_quantity, holding.quantity)
                            
                            # Update the current holding 
                            holding.quantity = holding.quantity - sell_quantity
                            holding.save()

                            # Update the sell_transactions_dic
                            related_stockholding_dic['transactions'].append({'id': holding.id, 'quantity': float(sell_quantity)})
                        
                            # Count the quantity which is not deducted from the current holdings
                            non_deducted_quantity = non_deducted_quantity - sell_quantity
                            # print("Non deducted quantity:" + str(non_deducted_quantity))
                            # print("Related buy transaction:" + str(holding.buytransaction.id))
                            
                            # Calculate PL
                            pl = pl + ((price - holding.price) * sell_quantity)
                            cost = cost + (holding.price * sell_quantity)
                            
                    plpercent = pl/cost
                    
                    # An indicator to show that this sell transaction is valid
                    selling_is_valid = True
                        
            
            # Create a new transaction
            newtransaction = Transaction()
            newtransaction.user = request.user
            newtransaction.asset = asset
            newtransaction.currency = currency
            newtransaction.date = date
            newtransaction.type = type
            
            # Join the buy and sold currency if user bought a currency
            if asset=="FiatMoney" and type=="Buy":
                newtransaction.symbol = buyfiatsymbol + '.' + sellfiatsymbol
            elif asset=="FiatMoney" and type != "Buy":
                newtransaction.symbol = currency
            elif asset=="Crypto" and type=="Buy":
                newtransaction.symbol = buycryptosymbol + '.' + sellcryptosymbol
            else:
                newtransaction.symbol = symbol
            
            newtransaction.quantity = quantity
            newtransaction.price = price
            
            # Adjust the proceed to negative or positive
            if proceed == None:
                newtransaction.proceed = proceed
            else:
                if asset=="Stock" and type=="Buy":
                    newtransaction.proceed = -abs(proceed)
                elif asset=="Stock" and type=="Sell":
                    newtransaction.proceed = abs(proceed)
                elif type=="Deposit":
                    newtransaction.proceed = abs(proceed)
                elif type=="Withdrawal":
                    newtransaction.proceed = -abs(proceed)
                elif type=="Deduction":
                    newtransaction.proceed = -abs(proceed)
                elif (asset=="FiatMoney" or asset=="Crypto") and type=="Buy":
                    newtransaction.proceed = -abs(proceed)
                else:
                    newtransaction.proceed = proceed
                
            
            # Fee is always negative
            if fee == None or fee < 0:
                newtransaction.fee = fee
            else:
                newtransaction.fee = fee * -1

            # Adjust the basis to negative or positive
            if asset=="Stock" and type=="Buy":
                newtransaction.basis = -abs(basis)
            elif asset=="Stock" and type=="Sell":
                newtransaction.basis = abs(basis)
            elif type=="Deposit":
                newtransaction.basis = abs(basis)
            elif type=="Withdrawal":
                newtransaction.basis = -abs(basis)
            elif type=="Deduction":
                newtransaction.basis = -abs(basis)
            elif (asset=="FiatMoney" or asset=="Crypto") and type=="Buy":
                newtransaction.basis = -abs(basis)
            else:
                newtransaction.basis = basis
                

            newtransaction.remark = remark

            newtransaction.pl = pl
            newtransaction.plpercent = plpercent

            newtransaction.relatedstockholdings = related_stockholding_dic

            # Save the transaction
            newtransaction.save()

            # If the sell stock transaction is valid
            if selling_is_valid:
                
                # Update the selltransaction field in Stockholding objects and the buytransaction field in the sell transaction
                sold_stockholding = newtransaction.relatedstockholdings['transactions']
                sold_stockholding_id = []
                
                for holding in sold_stockholding:
                    sold_stockholding_id.append(holding['id'])

                for id in sold_stockholding_id:
                    
                    # Update the selltransaction field in Stockholding objects
                    to_update_holding = StockHolding.objects.get(id=id)
                    to_update_holding.selltransaction.add(newtransaction)
                    to_update_holding.save()

                    # Update the buytransaction field in the sell transaction
                    newtransaction.relatedbuytransaction.add(to_update_holding.buytransaction)
                
                newtransaction.save()
                  

            # If the user buy a stock, add the stock to current holding
            if asset == "Stock" and type == "Buy":
                newholding = StockHolding()
                newholding.user = request.user
                newholding.buytransaction = newtransaction
                newholding.buydate = newtransaction.date
                newholding.currency = newtransaction.currency
                newholding.symbol = newtransaction.symbol
                newholding.original_quantity = newtransaction.quantity
                newholding.quantity = newtransaction.quantity
                newholding.price = newtransaction.price

                # Save the new holding
                newholding.save()

            # Create an object for FiatHolding or CryptoHolding
            # If the asset is not Crypto or buying fiat money
            if not (asset == "Crypto" or (asset == "FiatMoney" and type == "Buy")):
                newfiatholding = FiatHolding()
                newfiatholding.user = request.user
                newfiatholding.relatedtransaction = newtransaction
                newfiatholding.date = newtransaction.date
                newfiatholding.currency = newtransaction.currency
                newfiatholding.amount = newtransaction.basis
                if asset == "Stock" and type == "Buy":
                    newfiatholding.type = 'Stockbuy'
                elif asset == "Stock" and type == "Sell":
                    newfiatholding.type = 'Stocksell'
                else:
                    newfiatholding.type = newtransaction.type

                newfiatholding.save()
            
            # Else if buying fiat money
            elif asset == "FiatMoney" and type == "Buy":
                newfiatholding_buy = FiatHolding()
                newfiatholding_buy.user = request.user
                newfiatholding_buy.relatedtransaction = newtransaction
                newfiatholding_buy.date = newtransaction.date
                newfiatholding_buy.currency = buyfiatsymbol
                newfiatholding_buy.amount = newtransaction.quantity
                newfiatholding_buy.type = 'Buy'
                newfiatholding_buy.save()

                newfiatholding_sell = FiatHolding()
                newfiatholding_sell.user = request.user
                newfiatholding_sell.relatedtransaction = newtransaction
                newfiatholding_sell.date = newtransaction.date
                newfiatholding_sell.currency = sellfiatsymbol
                newfiatholding_sell.amount = newtransaction.basis
                newfiatholding_sell.type = 'Sell'
                newfiatholding_sell.save()
            
            # Else if buying cryptocurrency
            elif asset == "Crypto" and type == "Buy":
                newcryptoholding_buy = CryptoHolding()
                newcryptoholding_buy.user = request.user
                newcryptoholding_buy.relatedtransaction = newtransaction
                newcryptoholding_buy.date = newtransaction.date
                newcryptoholding_buy.currency = buycryptosymbol
                newcryptoholding_buy.amount = newtransaction.quantity
                newcryptoholding_buy.type = 'Buy'
                newcryptoholding_buy.save()

                newcryptoholding_sell = CryptoHolding()
                newcryptoholding_sell.user = request.user
                newcryptoholding_sell.relatedtransaction = newtransaction
                newcryptoholding_sell.date = newtransaction.date
                newcryptoholding_sell.currency = sellcryptosymbol
                newcryptoholding_sell.amount = newtransaction.basis
                newcryptoholding_sell.type = 'Sell'
                newcryptoholding_sell.save()
            
            # Else, asset is Crypto but type is not Buy
            else:
                newcryptoholding = CryptoHolding()
                newcryptoholding.user = request.user
                newcryptoholding.relatedtransaction = newtransaction
                newcryptoholding.date = newtransaction.date
                newcryptoholding.currency = newtransaction.symbol
                newcryptoholding.amount = newtransaction.basis
                newcryptoholding.type = newtransaction.type
                newcryptoholding.save()
            
            return redirect('transaction')
        else:
            # Handle invalid form data
            errors = createform.errors.as_json()
            return JsonResponse({'error': errors}, status=400)
    
    # Edit transaction form
    edit_transaction_form = EditTransaction(request.POST or None)    
        
    context = {
        'transactions': transactions,
        'transactions_page_obj': transactions_page_obj,
        'search_parameters_clean': search_parameters_clean,
        'searchform': searchform,
        'createform': createform,
        'edit_transaction_form': edit_transaction_form,
        'message': message,
    }
    return render(request, "stockcalculator/transaction.html", context)


@login_required
def edit_transaction(request, transaction_id):
    # Query for requested transaction
    try:
        transaction = Transaction.objects.get(pk=transaction_id)
    except Transaction.DoesNotExist:
        return JsonResponse({"error": "Transaction not found."}, status=404)
    
    if transaction.user.id != request.user.id:
        return JsonResponse({"error": "Not allowed to update this transaction."}, status=403)
    
    else:
        # Return transaction details
        if request.method == "GET":
            return JsonResponse({
                "transaction": transaction.serialize(),
                "user_id": transaction.user.id,
                "logged_in_user_id": request.user.id,
            })

        elif request.method == 'PUT':            
            data = json.loads(request.body)
            transaction.remark = data["remark"]
            transaction.save()
            return JsonResponse({'success': True})
        else:
            # Request must be via GET or PUT
            return JsonResponse({"error": "GET or PUT request required."}, status=403)


@login_required
def delete_transaction(request, transaction_id):
    
    # Query the transaction
    try:
        transaction = Transaction.objects.get(pk=transaction_id)
    except Transaction.DoesNotExist:
        return JsonResponse({"error": "Transaction not found."}, status=404)
    
    # User is not allowed to delete others' transactions
    if transaction.user.id != request.user.id:
        return JsonResponse({"error": "Not allowed to delete this transaction."}, status=403)
    
    # Check if the transaction is deleted already
    elif transaction.deleted_at != None:
        return JsonResponse({"error": "The transaction has been deleted already."}, status=403)

    else: 
        # If asset = Crypto
        if transaction.asset == "Crypto":
            
            # Flag the related CryptoHolding as deleted
            related_cryptoholding = CryptoHolding.objects.filter(relatedtransaction = transaction, include_deleted=True)
            # print(related_cryptoholding)

            for holding in related_cryptoholding:
                
                # Check if the holding is deleted already
                if holding.deleted_at != None:
                    return JsonResponse({"error": "The related crypto holding has been deleted already."}, status=403)
                else:
                    # Flag the holding as deleted
                    holding.deleted_at = timezone.now()
                    holding.save()


        # Else, asset = Stock or FiatMoney
        else:

            # If transaction is Buying Stock
            if transaction.asset == "Stock" and transaction.type == "Buy":
                #  Check if the stock is sold partially or completely
                related_stockholding = StockHolding.objects.get(buytransaction = transaction)

                # If the buy_stock transaction is sold, request the user to delete the sell_stock transaction first
                if related_stockholding.selltransaction.exists():
                    return JsonResponse({"error": "This stock is sold already. Please delete all related sell transactions first."}) 
                
                # Check if the holding is deleted already
                elif related_stockholding.deleted_at != None:
                    return JsonResponse({"error": "The related stock holding has been deleted already."}, status=403)
                
                else:
                    # Get the related StockHolding object and mark deleted
                    related_stockholding.deleted_at = timezone.now()
                    related_stockholding.save()
        
            # Elif transaction is Selling Stock
            elif transaction.asset == "Stock" and transaction.type == "Sell":

                # Query the sold StockHolding objects
                related_stockholding = transaction.relatedstockholdings['transactions']

                for holding in related_stockholding:
                    holding_id = holding['id']
                    holding_sold_quantity = holding['quantity']
                    
                    holding_obj = StockHolding.objects.get(id=holding_id)

                    # Add the quantity back to each related StockHolding object 
                    holding_obj.quantity = holding_obj.quantity + Decimal(holding_sold_quantity)

                    # Check if the updated quantity is more than the original quantity
                    if holding_obj.quantity > holding_obj.original_quantity:
                        return JsonResponse({"error": "The updated stock holding quantity is more than the original quantity."}, status=403)

                    else:
                    # Remove the sell transaction from the selltransaction field
                        holding_obj.selltransaction.remove(transaction)
                        holding_obj.save()

            # Flag related FiatHolding as deleted for all Stock or FiatMoney transaction
            related_fiatholding = FiatHolding.objects.filter(relatedtransaction = transaction, include_deleted=True)

            for holding in related_fiatholding:

                # Check if the holding is deleted already
                if holding.deleted_at != None:
                    return JsonResponse({"error": "The related fiat holding has been deleted already."}, status=403)
                else:
                    holding.deleted_at = timezone.now()
                    holding.save()
        
        # Flag the transaction as deleted for transactions of any asset
        transaction.deleted_at = timezone.now()
        transaction.save()

        return JsonResponse({'success': True})

"""
@login_required
def createtransaction(request):
    if request.method == 'POST':
        
        newtransaction = Transaction()
        newtransaction.user = request.user
        newtransaction.asset = request.POST["asset"]
        newtransaction.currency = request.POST["currency"]
        newtransaction.date = request.POST["date"]
        newtransaction.type = request.POST["type"]
        if request.POST["symbol"]:
            newtransaction.symbol = request.POST["symbol"]
        elif request.POST["currencytradingsymbol_0"] and request.POST["currencytradingsymbol_0"]:
            newtransaction.symbol = request.POST["currencytradingsymbol_0"] + '.' + request.POST["currencytradingsymbol_1"]
        else:
            newtransaction.symbol = request.POST["cryptotradingsymbol_0"] + '.' + request.POST["cryptotradingsymbol_1"]
        newtransaction.quantity = request.POST["quantity"]
        newtransaction.price = request.POST["price"]
        newtransaction.proceed = request.POST["proceed"]
        newtransaction.fee = request.POST["fee"]
        newtransaction.basis = request.POST["basis"]
        newtransaction.remark = request.POST["remark"]
        
        newtransaction.save()

        return HttpResponseRedirect('transaction')
        form = CreateTransaction(request.POST)
        
        asset = request.POST["asset"]
        currency = request.POST["currency"]
        date = request.POST["date"]
        type = request.POST["type"]
        symbol = request.POST["symbol"]
        buyfiatsymbol = request.POST.get("buyfiatsymbol")
        sellfiatsymbol = request.POST.get("sellfiatsymbol")
        buycryptosymbol = request.POST["buycryptosymbol"]
        sellcryptosymbol = request.POST["sellcryptosymbol"]
        quantity = request.POST["quantity"]
        price = request.POST["price"]
        proceed = request.POST["proceed"]
        fee = request.POST["fee"]
        basis = request.POST["basis"]
        remark = request.POST["remark"]
        
        return JsonResponse({
            'asset': asset,
            'currency': currency,
            'date': date,
            'type': type,
            'symbol': symbol,
            'buyfiatsymbol': buyfiatsymbol,
            'sellfiatsymbol': sellfiatsymbol,
            'buycryptosymbol': buycryptosymbol,
            'sellcryptosymbol': sellcryptosymbol,
            'quantity': quantity,
            'price': price,
            'proceed': proceed,
            'fee': fee,
            'basis': basis,
            'remark': remark,
            }, 
            status=200)"""
            


"""
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "stock/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "stock/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "stock/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "stock/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "stock/register.html")

"""
