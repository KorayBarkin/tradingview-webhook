from flask import Flask, request
import json
import telebot
from binance.spot import Spot as Client
from binance.um_futures import UMFutures

cm_futures_client = UMFutures()
cm_futures_client = UMFutures(key="dxEwDgC5sC963gy8tYE8gIAU3RDKL7JdHeGN95jqiS6S5gUp2dbBwngmlviSqkmk", secret="qQpSatKOO70ty2EMSf8PEa2NfnKY1ABsUXakNPDPzSyD2IZD8OP9g3fouUDPLeNy")

# Price precision. BTC has 1, XRP has 4
def get_price_precision(symbol):
    resp = cm_futures_client.exchange_info()['symbols']
    for elem in resp:
        if elem['symbol'] == symbol:
            return elem


# Amount precision. BTC has 3, XRP has 1
def get_qty_precision(symbol):
    resp = cm_futures_client.exchange_info()['symbols']
    for elem in resp:
        if elem['symbol'] == symbol:
            return elem['quantityPrecision']
        
# getting your futures balance in USDT
def get_balance_usdt():
        response = cm_futures_client.balance(recvWindow=6000)
        for elem in response:
            if elem['asset'] == 'USDT':
                return float(elem['balance'])

def get_tickers_usdt():
    tickers = []
    resp = cm_futures_client.ticker_price()
    for elem in resp:
        if 'USDT' in elem['symbol']:
            tickers.append(elem['symbol'])
    return tickers

print(get_tickers_usdt())
