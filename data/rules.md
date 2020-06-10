>> greet/bye path
    - ...
* greet
    - utter_greet

>> say goodbye
    - ...
* goodbye
    - utter_goodbye

>> thank you 
    - ...
* thankyou
    - utter_noworries

>> check account balance 
    - ...
* check_balance
    - action_account_balance
    - ...

>> transfer charge 
    - ...
* ask_transfer_charge
    - utter_transfer_charge
    - ...

>> pay credit card
    - ...
* pay_cc
    - cc_payment_form
    - form{"name": "cc_payment_form"}
    - ...

>> pay credit card submit
    - form{"name": "cc_payment_form"}
    - ...
    - cc_payment_form
    - form{"name": "null"}
    - slot{"requested_slot": null}
    - action_submit_cc_payment
    - ...

>> transfer money
    - ...
* transfer_money
    - transfer_form
    - form{"name": "transfer_form"}
    - ...

>> transfer money submit
    - form{"name": "transfer_form"}
    - ...
    - transfer_form
    - form{"name": "null"}
    - slot{"requested_slot": null}
    - action_submit_transfer
    - ...

>> search transactions
    - ...
* search_transactions
    - transact_search_form
    - form{"name": "transact_search_form"}
    - ...

>> search transactions
    - ...
* check_earnings
    - transact_search_form
    - form{"name": "transact_search_form"}
    - ...


>> search transactions submit
    - form{"name": "transact_search_form"}
    - ...
    - transact_search_form
    - form{"name": "null"}
    - slot{"requested_slot": null}
    - action_submit_transact_search
    - ...