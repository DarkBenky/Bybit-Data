import bybit
import pandas as pd
import time
import pandas as pd
import datetime as dt
import ccxt
import numpy as np
import sqlite3 as sql
import threading

def check_if_user_valid(api_key_user = "FwnzUmI53zrJNQErck",api_secret_user = "oXFqQ4dnxeKBx8ghdhwBMdc1AAtNLHeg3wlM"):
    """
    Check if the user is valid by using the provided API key and API secret.

    Parameters:
        api_key_user (str): The API key of the user. Defaults to "FwnzUmI53zrJNQErck".
        api_secret_user (str): The API secret of the user. Defaults to "oXFqQ4dnxeKBx8ghdhwBMdc1AAtNLHeg3wlM".

    Returns:
        bool: True if the user is valid, False otherwise.
    """
    try:
        client = bybit.bybit(test=False,api_key=api_key_user,api_secret=api_secret_user)
        return True
    except:
        return False

def check_if_user_valid_mexc(api_key, api_secret):
    """
    Check if the provided API key and API secret are valid for the MEXC exchange.

    Args:
        api_key (str): The API key for the MEXC exchange.
        api_secret (str): The API secret for the MEXC exchange.

    Returns:
        bool: True if the API key and API secret are valid, False otherwise.
    """
    try:
        client = ccxt.mexc({
            'apiKey': api_key,
            'secret': api_secret,
        })
        return True
    except:
        return False
    
class OrderExecution:
    def __init__(self, exchange_name, api_key, secret):
        self.exchange_name = exchange_name
        self.api_key = api_key
        self.secret = secret
        if exchange_name == 'Bybit':
            self.exchange = bybit.bybit(test=False,api_key=api_key,api_secret=secret)
        elif exchange_name == 'Mexc':
            self.exchange = ccxt.mexc({
                'apiKey': api_key,
                'secret': secret,
            })


    def execute_order(self, pair, side, order_type, quantity, price=None):
        """
        Executes an order on the exchange.

        Args:
            pair (str): The trading pair for the order.
            side (str): The side of the order, either 'buy' or 'sell'.
            order_type (str): The type of the order, either 'market' or 'limit'.
            quantity (float): The quantity of the asset to trade.
            price (float, optional): The price at which to execute the order. Required for limit orders.

        Returns:
            dict or None: The order object returned by the exchange API, or None if the order type is invalid.
        """
        if order_type == 'market':
            if side == 'buy':
                order = self.exchange.create_market_buy_order(pair, quantity,)
            elif side == 'sell':
                order = self.exchange.create_market_sell_order(pair, quantity,)
        elif order_type == 'limit':
            if side == 'buy':
                order = self.exchange.create_limit_buy_order(pair, quantity, price)
            elif side == 'sell':
                order = self.exchange.create_limit_sell_order(pair, quantity, price)
        else:
            return None  # Invalid order type
        return order
    

# mexc key mx0vgl6OaSE0cVBAMH secret 830bae207b5e46a3b39352894720fb13

def close_order(api_key , api_secret , exchange):
    if exchange == 'Bybit':
        pass
    else:
        OB = OrderExecution(exchange , api_key , api_secret)
        exchange_name = exchange
        exchange = OB.exchange
        try:
            exchange.cancel_all_orders('BTC/USDC')
        except Exception as e:
            print(e)
            pass
        


def close_all_orders():
    database = sql.connect("database.db")
    cursor = database.cursor()
    
    account = cursor.execute("SELECT * FROM accounts").fetchall()
    threads = []
    
    for acc in account:
        thread = threading.Thread(target= close_order , args=(acc[1],acc[2],acc[3]))
        threads.append(thread)
        thread.start()
        
    for thread in threads:
        thread.join()


def create_order(user , api_key , api_secret , exchange , side , ammount):
    OB = OrderExecution(exchange , api_key , api_secret)
    exchange_name = exchange
    exchange = OB.exchange
    # exchange.options['createMarketBuyOrderRequiresPrice'] = False
    # exchange.options['createMarketSellOrderRequiresPrice'] = False
    if side == 'BUY':
        try:
            ammount = exchange.fetchBalance()['total']['BTC'] * ammount
            if ammount < 0.00015:
                ammount = 0.000175
            ticker = exchange.fetch_ticker('BTC/USDC')
            last_price = ticker['ask']
            order = exchange.create_limit_buy_order('BTC/USDC', ammount, last_price)
            print(order)
        except Exception as e:
            print(e)
            pass
    elif side == 'SELL':
        try:
            ammount = exchange.fetchBalance()['total']['BTC'] * ammount
            if ammount < 0.00015:
                ammount = 0.000175
            ticker = exchange.fetch_ticker('BTC/USDC')
            last_price = ticker['bid']
            order = exchange.create_limit_sell_order('BTC/USDC', ammount, last_price)
            print(order)
        except Exception as e:
            print(e)
            pass
    else:
        pair = None
    
    database = sql.connect("database.db")
    cursor = database.cursor()
    
    if exchange_name == 'Bybit':
        pass
        # client = bybit.bybit(test=False,api_key=api_key,api_secret=api_secret)
        # balance = client.Wallet.Wallet_getBalance(coin='BTC').result()
        # return balance
    elif exchange_name == 'Mexc':
        try:
            balance = exchange.fetch_balance()
            for key in balance['total']:
                if 'BTC' in key:
                    balance_BTC = balance['total'][key]
                if 'USDC' in key:
                    balance_USDC = balance['total'][key]
            if balance_BTC == None:
                balance_BTC = 0
            if balance_USDC == None:
                balance_USDC = 0 
            cursor.execute('''INSERT INTO balances (username, BTC, USD) VALUES (?,?,?)''', (user, balance_BTC, balance_USDC))
            overall_balance = balance_BTC * exchange.fetch_ticker('BTC/USDC')['last'] + balance_USDC
            cursor.execute('''INSERT INTO overall_value (username, overall_value) VALUES (?,?)''', (user, overall_balance))
            database.commit()
            database.close()
        except Exception as e:
            print(e)
            pass
        
    
    

def create_all_orders(side , ammount):
    database = sql.connect("database.db")
    cursor = database.cursor()
    
    account = cursor.execute("SELECT * FROM accounts").fetchall()
    threads = []
    
    for acc in account:
        thread = threading.Thread(target= create_order , args=(acc[0],acc[1],acc[2],acc[3],side,ammount))
        threads.append(thread)
        thread.start()
        
    for thread in threads:
        thread.join()

            
def get_balance(key,secret,exchange):
    """
    Get the balance of the user in the exchange.

    Args:
        key (str): The API key of the user.
        secret (str): The API secret of the user.
        exchange (str): The name of the exchange.

    Returns:
        balance_BTC (float): The balance of the user in BTC.
        balance_USDC (float): The balance of the user in USDC.
    """
    if exchange == 'Bybit':
        client = bybit.bybit(test=False,api_key=key,api_secret=secret)
        balance = client.Wallet.Wallet_getBalance(coin='BTC').result()
        return balance
    elif exchange == 'Mexc':
        client = ccxt.mexc({
            'apiKey': key,
            'secret': secret,
        })
        #  get total balance
        balance = client.fetch_balance()
        for key in balance['total']:
            if 'BTC' in key:
                balance_BTC = balance['total'][key]
            if 'USDC' in key:
                balance_USDC = balance['total'][key]
        if balance_BTC == None:
            balance_BTC = 0
        if balance_USDC == None:
            balance_USDC = 0 
        return balance_BTC, balance_USDC
    
