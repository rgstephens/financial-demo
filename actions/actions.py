from typing import Dict, Text, Any, List, Union, Optional
import logging
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction, REQUESTED_SLOT
from rasa_sdk.events import SlotSet, EventType
from actions.parsing import (
    parse_duckling_time_as_interval,
    parse_duckling_time,
    get_entity_details,
    parse_duckling_currency,
)

logger = logging.getLogger(__name__)


from typing import Dict, Text, List

from rasa_sdk import Tracker
from rasa_sdk.events import EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Action
from rasa_sdk.events import SlotSet


def payment_amount_db() -> Dict[Text, Any]:
    """Database of supported payment amounts"""

    return {
        "minimum balance": 85,
        "current balance": 550,
    }

def credit_card_db() -> List[Text]:
    """Database of supported credit cards"""

    return [
        "iron bank",
        "credit all",
        "gringots",
        "justice bank",
    ]

def vendor_name_db() -> List[Text]:
    """Database of supported vendors customers might buy from"""

    return [
        "amazon",
        "target",
        "starbucks",
    ]

def transactions_db() -> Dict[Text, Any]:
    """Database of transactions"""

    return {
        "spend": {
            "starbucks": [{"amount": 5.50}, {"amount": 9.10}],
            "amazon": [
                {"amount": 35.95},
                {"amount": 9.35},
                {"amount": 49.50},
            ],
            "target": [{"amount": 124.95}],
        },
        "deposit": {
            "employer": [{"amount": 1250.00}],
            "interest": [{"amount": 50.50}],
        },
    }

class ValidatePaymentAmount(Action):
    def name(self) -> text:
        return "validate_payment_amount"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Any]:
        """Validate payment amount value."""

        value = tracker.get_slot("payment_amount")

        try:
            entity = get_entity_details(
                tracker, "amount-of-money"
            ) or get_entity_details(tracker, "number")
            amount_currency = parse_duckling_currency(entity)
            if not amount_currency:
                raise (TypeError)
            return [SlotSet(payment_amount, amount_currency)]

        except (TypeError, AttributeError):
            pass
        if value and value.lower() in payment_amount_db():
            key = value.lower()
            amount = payment_amount_db().get(key)
            amount_type = f" (your {key})"
            return [
                        SlotSet("payment_amount", f"{amount:.2f}"),
                        SlotSet("payment_amount_type", amount_type),
                        SlotSet("currency", "$")
                ]

        else:
            dispatcher.utter_message(template="utter_no_payment_amount")
            return [SlotSet("payment_amount", None)]

class ValidateCreditCard(Action):
    def name(self) -> text:
        return "validate_credit_card"

    def validate_credit_card(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate credit_card value."""

        value = tracker.get_slot("credit_card")

        if value and value.lower() in credit_card_db():
            return [SlotSet("credit_card", value)]
        else:
            dispatcher.utter_message(template="utter_no_creditcard")
            return [SlotSet("credit_card", None)]

class ValidateTime(Action):
    def name(self) -> text:
        return "validate_time"

    def validate_time(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate time value."""
        
        if tracker.active_form == "cc_payment_form":
            timeentity = get_entity_details(tracker, "time")
            parsedtime = parse_duckling_time(timeentity)
            if not parsedtime:
                dispatcher.utter_message(template="utter_no_transactdate")
                return [SlotSet("time", None)]
            return [SlotSet(k, v) for k, v in parsedtime.items()]
        
        if tracker.active_form == "transact_search_form":
            timeentity = get_entity_details(tracker, "time")
            parsedinterval = parse_duckling_time_as_interval(timeentity)
            if not parsedinterval:
                dispatcher.utter_message(template="utter_no_transactdate")
                return [SlotSet("time", None)]
            return [SlotSet(k, v) for k, v in parsedinterval.items()]

class ValidateAmountOfMoney(Action):
    def name(self) -> Text:
        return "validate_amount_of_money"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        value = tracker.get_slot("amount_of_money")
        try:
            entity = get_entity_details(
                tracker, "amount-of-money"
            ) or get_entity_details(tracker, "number")
            amount_currency = parse_duckling_currency(entity)
            if not amount_currency:
                raise (TypeError)
            return [SlotSet(k,v) for k,v in amount_currency.items()]
        except (TypeError, AttributeError):
            dispatcher.utter_message(template="utter_no_payment_amount")
            return [SlotSet("amount_of_money", None)]

class ValidateVendorName(Action):
    def name(self) -> Text:
        return "validate_vendor_name"

    def validate_vendor_name(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate vendor_name value."""

        value = tracker.get_slot("vendor_name")

        if value and value.lower() in vendor_name_db():
            return {"vendor_name": value}
        else:
            dispatcher.utter_message(template="utter_no_vendor_name")
            return {"vendor_name": None}


class ActionSubmitCCPayment(Action):
    def name(self) -> Text:
        return "action_submit_cc_payment"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        if tracker.get_slot("confirm"):
            dispatcher.utter_message(template="utter_cc_pay_scheduled")
        else:
            dispatcher.utter_message(template="utter_cc_pay_cancelled")
        return [
            SlotSet("credit_card", None),
            SlotSet("payment_amount", None),
            SlotSet("confirm", None),
            SlotSet("time", None),
            SlotSet("grain", None),
        ]

class ActionSubmitTransactSearch(Action):
    def name(self) -> Text:
        return "action_submit_transact_search"

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        search_type = tracker.get_slot("search_type")
        transactions_subset = transactions_db().get(search_type, {})
        vendor = tracker.get_slot("vendor_name")

        if vendor:
            transactions = transactions_subset.get(vendor.lower())
            vendor = f" with {vendor}"
        else:
            transactions = [
                v for k in list(transactions_subset.values()) for v in k
            ]
            vendor = ""

        numtransacts = len(transactions)
        total = sum([t.get("amount") for t in transactions])
        slotvars = {
            "total": f"{total:.2f}",
            "numtransacts": numtransacts,
            "start_time": tracker.get_slot("start_time"),
            "end_time": tracker.get_slot("end_time"),
            "grain": tracker.get_slot("grain"),
            "vendor_name": vendor,
        }

        dispatcher.utter_message(
            template=f"utter_searching_{search_type}_transactions", **slotvars
        )
        dispatcher.utter_message(
            template=f"utter_found_{search_type}_transactions", **slotvars
        )

        return [
            SlotSet("time", None),
            SlotSet("start_time", None),
            SlotSet("end_time", None),
            SlotSet("grain", None),
            SlotSet("search_type", None),
        ]


class ActionSubmitTransfer(Action):
    def name(self) -> Text:
        return "action_submit_transfer"

    def submit(self, dispatcher, tracker, domain):
        if tracker.get_slot("confirm"):
            dispatcher.utter_message(template="utter_transfer_complete")
            return [
                SlotSet("PERSON", None),
                SlotSet("amount_of_money", None),
                SlotSet("confirm", None),
                SlotSet(
                    "amount_transferred", tracker.get_slot("amount_of_money")
                ),
            ]
        else:
            dispatcher.utter_message(template="utter_transfer_cancelled")
            return [
                SlotSet("PERSON", None),
                SlotSet("amount_of_money", None),
                SlotSet("confirm", None),
            ]


class ActionAccountBalance(Action):
    def name(self):
        return "action_account_balance"

    def run(self, dispatcher, tracker, domain):
        init_account_balance = float(tracker.get_slot("account_balance"))
        amount = tracker.get_slot("amount_transferred")
        if amount:
            amount = float(tracker.get_slot("amount_transferred"))
            account_balance = init_account_balance - amount
            dispatcher.utter_message(
                template="utter_changed_account_balance",
                init_account_balance=f"{init_account_balance:.2f}",
                account_balance=f"{account_balance:.2f}",
            )
            return [
                SlotSet("payment_amount", None),
                SlotSet("account_balance", account_balance),
                SlotSet("amount_transferred", None),
            ]
        else:
            dispatcher.utter_message(
                template="utter_account_balance",
                init_account_balance=f"{init_account_balance:.2f}",
            )
            return [SlotSet("payment_amount", None)]
