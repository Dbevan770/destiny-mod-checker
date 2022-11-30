import json
import random
    
# Get a random quote for the embeded message
def getQuote():

    with open("quotes.json") as quote_file:
        data = json.load(quote_file)
        quotes = list(data.items())

    random_num = random.randint(0, 23)

    quote = quotes[random_num][0]
    author = quotes[random_num][1]

    return f"“{quote}” - {author}"