import requests

from html_table_parser.parser import HTMLTableParser

from bs4 import BeautifulSoup as bs

import pandas as pd

from flask import Flask, render_template, request

from flask.views import View

app = Flask(__name__)


# Getting URL address into variable (Preparing a variable for HTML parsing)
req = requests.get(url='https://www.cnb.cz/cs/platebni-styk/sluzby-pro-klienty/kurzovni-listek-cnb/')

# Parsing URL address to HTML code and encoding setup
f = bs(req.content,'html.parser').decode('utf-8')

# Define HTML parsing object
p = HTMLTableParser()

# Filling the parsing object by HTML code
p.feed(f)

df = pd.DataFrame(p.tables[0])

column_headers =['Měna',
       'Země',
       'Množství',
       'Deviza_Nákup',
       'Deviza_Prodej',
       'Valuta_Nákup',
       'Valuta_Prodej']

df.columns = column_headers
df = df.loc[df['Měna'].isin(['EUR','GBP','USD'])]
df.set_index('Měna')



EUR_buy_sell = list((df.iat[0,3].replace(',','.'), df.iat[0,4].replace(',','.')))
GBP_buy_sell = list((df.iat[1,3].replace(',','.'), df.iat[1,4].replace(',','.')))
USD_buy_sell = list((df.iat[2,3].replace(',','.'), df.iat[2,4].replace(',','.')))




class Xchange(View):
    methods = ['GET', 'POST']

    def __init__(self):
        self.buy_sell = request.form.get("buy_or_sell")
        self.currency = request.form.get("currency")
        self.amount = request.form.get("cislo")

        if self.amount in (None,''):
            pass
        else:
            self.amount = float(self.amount)

    
    def currency_transfer(self):
        if self.buy_sell == 'buy' and self.currency == 'EUR':
            return str(round(float(EUR_buy_sell[1]) * self.amount, 2)) + ' CZK'
        elif self.buy_sell == 'sell' and self.currency == 'EUR':
            return str(round(self.amount * float(EUR_buy_sell[0]), 2)) + ' CZK'
        elif self.buy_sell == 'buy' and self.currency == 'GBP':
            return str(round(float(GBP_buy_sell[1]) * self.amount, 2)) + ' CZK' 
        elif self.buy_sell == 'sell' and self.currency == 'GBP':
            return str(round(self.amount * float(GBP_buy_sell[0]), 2)) + ' CZK'
        elif self.buy_sell == 'buy' and self.currency == 'USD':
            return str(round(float(USD_buy_sell[1]) * self.amount, 2)) + ' CZK' 
        elif self.buy_sell == 'sell' and self.currency == 'USD':
            return str(round(self.amount * float(USD_buy_sell[0]), 2)) + ' CZK'

    def transfer_message(self):
        if self.buy_sell == 'buy' and self.currency == 'EUR':
            return f'For {self.amount} EUR you will pay {str(round(float(EUR_buy_sell[1]) * self.amount, 2))} CZK'
        elif self.buy_sell == 'sell' and self.currency == 'EUR':
            return f'For {self.amount} EUR you will get {str(round(self.amount * float(EUR_buy_sell[0]), 2))} CZK'
        elif self.buy_sell == 'buy' and self.currency == 'GBP':
            return f'For {self.amount} GBP you will pay {str(round(float(GBP_buy_sell[1]) * self.amount, 2))} CZK' 
        elif self.buy_sell == 'sell' and self.currency == 'GBP':
            return f'For {self.amount} GBP you will get {str(round(self.amount * float(GBP_buy_sell[0]), 2))} CZK'
        elif self.buy_sell == 'buy' and self.currency == 'USD':
            return f'For {self.amount} USD you will pay {str(round(float(USD_buy_sell[1]) * self.amount, 2))} CZK' 
        elif self.buy_sell == 'sell' and self.currency == 'USD':
            return f'For {self.amount} USD you will get {str(round(self.amount * float(USD_buy_sell[0]), 2))} CZK'  


    def dispatch_request(self):
        if self.amount in (None,''):
            result = ''
            text = ''
        else:
            values = Xchange()
            result = values.currency_transfer()
            text = values.transfer_message()
            
        

        return render_template("template_money_exchange.html", result = result, text = text) #Vrátíme naší šablonu s výsledkem
    

    
app.add_url_rule("/", view_func= Xchange.as_view(name="xchange"))

if __name__ == "__main__":
    app.run(debug=True)