from pymongo import MongoClient

MONGODB_URI = 'mongodb+srv://appAdmin:cB45KLzyPdV8NdG3@realto-stage.xg5kl.mongodb.net/'
# MONGODB_URI = os.environ['mongodb+srv://appAdmin:cB45KLzyPdV8NdG3@realto-stage.xg5kl.mongodb.net/redev?retryWrites=true&w=majority&authMechanism=DEFAULT']

db = MongoClient(MONGODB_URI)

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World! from custom action")

        return []



class ActionGetWallet(Action):
    
    def name(self) -> Text:
        return "action_get_wallet_balance"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # function to collect user id credntials
        # user_id = tracker.slot['user_id'] 
        query = {'userId':"617fc06495c1d37b3135e397"} # to be conneced to listener 
        # define mongoDB collection
        wallet = db.redev.crypto_wallets
        # intent = tracker.latest_message.intent['name']
        answer = wallet.find_one(query)

        response = """Your wallet currently holds {}$ in your wallet as of today:""".format(answer['balance'])

        dispatcher.utter_message(response)

class ActionGetAssets(Action):
    
    def name(self) -> Text:
        return "action_get_asset"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="asset [assList] meant to be this")

        return []

class ActionCarousel(Action):
    def name(self) -> Text:
        return "action_carousels"
    
    def run(self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "title": "Carousel 1",
                        "subtitle": "$10",
                        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSqhmyBRCngkU_OKSL6gBQxCSH-cufgmZwb2w&usqp=CAU",
                        "buttons": [ 
                            {
                            "title": "option 1",
                            "payload": "Happy",
                            "type": "postback"
                            },
                            {
                            "title": "option 2",
                            "payload": "sad",
                            "type": "postback"
                            }
                        ]
                    },
                    {
                        "title": "Carousel 2",
                        "subtitle": "$12",
                        "image_url": "https://image.freepik.com/free-vector/city-illustration_23-2147514701.jpg",
                        "buttons": [ 
                            {
                            "title": "Click here",
                            "url": "https://image.freepik.com/free-vector/city-illustration_23-2147514701.jpg",
                            "type": "web_url"
                            }
                        ]
                    }
                ]
                }
        }
        dispatcher.utter_message(attachment=message)
        return []

# class ActionGetPortfolio(Action):
    
#     def name(self) -> Text:
#         return "action_get_portfolio"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         # function to collect user id credntials

#         query = {'userId':"617fc06495c1d37b3135e397"} # to be conneced to 
#         # define mongoDB collection

#         wallet = db.redev.crypto_wallets
#         # intent = tracker.latest_message.intent['name']
#         answer = wallet.find_one(query)


        # dispatcher.utter_message("utter_wallet_balance",tracker, answer=link)

        # return []



# class ActionGetUserId(Action):
    
#     def name(self) -> Text:
#         return "action_get_userid"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         # function to collect user id credntials
#         return [SlotSet]



# class ActionCustomFallback(Action):

#     def name(self) -> Text:
#         return "action_custom_fallback"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
#         intents = [i for i in tracker.current_state()['latest_message']['intent_ranking'] if i['name'] != 'nlu_fallback']
#         allowed_intents = ["new_order", "what_happened", "inform"]
#         message = {
#             "new_order": "Do you want to place a new order?",
#             "what_happened": "Do you want to ask about a previous order?",
#             "inform": "Would you like more information about stroopwafels?"
#         }
#         buttons = [{'payload': i['name'], 'title': message[i['name']]} for i in intents[:3] if i['name'] in allowed_intents]
#         dispatcher.utter_message(
#             text="It wasn't 100% clear what you meant. Could you speficy/rephrase?",
#             buttons=buttons
#         )
#         return []


# import json
# from lunr.index import Index
# from clumper import Clumper


# # Read in the recipes with all the data.
# recipes = Clumper.read_jsonl("static/recipes.jsonl").collect()


# class ActionSuggestRecipe(Action):

#     def name(self) -> Text:
#         return "action_suggest_recipe"

#     async def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
#         db = {d['uid']: d for d in recipes}
#         # Read in the index for fast querying.
#         with open("static/index.json", "r") as f:
#             idx = Index.load(json.loads(f.read()))
        
#         # Attempt to find matching documents.
#         matches = idx.search(tracker.latest_message['text'])

#         # We may have no matches, respond appropriately.
#         if len(matches) == 0:
#             dispatcher.utter_message(text="Sorry, I couldn't find any recipes.")
#             return []
#         # We've found matches here, so we list the top 5.
#         dispatcher.utter_message(text="These recipes might be interesting.")
#         for match in matches[:5]:
#             item = db[match['ref']]
#             dispatcher.utter_message(f" - {item['name']}")
#         return []