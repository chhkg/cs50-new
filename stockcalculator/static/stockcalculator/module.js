/* transaction.html Related */

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

export function expand_transaction_search_form() {
    //document.querySelector('#search-form-expand-button').toggleAttribute("disabled");
    const searchformdiv = document.querySelector('#transaction-search-form-div');
    if (searchformdiv.style.display === 'none') {
        searchformdiv.style.display = 'block';
    } else {
        searchformdiv.style.display = 'none';
    }
    document.querySelector('#transaction-create-form-div').style.display = 'none';
}

export function hide_transaction_search_form() {
    document.querySelector('#transaction-search-form-div').style.display = 'none';
    //document.querySelector('#search-form-expand-button').toggleAttribute("disabled"); 
}

export function clear_filter() {
    $('#transaction-search-form').trigger('reset');
};

export function expand_transaction_create_form() {
    //document.querySelector('#create-form-expand-button').toggleAttribute("disabled");
    const createformdiv = document.querySelector('#transaction-create-form-div');
    if (createformdiv.style.display === 'none') {
        createformdiv.style.display = 'block';
    } else {
        createformdiv.style.display = 'none';
    }
    document.querySelector('#transaction-search-form-div').style.display = 'none';
}

export function hide_transaction_create_form() {
    document.querySelector('#transaction-create-form-div').style.display = 'none';
    //document.querySelector('#create-form-expand-button').toggleAttribute("disabled"); 
}

export function create_transaction_dynamic_field() {
    // Hide the currency field by default
    $('#buyfiatsymbol-create').closest('.form-group').hide();
    $('#sellfiatsymbol-create').closest('.form-group').hide();
    $('#buycryptosymbol-create').closest('.form-group').hide();
    $('#sellcryptosymbol-create').closest('.form-group').hide();
    
    $('#asset-create, #type-create').change(function() {
        var asset = $('#asset-create').val();
        var type = $('#type-create').val();
        
        if (asset == 'Stock' && (type == 'Buy' || type=="Sell")) {
            // If Asset = Stock and type = Buy, adjust the form
            $('#symbol-create').closest('.form-group').show();
            $('#currency-create').closest('.form-group').show();
            $('#buyfiatsymbol-create').closest('.form-group').hide();
            $('#sellfiatsymbol-create').closest('.form-group').hide();
            $('#buycryptosymbol-create').closest('.form-group').hide();
            $('#sellcryptosymbol-create').closest('.form-group').hide();
            $('#type-create option[value="Sell"]').show();
            $('#type-create option[value="Deposit"]').hide();
            $('#type-create option[value="Withdrawal"]').hide();
            
            $('#symbol-create').prop('required', true);
            $('#currency-create').prop('required', true);
            $('#buyfiatsymbol-create').prop('required', false);
            $('#sellfiatsymbol-create').prop('required', false);
            $('#buycryptosymbol-create').prop('required', false);
            $('#sellcryptosymbol-create').prop('required', false);
            $('#quantity-create').prop('required', true);
            $('#price-create').prop('required', true);

            $('label[for="symbol-create"]').text('Symbol*')
            $('label[for="currency-create"]').text('Currency*')
            $('label[for="buyfiatsymbol-create"]').text('Buy Currency')
            $('label[for="sellfiatsymbol-create"]').text('Sell Currency')
            $('label[for="buycryptosymbol-create"]').text('Buy Crypto Symbol')
            $('label[for="sellcryptosymbol-create"]').text('Sell Crypto Symbol')
            $('label[for="quantity-create"]').text('Quantity*')
            $('label[for="price-create"]').text('Price*')

        } else if(asset == 'Stock' && type != 'Buy') {
            // If Asset = Stock and type != Buy, adjust the form
            $('#symbol-create').closest('.form-group').show();
            $('#currency-create').closest('.form-group').show();
            $('#buyfiatsymbol-create').closest('.form-group').hide();
            $('#sellfiatsymbol-create').closest('.form-group').hide();
            $('#buycryptosymbol-create').closest('.form-group').hide();
            $('#sellcryptosymbol-create').closest('.form-group').hide();
            $('#type-create option[value="Sell"]').show();
            $('#type-create option[value="Deposit"]').hide();
            $('#type-create option[value="Withdrawal"]').hide();

            $('#symbol-create').prop('required', true);
            $('#currency-create').prop('required', true);
            $('#buyfiatsymbol-create').prop('required', false);
            $('#sellfiatsymbol-create').prop('required', false);
            $('#buycryptosymbol-create').prop('required', false);
            $('#sellcryptosymbol-create').prop('required', false);
            $('#quantity-create').prop('required', false);
            $('#price-create').prop('required', false);

            $('label[for="symbol-create"]').text('Symbol*')
            $('label[for="currency-create"]').text('Currency*')
            $('label[for="buyfiatsymbol-create"]').text('Buy Currency')
            $('label[for="sellfiatsymbol-create"]').text('Sell Currency')
            $('label[for="buycryptosymbol-create"]').text('Buy Crypto Symbol')
            $('label[for="sellcryptosymbol-create"]').text('Sell Crypto Symbol')
            $('label[for="quantity-create"]').text('Quantity')
            $('label[for="price-create"]').text('Price')

        } else if (asset == 'FiatMoney' && type == 'Buy') {
            // If Asset = Fiat Money and Type = Buy, adjust the form
            $('#symbol-create').closest('.form-group').hide();
            $('#currency-create').closest('.form-group').hide();
            $('#buyfiatsymbol-create').closest('.form-group').show();
            $('#sellfiatsymbol-create').closest('.form-group').show();
            $('#buycryptosymbol-create').closest('.form-group').hide();
            $('#sellcryptosymbol-create').closest('.form-group').hide();
            $('#type-create option[value="Sell"]').hide();
            $('#type-create option[value="Deposit"]').show();
            $('#type-create option[value="Withdrawal"]').show();

            $('#symbol-create').prop('required', false);
            $('#currency-create').prop('required', false);
            $('#buyfiatsymbol-create').prop('required', true);
            $('#sellfiatsymbol-create').prop('required', true);
            $('#buycryptosymbol-create').prop('required', false);
            $('#sellcryptosymbol-create').prop('required', false);
            $('#quantity-create').prop('required', true);
            $('#price-create').prop('required', false);

            $('label[for="symbol-create"]').text('Symbol')
            $('label[for="currency-create"]').text('Currency')
            $('label[for="buyfiatsymbol-create"]').text('Buy Currency*')
            $('label[for="sellfiatsymbol-create"]').text('Sell Currency*')
            $('label[for="buycryptosymbol-create"]').text('Buy Crypto Symbol')
            $('label[for="sellcryptosymbol-create"]').text('Sell Crypto Symbol')
            $('label[for="quantity-create"]').text('Quantity*')
            $('label[for="price-create"]').text('Price')

        } else if (asset == 'Crypto' && type == 'Buy') {
            // If Asset = Crypto and Type = Buy, adjust the form
            $('#symbol-create').closest('.form-group').hide();
            $('#currency-create').closest('.form-group').hide();
            $('#buyfiatsymbol-create').closest('.form-group').hide();
            $('#sellfiatsymbol-create').closest('.form-group').hide();
            $('#buycryptosymbol-create').closest('.form-group').show();
            $('#sellcryptosymbol-create').closest('.form-group').show();
            $('#type-create option[value="Sell"]').hide();
            $('#type-create option[value="Deposit"]').show();
            $('#type-create option[value="Withdrawal"]').show();

            $('#symbol-create').prop('required', false);
            $('#currency-create').prop('required', false);
            $('#buyfiatsymbol-create').prop('required', false);
            $('#sellfiatsymbol-create').prop('required', false);
            $('#buycryptosymbol-create').prop('required', true);
            $('#sellcryptosymbol-create').prop('required', true);
            $('#quantity-create').prop('required', true);
            $('#price-create').prop('required', false);

            $('label[for="symbol-create"]').text('Symbol')
            $('label[for="currency-create"]').text('Currency')
            $('label[for="buyfiatsymbol-create"]').text('Buy Currency')
            $('label[for="sellfiatsymbol-create"]').text('Sell Currency')
            $('label[for="buycryptosymbol-create"]').text('Buy Crypto Symbol*')
            $('label[for="sellcryptosymbol-create"]').text('Sell Crypto Symbol*')
            $('label[for="quantity-create"]').text('Quantity*')
            $('label[for="price-create"]').text('Price')

        } else if (asset == 'Crypto' && type != 'Buy') {
            // If Asset = Crypto and type != Buy, adjust the form
            $('#symbol-create').closest('.form-group').show();
            $('#currency-create').closest('.form-group').hide();
            $('#buyfiatsymbol-create').closest('.form-group').hide();
            $('#sellfiatsymbol-create').closest('.form-group').hide();
            $('#buycryptosymbol-create').closest('.form-group').hide();
            $('#sellcryptosymbol-create').closest('.form-group').hide();
            $('#type-create option[value="Sell"]').hide();
            $('#type-create option[value="Deposit"]').show();
            $('#type-create option[value="Withdrawal"]').show();

            $('#symbol-create').prop('required', true);
            $('#currency-create').prop('required', false);
            $('#buyfiatsymbol-create').prop('required', false);
            $('#sellfiatsymbol-create').prop('required', false);
            $('#buycryptosymbol-create').prop('required', false);
            $('#sellcryptosymbol-create').prop('required', false);
            $('#quantity-create').prop('required', false);
            $('#price-create').prop('required', false);

            $('label[for="symbol-create"]').text('Symbol*')
            $('label[for="currency-create"]').text('Currency')
            $('label[for="buyfiatsymbol-create"]').text('Buy Currency')
            $('label[for="sellfiatsymbol-create"]').text('Sell Currency')
            $('label[for="buycryptosymbol-create"]').text('Buy Crypto Symbol')
            $('label[for="sellcryptosymbol-create"]').text('Sell Crypto Symbol')
            $('label[for="quantity-create"]').text('Quantity')
            $('label[for="price-create"]').text('Price')

        } else {
            $('#symbol-create').closest('.form-group').hide();
            $('#currency-create').closest('.form-group').show();
            $('#buyfiatsymbol-create').closest('.form-group').hide();
            $('#sellfiatsymbol-create').closest('.form-group').hide();
            $('#buycryptosymbol-create').closest('.form-group').hide();
            $('#sellcryptosymbol-create').closest('.form-group').hide();
            $('#type-create option[value="Sell"]').hide();
            $('#type-create option[value="Deposit"]').show();
            $('#type-create option[value="Withdrawal"]').show();

            $('#symbol-create').prop('required', false);
            $('#currency-create').prop('required', true);
            $('#buyfiatsymbol-create').prop('required', false);
            $('#sellfiatsymbol-create').prop('required', false);
            $('#buycryptosymbol-create').prop('required', false);
            $('#sellcryptosymbol-create').prop('required', false);
            $('#quantity-create').prop('required', false);
            $('#price-create').prop('required', false);

            $('label[for="symbol-create"]').text('Symbol')
            $('label[for="currency-create"]').text('Currency*')
            $('label[for="buyfiatsymbol-create"]').text('Buy Currency')
            $('label[for="sellfiatsymbol-create"]').text('Sell Currency')
            $('label[for="buycryptosymbol-create"]').text('Buy Crypto Symbol')
            $('label[for="sellcryptosymbol-create"]').text('Sell Crypto Symbol')
            $('label[for="quantity-create"]').text('Quantity')
            $('label[for="price-create"]').text('Price')
        }
    });
}

export function clear_search() {
    // Clear the search form fields
    const asset = document.getElementById('asset-search');
    const type = document.getElementById('type-search');
    const currency = document.getElementById('currency-search');
    const startdate = document.getElementById('startdate-search');
    const enddate = document.getElementById('enddate-search');
    const symbol = document.getElementById('symbol-search');
    const remark = document.getElementById('remark-search');

    asset.value = '';
    type.value = '';
    currency.value = '';
    startdate.value = '';
    enddate.value = '';
    symbol.value = '';
    remark.value = '';

    location.reload()
}

export function edit_transaction(transaction_edit_button_parent, transaction_id) {
    const remark_edit_input = document.querySelector('#remark-edit');
    const close_modal_button = document.querySelector('#close-edit-modal');
    const remark_content = transaction_edit_button_parent.querySelector('.transaction-remark').innerHTML

    // Insert the original remark content to the modal form
    remark_edit_input.value = remark_content;
    
    // Update the transaction after clicking save button
    $('#save-edit-change-button').off().on('click', () => {
        fetch('/edittransaction/' + transaction_id)
        .then(response => response.json())
        .then(data => {
            // User is allowed to update their own transaction only
            if(data.user_id == data.logged_in_user_id){                
                // Update the transaction via PUT request
                fetch('/edittransaction/' + transaction_id, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        remark: remark_edit_input.value
                    })
                })
                .then(response => {
                    // Close the modal after updating the remark
                    close_modal_button.click()
                    transaction_edit_button_parent.querySelector('.transaction-remark').innerHTML = remark_edit_input.value

                    // Show a successful update alert
                    $('#success-alert').html("Transaction updated successfully")
                    $('#success-alert').fadeTo(4000, 500).slideUp(500, function() {
                        $("#success-alert").slideUp(500);
                      });
                })
                .catch((error) => console.log(error));
            } else {
                // Throw an error if a user tried to update another user's transaction
                alert('You are not allowed to edit this transaction!')
            }
        })
        .catch((error) => console.log(error));
    })
}