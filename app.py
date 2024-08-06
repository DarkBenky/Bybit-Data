import streamlit as st
import streamlit.components.v1 as components
import streamlit_extras as st_extras
from streamlit_card import card
from annotated_text import annotated_text, annotation
import pandas as pd
import numpy as np
import sqlite3
import hashlib
from streamlit_extras.buy_me_a_coffee import button
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
import time
import ByBit_API
import pickle
import plotly_express as px
import hydralit_components as hc
import grid_POC_TPO_strategy as POC_TPO
from markdownlit import mdlit
import ta
import data_formating_update as data_formatting
import yfinance as yf


class DB():
    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT, email TEXT, type TEXT)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS accounts (username TEXT, api_key TEXT, api_secret TEXT , exchange TEXT, active BOOLEAN, time REAL)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS transactions (username TEXT, buy_sell TEXT, amount REAL)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS balances (username TEXT, BTC REAL, USD REAL)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS trading_algorithms (username TEXT, name TEXT)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS payed_members (username TEXT, payed BOOLEAN , time REAL)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS trading_algo_settings (username TEXT, settings TEXT)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS overall_value (username TEXT, overall_value REAL)''')
        # create admin account
        self.c.execute('''SELECT * FROM users WHERE type =?''', ('admin',))
        if self.c.fetchall() == []:
            self.c.execute('''INSERT INTO users (username, password, email, type) VALUES (?,?,?,?)''', ('admin', hashlib.sha256('0fe423xDarkyNet$'.encode()).hexdigest(), ' ', 'admin'))
        self.conn.commit()
        
    def add_overall_value(self, username, overall_value):
        self.c.execute('''INSERT INTO overall_value (username, overall_value) VALUES (?,?)''', (username, overall_value))
        self.conn.commit()
    def get_overall_value(self, username):
        self.c.execute('''SELECT * FROM overall_value WHERE username =?''', (username,))
        return self.c.fetchall()
    def add_user(self, username, password, email, type_user):
        self.c.execute('''INSERT INTO users (username, password, email, type) VALUES (?,?,?,?)''', (username, password, email, type_user))
        self.conn.commit()
    def update_api(self,username, api_key, api_secret, exchange):
        self.c.execute('''UPDATE accounts SET api_key =? , api_secret =? , exchange =? WHERE username =?''', (api_key, api_secret, exchange, username))
        self.conn.commit()
    def add_account(self,  username ,api_key, api_secret, exchange , active , time):
        self.c.execute('''INSERT INTO accounts (username, api_key, api_secret, exchange , active, time) VALUES (?,?,?,?,?,?)''', (username, api_key, api_secret, exchange , active, time))
        self.conn.commit()
    def add_transaction(self, username, buy_sell, amount):
        self.c.execute('''INSERT INTO transactions (username, buy_sell, amount) VALUES (?,?,?)''', (username, buy_sell, amount))
        self.conn.commit()
    def add_balance(self, username, BTC, USD):
        self.c.execute('''INSERT INTO balances (username, BTC, USD) VALUES (?,?,?)''', (username, BTC, USD))
        self.conn.commit()
    def get_user(self, username):
        self.c.execute('''SELECT * FROM users WHERE username =?''', (username,))
        return self.c.fetchall()
    def get_balance(self, username):
        self.c.execute('''SELECT * FROM balances WHERE username =?''', (username,))
        return self.c.fetchall()
    def get_transactions(self, username):
        self.c.execute('''SELECT * FROM transactions WHERE username =?''', (username,))
        return self.c.fetchall()
    def get_accounts(self, username):
        self.c.execute('''SELECT * FROM accounts WHERE username =?''', (username,))
        return self.c.fetchall()
    def set_account_active_or_inactive(self, username, active):
        self.c.execute('''UPDATE accounts SET active =? WHERE username =?''', (active, username))
        self.conn.commit()
    def set_trading_algorithm(self, username, name):
        self.c.execute('''INSERT INTO trading_algorithms (username, name) VALUES (?,?)''', (username, name))
        self.conn.commit()
    def update_trading_algorithm(self, username, name):
        self.c.execute('''UPDATE trading_algorithms SET name =? WHERE username =?''', (name, username))
        self.conn.commit()
    def get_trading_algorithm(self, username):
        self.c.execute('''SELECT * FROM trading_algorithms WHERE username =?''', (username,))
        return self.c.fetchall()
    def set_payed_member(self, username, payed, time):
        self.c.execute('''INSERT INTO payed_members (username, payed, time) VALUES (?,?,?)''', (username, payed, time))
        self.conn.commit()
    def load_trading_algo_settings(self, username):
        self.c.execute('''SELECT * FROM trading_algo_settings WHERE username =?''', (username,))
        return self.c.fetchall()
    def save_trading_algo_settings(self, username, settings):
        self.c.execute('''INSERT INTO trading_algo_settings (username, settings) VALUES (?,?)''', (username, settings))
        self.conn.commit()
    def check_if_payed_member(self, username):
        self.c.execute('''SELECT * FROM payed_members WHERE username =?''', (username,))
        # check if user payed in the last 30 days
        if self.c.fetchall() == []:
            return False
        else:
            self.c.execute('''SELECT * FROM payed_members WHERE username =?''', (username,))
            if self.c.fetchall()[0][2] + 2592000 < time.time():
                return False
            else:
                return True

class User(DB):
    def __init__(self , username =None , password =None , email =None , type_user =None):
        super().__init__()
        self.username = username
        self.password = password
        self.email = email
        self.type_user = type_user
        try:
            self.username = self.get_username(username)
        except:
            self.username = None  
            
    def add_account_user(self , username ,  api_key , api_secret , exchange):
        if len(api_key) > 6 and len(api_secret) > 6:
            if exchange == "ByBit":
                if ByBit_API.check_if_user_valid(api_key , api_secret):
                    self.c.execute('''SELECT * FROM accounts WHERE api_key =? AND api_secret =?''', (api_key , api_secret,))
                    if self.c.fetchall() == []:
                        self.add_account(username ,api_key , api_secret , exchange  , False , time.time())
                    else:
                        return False 
                    return True
            if exchange == "Mexc":
                if ByBit_API.check_if_user_valid_mexc(api_key , api_secret):
                    self.c.execute('''SELECT * FROM accounts WHERE api_key =? AND api_secret =?''', (api_key , api_secret,))
                    if self.c.fetchall() == []:
                        self.add_account(username ,api_key , api_secret , exchange  , False , time.time())
                    else:
                        return False
                    return True
        return False
    def check_if_account_exists(self , username):
        self.c.execute('''SELECT * FROM accounts WHERE username =?''', (username,))
        return self.c.fetchall()
    def add_transaction(self, buy_sell, amount):
        self.add_transaction(self.username, buy_sell, amount)
        balance = self.get_balance(self.username)
        if balance == "buy":
            self.add_balance(self.username, balance[1] + amount, balance[2])
        elif balance == "sell":
            self.add_balance(self.username, balance[1] - amount, balance[2])
    def verify_user_login(self, username, password):
        self.c.execute('''SELECT * FROM users WHERE username =? AND password =?''', (username, password,))
        if self.c.fetchall() == []:
            return False
        return True
    def check_if_user_exists(self, username):
        self.c.execute('''SELECT * FROM users WHERE username =?''', (username,))
        if self.c.fetchall() == []:
            return False
        return True
    def check_if_admin(self, username , password):
        self.c.execute('''SELECT * FROM users WHERE username =? AND password =? AND type =?''', (username, password , 'admin',))
        if self.c.fetchall() == []:
            return False
        return True
    def show_DB(self):
        data = []
        self.c.execute('''SELECT * FROM users''')
        data.append(self.c.fetchall())
        self.c.execute('''SELECT * FROM accounts''')
        data.append(self.c.fetchall())
        self.c.execute('''SELECT * FROM transactions''')
        data.append(self.c.fetchall())
        self.c.execute('''SELECT * FROM balances''')
        data.append(self.c.fetchall())
        return data
            
st.set_page_config(page_title="AI-ByBit.com", page_icon="./assets/logo.png", layout="wide", initial_sidebar_state="expanded")

if 'current_user' not in st.session_state:
    st.session_state["current_user"] = None
if 'login' not in st.session_state:
    st.session_state["login"] = False
if 'current_page' not in st.session_state:
    st.session_state["current_page"] = "home"
if 'type_user' not in st.session_state:
    st.session_state["type_user"] = "user"
if 'api_key' not in st.session_state:
    st.session_state["api_key"] = None
if 'api_secret' not in st.session_state:
    st.session_state["api_secret"] = None
if 'POC_TPO_settings' not in st.session_state:
    st.session_state['POC_TPO_settings'] = {"ticks" : 12.5 , "window_size_in_days" : 0.10 , "look_back_in_days" : 0.25 , "ammount" : 0.1 , "number_of_TPOs_POCs" : 50 , "remove_close_TPOs_POCs_value" : 5 , "wait_after_order" : 15 , "offset" : 25}
if 'graph' not in st.session_state:
    st.session_state['graph'] = None
if 'subpage' not in st.session_state:
    st.session_state['subpage'] = "Portfolio"
if 'latest_data' not in st.session_state:
    index_names = {
        "Price" : 1,
        "Previous 24h price": 2,
        "Percent": 3,
        "Highest Price in 24h": 4,
        "Lowest Price in 24h": 5,
        "Previous price 1h": 6,
        "Open Interest": 7,
        "Turnover in 24h": 8,
        "Volume in 24 h": 9,
        "Funding Rate": 10,
        'Volume':11,
        'Average Volume':12,
        'Average Price':13,
        'Average Direction':14,
        'POC':15,
        'TP0':16,
        'VWAP':17,
        'RSI':18,
        'MACD':19,
        'OBV':20,
        'Boulanger Band1':21,
        'Boulanger Band2':22,
        'Boulanger Band3':23,
        'Resistance 1':24,
        'Resistance 2':25,
        'Resistance 3':26,
        'Support 1':27,
        'Support 2':28,
        'Support 3':29,
        'VOLIT1':30,
        'VOLIT2':31,
        'VOLIT3':32,
        'VOLIT4':33,
        'Change of Trend 1':34,
        'Change of Trend 2':35,
        'Change of Trend 3':36,
        'Price Pattern 1':37,
        'Price Pattern 2':38,
        'Price Pattern 3':39,
        'MA cross 1':40,
        'MA cross 2':41,
        'Weighted Moving Average 1':42,
        'Weighted Moving Average 2':43,
        'Weighted Moving Average 3':44,
        'True Strength Index 1':45,
        'True Strength Index 2':46,
        'True Strength Index 3':47,
        'Parentage Volume Oscillator 1':48,
        'Parentage Volume Oscillator 2':49,
        'Parentage Volume Oscillator 3':50,
        'Stochastic RSI 1':51,
        'Stochastic RSI 2':52,
        'Stochastic RSI 3':53,
        'Accumulation Distribution 1':54,
        'Accumulation Distribution 2':55,
        'Accumulation Distribution 3':56,
        'Donchian Channel 1':57,
        'Donchian Channel 2':58,
        'Donchian Channel 3':59,
        'Donchian Channel 4':60,
        'Donchian Channel 5':61,
        'Donchian Channel 6':62,
        'Donchian Channel 7':63,
        'Donchian Channel 8':64,
        'Donchian Channel 9':65,
        'Ulcer Index 1':66,
        'Ulcer Index 2':67,
        'Ulcer Index 3':68,
        'Volume Price Trend 1':69,
        'Volume Price Trend 2':70,
        'Volume Price Trend 3':71,
        'temp':72,
        'temp2':73,
        'temp3':74,
        'temp4':75,
        'temp5':76,
        'temp6':77,
    }
    index_names = {key: value - 1 for key, value in index_names.items()}
    data = data_formatting.load_last_x(120)
    df = pd.DataFrame(data , columns=index_names)
    st.session_state['latest_data'] = df


def POCs_TPOs():
    graph = POC_TPO.test_strategy(st.session_state["POC_TPO_settings"]['ticks'], st.session_state["POC_TPO_settings"]['window_size_in_days'] , st.session_state["POC_TPO_settings"]["look_back_in_days"] , st.session_state["POC_TPO_settings"]['ammount'],st.session_state["POC_TPO_settings"]['number_of_TPOs_POCs'], st.session_state["POC_TPO_settings"]['wait_after_order'] , st.session_state["POC_TPO_settings"]['offset'])
    st.session_state['graph'] = graph
    st.experimental_rerun()

def show_DB():
    user = User()
    st.write(user.show_DB())
    
        
def home_page():
    st.write(st.session_state)
    login , signup = st.sidebar.columns(2)
    with login:
        st.image("./assets/login.png" , width=48)
        if st.button("Login"):
            st.session_state["current_page"] = "login"
            st.experimental_rerun()
    with signup:
        st.image("./assets/signup.png" , width=48)
        if st.button("Sign Up"):
            st.session_state["current_page"] = "signup"
            st.experimental_rerun()
    left , right = st.columns(2)
    with left:
        st.image("./assets/img_big.png")
    with right:
        st.header("AI-ByBit.com")
        annotated_text(annotation("Welcome" , color='#f571cf') , "to" , annotation("AI-ByBit.com" , color='#f571cf'))
        annotated_text(annotation("The revolutionary platform that allows you to connect your exchange account to our advanced AI trading system.", color='#f571cf'))
        st.write("Our cutting-edge technology uses sophisticated algorithms to constantly analyze market data and execute trades on your behalf, 24/7, completely free of charge.")
        st.write("Gone are the days of having to manually monitor the markets and execute trades yourself.")
        annotated_text(annotation("With AI-ByBit.com, you can sit back and relax while our AI takes care of everything for you." , color='#f571cf'))
        st.write("Our system is designed to maximize profits and minimize risk, so you can trust that your assets are in good hands.")
        annotated_text(annotation("To get started, simply sign up for an account and link your exchange API key.", color='#f571cf'))
        st.write("Our user-friendly interface makes it easy to set your trading preferences and monitor your performance. You'll also have access to detailed analytics and performance reports so you can track your progress over time.")
        st.write("At AI-ByBit.com, our mission is to democratize access to advanced trading tools and strategies. We believe that everyone should have the opportunity to benefit from the power of AI, regardless of their level of experience or capital.")
        annotated_text(annotation("Join us today and experience the future of trading!", color='#f571cf'))
    colored_header('','',color_name="blue-40")
    l , r = st.columns(2)
    with r:
        st.image("./assets/icons-01.png")
    with l:
        st.header("We hope you enjoy using AI-ByBit.com!")
        st.write("you can support us by donating to our BTC address:")
        annotated_text(annotation('14kQykoaNMV4UDZ5S4D5HkWS3G7DBfdx8N', color='#f571cf'))
        st.write('or using XMR:')
        annotated_text(annotation('86ejs8FTPwRi1dMq4P8zV36sMNTwFyQouGxvzx42YNKLNt2pJHM9Ar8MfLKrn6AgxKWL4rmD6LVpVjdKDh1cLvxhNKtWCekj', color='#f571cf'))
    button('DarkBenky',bg_color="#36b2e4")
    colored_header('','',color_name="blue-40")
        
def login_page():
    user = User()
    st.write(st.session_state)
    left , middle, right = st.columns(3)
    with middle:
        error_msg = None
        st.header("Login to AI-ByBit.com")
        add_vertical_space(5)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        password = hashlib.sha256(password.encode()).hexdigest()
        # st.write(password)
        add_vertical_space(5)
        n ,n1 , l , r ,n2 , n3 = st.columns(6)
        with l:
            st.image("./assets/login.png" , width=48)
        with r:
            if st.button("Login"):
                if user.check_if_user_exists(username) and user.verify_user_login(username, password):
                    if user.check_if_admin(username, password):
                        st.session_state["type_user"] = "admin"
                        st.session_state["current_user"] = username
                        st.session_state["login"] = True
                        st.session_state["current_page"] = "admin_panel"
                        st.experimental_rerun()
                    st.session_state["current_user"] = username
                    st.session_state["login"] = True
                    st.session_state["current_page"] = "main_panel"
                    st.session_state["type_user"] = "user"
                    st.experimental_rerun()
                elif user.check_if_user_exists(username) and not user.verify_user_login(username, password):
                    error_msg = ("Wrong Password")
                else:
                    error_msg = ("Wrong Username or Account does not exist")
        if error_msg != None:
            st.error(error_msg)
    
                    
                

def signup_page():
    st.write(st.session_state)
    left , middle, right = st.columns(3)
    user = User()
    with middle:
        error_msg = None
        st.header("Sign Up to AI-ByBit.com")
        add_vertical_space(5)
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password")
        password = hashlib.sha256(password.encode()).hexdigest()
        add_vertical_space(5)
        n ,n1 , l , r ,n2 , n3 = st.columns(6)
        with l:
            st.image("./assets/signup.png" , width=48)
        with r:
            if st.button("Sign Up"):
                if user.check_if_user_exists(username):
                    error_msg = ("Username already exists")
                else:
                    user.add_user(username, password , email,  "user")
                    st.session_state["current_page"] = "login"
                    st.experimental_rerun()
        if error_msg != None:
            st.error(error_msg)
            
def advance_overview():
    st.header("Advance Overview")
    colored_header('','',color_name="blue-40")
    number_of_minutes = st.slider("Number of minutes" , 60 , 240 , 120)
    def update_data():
        index_names = {
        "Price" : 1,
        "Previous 24h price": 2,
        "Percent": 3,
        "Highest Price in 24h": 4,
        "Lowest Price in 24h": 5,
        "Previous price 1h": 6,
        "Open Interest": 7,
        "Turnover in 24h": 8,
        "Volume in 24 h": 9,
        "Funding Rate": 10,
        'Volume':11,
        'Average Volume':12,
        'Average Price':13,
        'Average Direction':14,
        'POC':15,
        'TP0':16,
        'VWAP':17,
        'RSI':18,
        'MACD':19,
        'OBV':20,
        'Boulanger Band1':21,
        'Boulanger Band2':22,
        'Boulanger Band3':23,
        'Resistance 1':24,
        'Resistance 2':25,
        'Resistance 3':26,
        'Support 1':27,
        'Support 2':28,
        'Support 3':29,
        'VOLIT1':30,
        'VOLIT2':31,
        'VOLIT3':32,
        'VOLIT4':33,
        'Change of Trend 1':34,
        'Change of Trend 2':35,
        'Change of Trend 3':36,
        'Price Pattern 1':37,
        'Price Pattern 2':38,
        'Price Pattern 3':39,
        'MA cross 1':40,
        'MA cross 2':41,
        'Weighted Moving Average 1':42,
        'Weighted Moving Average 2':43,
        'Weighted Moving Average 3':44,
        'True Strength Index 1':45,
        'True Strength Index 2':46,
        'True Strength Index 3':47,
        'Parentage Volume Oscillator 1':48,
        'Parentage Volume Oscillator 2':49,
        'Parentage Volume Oscillator 3':50,
        'Stochastic RSI 1':51,
        'Stochastic RSI 2':52,
        'Stochastic RSI 3':53,
        'Accumulation Distribution 1':54,
        'Accumulation Distribution 2':55,
        'Accumulation Distribution 3':56,
        'Donchian Channel 1':57,
        'Donchian Channel 2':58,
        'Donchian Channel 3':59,
        'Donchian Channel 4':60,
        'Donchian Channel 5':61,
        'Donchian Channel 6':62,
        'Donchian Channel 7':63,
        'Donchian Channel 8':64,
        'Donchian Channel 9':65,
        'Ulcer Index 1':66,
        'Ulcer Index 2':67,
        'Ulcer Index 3':68,
        'Volume Price Trend 1':69,
        'Volume Price Trend 2':70,
        'Volume Price Trend 3':71,
        'temp':72,
        'temp2':73,
        'temp3':74,
        'temp4':75,
        'temp5':76,
        'temp6':77,
    }
        index_names = {key: value - 1 for key, value in index_names.items()}
        data = data_formatting.load_last_x(number_of_minutes)
        df = pd.DataFrame(data , columns=index_names)
        st.session_state['latest_data'] = df
    if st.button("Update"):
        update_data()
        
    try:
        st.session_state['latest_data']['Time'] = pd.date_range(start=pd.Timestamp.now() - pd.Timedelta(minutes=number_of_minutes), periods=number_of_minutes, freq='1min')
    except:
        update_data()
        st.session_state['latest_data']['Time'] = pd.date_range(start=pd.Timestamp.now() - pd.Timedelta(minutes=number_of_minutes), periods=number_of_minutes, freq='1min')
    
    index_names = {
        "Price" : 1,
        "Previous 24h price": 2,
        "Percent": 3,
        "Highest Price in 24h": 4,
        "Lowest Price in 24h": 5,
        "Previous price 1h": 6,
        "Open Interest": 7,
        "Turnover in 24h": 8,
        "Volume in 24 h": 9,
        "Funding Rate": 10,
        'Volume':11,
        'Average Volume':12,
        'Average Price':13,
        'Average Direction':14,
        'POC':15,
        'TP0':16,
        'VWAP':17,
        'RSI':18,
        'MACD':19,
        'OBV':20,
        'Boulanger Band1':21,
        'Boulanger Band2':22,
        'Boulanger Band3':23,
        'Resistance 1':24,
        'Resistance 2':25,
        'Resistance 3':26,
        'Support 1':27,
        'Support 2':28,
        'Support 3':29,
        'VOLIT1':30,
        'VOLIT2':31,
        'VOLIT3':32,
        'VOLIT4':33,
        'Change of Trend 1':34,
        'Change of Trend 2':35,
        'Change of Trend 3':36,
        'Price Pattern 1':37,
        'Price Pattern 2':38,
        'Price Pattern 3':39,
        'MA cross 1':40,
        'MA cross 2':41,
        'Weighted Moving Average 1':42,
        'Weighted Moving Average 2':43,
        'Weighted Moving Average 3':44,
        'True Strength Index 1':45,
        'True Strength Index 2':46,
        'True Strength Index 3':47,
        'Parentage Volume Oscillator 1':48,
        'Parentage Volume Oscillator 2':49,
        'Parentage Volume Oscillator 3':50,
        'Stochastic RSI 1':51,
        'Stochastic RSI 2':52,
        'Stochastic RSI 3':53,
        'Accumulation Distribution 1':54,
        'Accumulation Distribution 2':55,
        'Accumulation Distribution 3':56,
        'Donchian Channel 1':57,
        'Donchian Channel 2':58,
        'Donchian Channel 3':59,
        'Donchian Channel 4':60,
        'Donchian Channel 5':61,
        'Donchian Channel 6':62,
        'Donchian Channel 7':63,
        'Donchian Channel 8':64,
        'Donchian Channel 9':65,
        'Ulcer Index 1':66,
        'Ulcer Index 2':67,
        'Ulcer Index 3':68,
        'Volume Price Trend 1':69,
        'Volume Price Trend 2':70,
        'Volume Price Trend 3':71,
        'temp':72,
        'temp2':73,
        'temp3':74,
        'temp4':75,
        'temp5':76,
        'temp6':77,
    }
    
    options = st.multiselect('Select Indicators', list(index_names.keys()))
    for option in options:
        fig = px.line(st.session_state['latest_data'], x="Time", y=option, title=option)
        st.header(option)
        st.plotly_chart(fig, use_container_width=True)        
    
     
            
         
def main_panel():
    show_DB()
    sidebar = st.sidebar.selectbox("Models", ["Portfolio", "Market Overview", 'Advance Overview','Account Settings'])
    if sidebar != st.session_state['subpage']:
        st.session_state['subpage'] = sidebar
        st.experimental_rerun()
    st.write(st.session_state)
    if st.session_state['subpage'] == 'Portfolio':
        st.header("Portfolio")
        colored_header('','',color_name="blue-40")
        user = User()
        # st.write(user.get_trading_algorithm(st.session_state["current_user"]))
        if user.check_if_account_exists(st.session_state["current_user"]) == []:
            st.warning("You have not linked your account yet")
            st.write("Please link your account to start using AI-ByBit.com")
            st.write("You can link your account by clicking on the button below")
            if st.button("Link Account"):
                st.session_state["current_page"] = "add_panel"
                st.experimental_rerun()
        elif user.get_trading_algorithm(st.session_state["current_user"]) == [] or user.get_trading_algorithm(st.session_state["current_user"])[0][1] == "None":
            st.warning("You have not set your trading algorithm yet")
            st.write("Please set your trading algorithm to start using AI-ByBit.com")
            st.write("You can set your trading algorithm by clicking on the button below")
            if st.button("Set Trading Algorithm"):
                st.session_state["current_page"] = "trading_algorithm"
                st.experimental_rerun()
        else:
            balance_data = ByBit_API.get_balance(user.get_accounts(st.session_state["current_user"])[0][1] , user.get_accounts(st.session_state["current_user"])[0][2] , user.get_accounts(st.session_state["current_user"])[0][3])
            user.add_balance(st.session_state["current_user"] , balance_data[0], balance_data[1])
            overall_value = user.get_overall_value(st.session_state["current_user"])
            balance = user.get_balance(st.session_state["current_user"])
            balance = pd.DataFrame(balance , columns=['username', 'BTC', 'USD'])
            balance['BTC'] = balance['BTC'].rolling(30).mean()
            balance['USD'] = balance['USD'].rolling(30).mean()
            balance = balance.drop(columns=['username'])
            # st.write(balance)
            
            left , right , right1 = st.columns(3)
            with left:
                st.header('Current Amount of BTC')
                colored_header('','',color_name="blue-40")
                st.subheader(f"{balance['BTC'].iloc[-1]} BTC")
                fig = px.line(balance , y='BTC')
                st.plotly_chart(fig, use_container_width=True)
            with right:
                st.header('Current Amount of USDC')
                colored_header('','',color_name="blue-40")
                st.subheader(f"{balance['USD'].iloc[-1]} USDC")
                fig = px.line(balance , y='USD')
                st.plotly_chart(fig, use_container_width=True)
            with right1:
                st.header('Overall Value in USD')
                colored_header('','',color_name="blue-40")
                overall_value = pd.DataFrame(overall_value , columns=['username', 'overall_value'])
                overall_value['overall_value'] = overall_value['overall_value'].rolling(30).mean()
                st.subheader(f"{overall_value['overall_value'].iloc[-1]} USD")
                # st.write(overall_value)
                fig = px.line(overall_value , y='overall_value')
                st.plotly_chart(fig, use_container_width=True)
                
    elif st.session_state['subpage'] == 'Market Overview':
        candle_fig, poc_fig , tpo_fig = ta.UI()
        st.header("Market Overview")
        colored_header('','',color_name="blue-40")
        st.plotly_chart(candle_fig , use_container_width=True)
        st.plotly_chart(poc_fig, use_container_width=True)
        st.plotly_chart(tpo_fig, use_container_width=True)
    elif st.session_state['subpage'] == 'Advance Overview':
        advance_overview()
    elif st.session_state['subpage'] == 'Account Settings':
        st.header("Account Settings")
        colored_header('','',color_name="blue-40")
        cul , cul1 = st.columns(2)
        with cul:
            user = User(username=st.session_state["current_user"])
            accounts = user.get_accounts(st.session_state["current_user"])
            st.write(accounts)
            api_key = st.text_input("API Key" , value=accounts[0][1])
            api_secret = st.text_input("API Secret" , value=accounts[0][2])
            exchange = st.selectbox("Select Exchange",("ByBit" , "Mexc") , index=1)
            if st.button("Update"):
                user.update_api(st.session_state["current_user"] , api_key , api_secret , exchange)
                st.experimental_rerun()
        with cul1:
            trading_algo = user.get_trading_algorithm(st.session_state["current_user"])
            st.warning(f"Your current trading algorithm is {trading_algo[0][1]}")
            if st.button('Remove Trading Algorithm'):
                user.update_trading_algorithm(st.session_state["current_user"] , 'None')
                st.experimental_rerun()
  
def trading_algorithm():
    st.write(st.session_state)
    left , middle , right= st.columns(3)
    @st.cache_data
    def load_graphs():
        pickle_in = open("test_xgb.pickle","rb")    
        graph = pickle.load(pickle_in)
        
        
        fig = px.line(graph , x='Time in 1 hour increments', y='Net worth over time in percentage change')
        average_hourly_gain = graph['Net worth over time in percentage change'].mean()
        # st.write(average_hourly_gain)
        
        # load predicted graph from results/black-XLEWL4ZZ-bird.csv
        df = pd.read_csv('results/black-XLEWL4ZZ-bird.csv ')
        # get evry 60th row
        df = df.iloc[::60, :]
        df['Net worth over time in percentage change'] = df['overall_net_worth']
        df['Time in 1 hour increments'] = [(str(i) + 'hour') for i in range(0,len(df))]
        
        # st.write(df)
        
        average_hourly_gain_2 = df['overall_net_worth'].mean()
        
        # st.write(average_hourly_gain_2)
        
        # pickle_in = open("test_OpenAI.pickle","rb")
        # graph2 = pickle.load(pickle_in)
        
        fig2 = px.line(df , x='Time in 1 hour increments', y='Net worth over time in percentage change')
        # average_hourly_gain_2 = graph2['Net worth over time in percentage change'].mean()
        
        # st.write(average_hourly_gain_2)
        
        pickle_in = open("test_grid.pickle","rb")
        graph3 = pickle.load(pickle_in)
        
        fig3 = px.line(graph3 , x='Time in 1 hour increments', y='Net worth over time in percentage change')
        average_hourly_gain_3 = graph3['Net worth over time in percentage change'].mean()
        
        
        return fig , fig2 , fig3 ,  average_hourly_gain , average_hourly_gain_2 , average_hourly_gain_3

   
        

    fig , fig2 , fig3 ,  average_hourly_gain , average_hourly_gain_2 , average_hourly_gain_3 = load_graphs()
    
    with left:
        st.header("CoinSense")
        colored_header('','',color_name="blue-40")
        st.write("CoinSense is a proprietary algorithm developed by AI-ByBit.com that uses advanced machine learning techniques to predict the future price of Bitcoin.")      
        
        st.plotly_chart(fig, use_container_width=True)
      
        
    with right:
        st.header("TradeMate")
        colored_header('','',color_name="blue-40")
        st.write("TradeMate is AI-ByBit.com's proprietary algorithm utilizing advanced machine learning to predict Bitcoin price.")

        st.plotly_chart(fig2, use_container_width=True)
    
    with middle:
        st.header("MarketMaster")
        colored_header('','',color_name="blue-40")
        st.write("MarketMaster is trading strategy with the power of grid-based trading.")
        
        st.plotly_chart(fig3, use_container_width=True)
        
    
    r_1 , m_1 , l_2 = st.columns(3)
    with r_1:
        bar = st.progress(0)
        for i in range(0,int(average_hourly_gain)):
            time.sleep(0.01)
            bar.progress(value = i + 1 , text = f"Average Hourly Gain: {average_hourly_gain.round(2)}%")
        st.warning('Experience the potential rewards with reduced risk')
        st.error('This strategy is still in development')
        l , m , r = st.columns(3)
        # with m:
        #     if st.button("Set Trading Algorithm"):
        #         user = User()
        #         user.set_trading_algorithm(st.session_state["current_user"] , "CoinSense")
        #         st.session_state["current_page"] = "main_panel"
        #         st.experimental_rerun()
                
    with m_1:
        bar2 = st.progress(0)
        for i in range(0,int(average_hourly_gain_3)):
            time.sleep(0.01)
            bar2.progress(value = i + 1 , text = f"Average Hourly Gain: {average_hourly_gain_3.round(2)}%")
        st.warning('Experience the potential rewards with reduced risk')
        st.error('This strategy is still in development')
        l , m , r = st.columns(3)
        # with m:
        #     if st.button("Set Trading Algorithm" , key='MarketMaster_button'):
        #         user = User()
        #         user.set_trading_algorithm(st.session_state["current_user"] , "MarketMaster")
        #         st.session_state["current_page"] = "main_panel"
        #         st.experimental_rerun()
    
    with l_2:
        bar1 = st.progress(0)
        for i in range(0,int(average_hourly_gain_2)):
            time.sleep(0.01)
            bar1.progress(value = i + 1 , text = f"Average Hourly Gain: {average_hourly_gain_2.round(2)}%")
        st.warning('Embrace the thrill of risk and potential rewards with this strategy.')
        l , m , r = st.columns(3)
        with m:
            if st.button("Set Trading Algorithm" , key='TradeMate_button'):
                user = User()
                user.set_trading_algorithm(st.session_state["current_user"] , "TradeMate")
                user.update_trading_algorithm(st.session_state["current_user"] , "TradeMate")
                st.session_state["current_page"] = "main_panel"
                st.experimental_rerun()
        
        
        
        
def add_panel():
    st.write(st.session_state)
    left , middle, right = st.columns(3)
    user = User()
    with middle:
        error_msg = None
        st.header("Add Account to AI-ByBit.com")
        add_vertical_space(5)
        
        st.markdown("---")
        exchange = st.selectbox("Select Exchange",("ByBit" , "Mexc"))
        if exchange == "ByBit":
            st.warning("ByBit exchange has fees for execution of trade")
        st.markdown("---")
        
        api_key = st.text_input("API Key")
        api_secret = st.text_input("API Secret")
        add_vertical_space(5)
        
        # st.write(ByBit_API.check_if_user_valid_mexc(api_key, api_secret))
        
        n  , l , r , n3 = st.columns(4)
        with l:
            st.image("./assets/signup.png" , width=48)
        with r:
            if st.button("Add Account"):
                if user.add_account_user(st.session_state['current_user'] , api_key , api_secret , exchange=exchange):
                    st.session_state["current_page"] = "main_panel"
                    st.session_state["api_key"] = api_key
                    st.session_state["api_secret"] = api_secret
                    st.experimental_rerun()
                else:
                    error_msg = ("Wrong API Key or API Secret")
        if error_msg != None:
            st.error(error_msg)

if st.session_state["current_page"]== "login":
    login_page()
elif st.session_state["current_page"] == "signup":
    signup_page()
elif st.session_state["current_page"] == "main_panel":
    main_panel()
elif st.session_state["current_page"] == "add_panel":
    add_panel()
elif st.session_state["current_page"] == "admin_panel":
    main_panel()
elif st.session_state["current_page"] == "trading_algorithm":
    trading_algorithm()
else:
    home_page()
    

        
        
        
        
        
        
        
            
            
        
        
        

