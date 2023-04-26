import {
    expand_transaction_search_form, 
    hide_transaction_search_form, 
    clear_filter,
    expand_transaction_create_form, 
    hide_transaction_create_form,
    create_transaction_dynamic_field,
} from './module.js'

document.addEventListener('DOMContentLoaded', function() {
    const search_form = document.querySelector('#transaction-search-form-div');
    const search_form_expand_button = document.querySelector('#search-form-expand-button');
    const search_cancel_button = document.querySelector('#search_cancel_button');
    const clear_filter_button = document.querySelector('#clear_filter_button');

    const create_form = document.querySelector('#transaction-create-form-div');
    const create_form_expand_button = document.querySelector('#create-form-expand-button');
    const create_cancel_button = document.querySelector('#create_cancel_button');

    // By default, hide the transaction search form
    search_form.style.display = 'none';
    create_form.style.display = 'none';

    // Expand or hide the search form
    search_form_expand_button.addEventListener('click', () => expand_transaction_search_form());
    clear_filter_button.addEventListener('click', () => clear_filter());
    search_cancel_button.addEventListener('click', () => hide_transaction_search_form());
    
    // Expand or hide the create form
    create_form_expand_button.addEventListener('click', () => expand_transaction_create_form());
    create_cancel_button.addEventListener('click', () => hide_transaction_create_form());

    // Control the dynamic fields of the create form
    create_transaction_dynamic_field();
});