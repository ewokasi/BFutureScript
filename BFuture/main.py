from binance.spot import Spot
from binance.lib.utils import config_logging
from binance.error import ClientError
import time
from datetime import datetime
import logging


def cur_price():
    return float(client.ticker_24hr("BNBBUSD").get("lastPrice"))


def avg_price():
    return float(client.avg_price("BNBBUSD").get("price"))


if __name__ == "__main__":
    client = Spot(key="####",
                  secret="###")

    if client.get_open_orders("BNBBUSD"):  # Closing all open orders
        client.cancel_open_orders("BNBBUSD")

    for i in client.account().get("balances"):  # Getting data about BNB wallet
        if i.get("asset") == "BNB":
            bnb_amount = float(i.get("free"))
        if i.get("asset") == "BUSD":
            busd_amount = float(i.get("free"))

    if bnb_amount * cur_price() > busd_amount:  # Deciding to sell or to buy status
        bnb_hold = 1
    else:
        bnb_hold = 0

    up_c = 1.002  # trade mults
    low_c = 0.998
    if bnb_hold == 1:  # Setting values for first trades
        current = cur_price()
        average = avg_price()

        if current > average * up_c:
            up_price = current
        else:
            up_price = average * up_c

        print(f"Start at {datetime.now()}\nAvg price: {average}, cur price {current}\n"
              f"Waiting for {up_price} to SELL\n")
    else:
        current = cur_price()
        average = avg_price()

        if current < average * low_c:
            low_price = current
        else:
            low_price = average * low_c

        print(f"Start at {datetime.now()}\nAvg price: {average}, cur price {current}\n"
              f"Waiting for {low_price} To Buy\n")
    lastorder_time = datetime.now()
    print("BNB:", bnb_amount, "$: ", busd_amount, '\n')

    while 1:
        current = cur_price()

        for i in client.account().get("balances"):  # Getting data about BNB wallet
            if i.get("asset") == "BNB":
                bnb_amount = float(i.get("free"))
            if i.get("asset") == "BUSD":
                busd_amount = float(i.get("free"))


        if bnb_hold:
            if current > up_price and client.get_open_orders() == []:

                params = {
                    'symbol': 'BNBBUSD',
                    'side': 'SELL',
                    'type': 'LIMIT',
                    'timeInForce': 'GTC',
                    'quantity': round(bnb_amount -0.0006, 3),
                    'price': current
                }
                post = client.new_order(**params)
                print(f"Order posted{datetime.now()}")
                low_price = current * low_c
                bnb_hold = 0
                lastorder_time = datetime.now()
                while client.get_open_orders():
                    time.sleep(10)
                print(f"\n-------{datetime.now()}-------\nПродажа {params['quantity']} BNB на сумму {params['quantity']*current}\nКурс {current}\nОжидание курса {low_price}\n")



        else:
            if current < low_price and client.get_open_orders() == []:
                params = {
                    'symbol': 'BNBBUSD',
                    'side': 'BUY',
                    'type': 'LIMIT',
                    'timeInForce': 'GTC',
                    'quantity': round(busd_amount / current-0.0006, 3),
                    'price': current
                }

                post = client.new_order(**params)
                bnb_hold = 1
                up_price = current * up_c
                lastorder_time =datetime.now()
                while client.get_open_orders():
                    time.sleep(10)
                print(
                    f"\n-------{datetime.now()}-------\nПокупка {params['quantity']} BNB на сумму {params['quantity'] * current}\nКурс {current}\nОжидание курса {up_price}\n")

        if lastorder_time.hour<=datetime.now().hour-3 and lastorder_time.day==datetime.now().day or datetime.now().hour+19 == lastorder_time.hour and lastorder_time.day==datetime.now().day-1:
            if client.get_open_orders():
                client.cancel_open_orders("BNBBUSD")

            if bnb_hold == 1:  # Setting values for first trades
                current = cur_price()
                average = avg_price()

                if current > average * up_c:
                    up_price = current
                else:
                    up_price = average * up_c


            else:
                current = cur_price()
                average = avg_price()

                if current < average * low_c:
                    low_price = current
                else:
                    low_price = average * low_c
            print(f"Restart at {datetime.now()}\nAvg price: {average}, cur price {current}\n"
                  f"Waiting for {low_price} to BUY\n")
            lastorder_time = datetime.now()
        time.sleep(2)
