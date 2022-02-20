from binance.spot import Spot
from binance.lib.utils import config_logging
from binance.error import ClientError
import time
import datetime
import logging


# mtsLUfoBVpcINTrWzfvut7zcplxHPYwXeJzXKwXUYXMXPWVbdeolf5sMRFfMswV1
# T8cwg8zW3MgSQbBsHTyzo5qArRcV4TWymjOhqyhIWDEedczgKauWd0UCJ2jG1Dht


def cur_price():
    return float(client.ticker_24hr("BNBBUSD").get("lastPrice"))


def avg_price():
    return float(client.avg_price("BNBBUSD").get("price"))

client = Spot(key="mtsLUfoBVpcINTrWzfvut7zcplxHPYwXeJzXKwXUYXMXPWVbdeolf5sMRFfMswV1",
              secret="T8cwg8zW3MgSQbBsHTyzo5qArRcV4TWymjOhqyhIWDEedczgKauWd0UCJ2jG1Dht")

if client.get_open_orders("BNBBUSD")!=[]:   #Closing all open orders
    client.cancel_open_orders("BNBBUSD")

for i in client.account().get("balances"):  #Getting data about BNB wallet
    if i.get("asset") == "BNB":
        bnb_amount = float(i.get("free"))

for i in client.account().get("balances"):  #Getting data about BUSD wallet
    if i.get("asset") == "BUSD":
        busd_amount = float(i.get("free"))

if bnb_amount*cur_price()> busd_amount:     #Deciding our to buy or to sell status
    holded = 1
else:
    holded = 0
up_c = 1.0035 #trade mults
low_c=0.998

if holded == 1:                             #Setting values for first trades
    buy_price = cur_price()
    print("Start price:",buy_price,"Hold status:",holded)
    print("waiting for ", buy_price * up_c, " of BNB to SELL\n")
    lastprice = buy_price
else:
    sell_price =cur_price()
    print("Start price:",sell_price,"Hold status:",holded)
    print("waiting for ", sell_price * low_c, " of BNB to BUY\n")
    lastprice = sell_price

print("BNB:",bnb_amount,"$: " ,busd_amount)

while 1:
    for i in client.account().get("balances"): #Every loop updates wallet info
        if i.get("asset") == "BNB":
            bnb_amount = float(i.get("free"))
    for i in client.account().get("balances"):
        if i.get("asset") == "BUSD":
            busd_amount = float(i.get("free"))


    current_price = cur_price() # And updates Current price


    try:
        if holded == 0 and sell_price*low_c>=current_price and client.get_open_orders("BNBBUSD")==[]: #checkes the market
            params = {
                'symbol': 'BNBBUSD',
                'side': 'BUY',
                'type': 'LIMIT',
                'timeInForce': 'GTC',
                'quantity': round((busd_amount/current_price)-0.0006, 3),
                'price': current_price
            }

            print("quantity",params.get("quantity"))
            client.new_order(**params)
            holded=1
            buy_price = current_price
            lastprice = buy_price
            print("Done buy: ", buy_price, "x", params.get('quantity'),"=",buy_price*params.get('quantity'), datetime.datetime.now())
            print("BNB ", bnb_amount, "  $ ", busd_amount)
            print("waiting for ", buy_price*up_c, " of BNB to SELL\n")

        if holded == 1 and (buy_price*up_c) <=current_price and client.get_open_orders("BNBBUSD")==[]:
            params = {
                'symbol': 'BNBBUSD',
                'side': 'SELL',
                'type': 'LIMIT',
                'timeInForce': 'GTC',
                'quantity': round(bnb_amount-0.0006, 3),
                'price': current_price
            }

            print('quantity',round(bnb_amount-0.006, 3))
            client.new_order(**params)
            holded=0
            sell_price = current_price
            lastprice = sell_price
            print("Done sell: ",sell_price,"x",params.get('quantity') ,"=", sell_price*params.get('quantity'), datetime.datetime.now())
            print("BNB ", bnb_amount, "  $ ", busd_amount)
            print("waiting for ",sell_price*low_c," of BNB to BUY\n")

    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
    if lastprice*0.97>current_price:
        params = {
            'symbol': 'BNBBUSD',
            'side': 'SELL',
            'type': 'LIMIT',
            'timeInForce': 'GTC',
            'quantity': round(bnb_amount - 0.0006, 3),
            'price': current_price
        }

        client.new_order(**params)
        print("Script was stoped automaticly. Price droped to ", current_price)
        break
    time.sleep(1)
