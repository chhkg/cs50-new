import {
    expand_transaction_search_form, 
    hide_transaction_search_form, 
    clear_filter,
    expand_transaction_create_form, 
    hide_transaction_create_form,
    create_transaction_dynamic_field,
    edit_transaction,
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
    
    // By default, hide the alerts
    $("#success-alert").hide();
    $("#fail-alert").hide();

    // Edit Transaction
    const transaction_edit_button = document.getElementsByClassName('transaction-edit-button')
    for (var i = 0; i < transaction_edit_button.length; i++) {
        const transaction_edit_button_parent = transaction_edit_button[i].closest('tr');
        const edit_transaction_id = transaction_edit_button_parent.querySelector('.transaction-id').innerHTML
        transaction_edit_button[i].addEventListener('click', () => {
            edit_transaction(transaction_edit_button_parent, edit_transaction_id);
        });

        //$('#edit-transaction-modal').on('hidden.bs.modal', function(event) {
        //    transaction_edit_button[i].removeEventListener('click', () => {
        //        edit_transaction(transaction_edit_button_parent, edit_transaction_id);
        //    });
        //})
    }

    

    // Delete Transaction
    $('#delete-transaction-confirmation-modal').on('show.bs.modal', function (event) {
        const delete_button = $(event.relatedTarget) // Button that triggered the modal
        const delete_button_closest_tr = delete_button.closest('tr')
        const delete_transaction_id = delete_button_closest_tr.find('.transaction-id').text()
        const close_modal_button = document.querySelector('#close-delete-modal');
        console.log(delete_transaction_id)

        const confirm_delete_button = document.querySelector('#confirm-delete-button')

        confirm_delete_button.addEventListener('click', () => {
            fetch('/deletetransaction/' + delete_transaction_id)
            .then(response => response.json())
            .then(data => {
                if (data.success) {

                    // Close the modal after updating the remark
                    close_modal_button.click()
    
                    // Show a successful update alert
                    $('#success-alert').html("Transaction deleted successfully")
                    $('#success-alert').fadeTo(4000, 500).slideUp(500, function() {
                        $("#success-alert").slideUp(500);
                        });
    
                        delete_button_closest_tr.fadeTo(1300, 0, function(){
                        $(this).remove();
                    })
                } else if (data.error) {
                    close_modal_button.click()
                    $('#fail-alert').html(data.error)
                    $('#fail-alert').fadeTo(4000, 500).slideUp(500, function() {
                        $("#fail-alert").slideUp(500);
                        });
                } else {
                    console.error(data)
                }
            })
            
            .catch((error) => console.log(error));
        } )

        //var delete_transaction_id = delete_button.data('transactionid') // Extract info from data-* attributes
        // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
        // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
        //var modal = $(this)
        //modal.find('#delete_transaction_id').val(delete_transaction_id)
      })
});