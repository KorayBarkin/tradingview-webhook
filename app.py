from flask import Flask, request
import json
import telebot
from binance.um_futures import UMFutures

app = Flask(__name__)

@app.route("/webhook", methods=['POST'])
def webhook():
    try:
        data = json.loads(request.data)
        print(data)
        
        ticker = data['ticker']
        exchange = data['exchange']
        price = float(data['price'])
        side = data['side']
        quantity = data['quantity']
        telegramBotApi = data['telegramBotApi']
        telegramUserId = data['telegramUserId']
        binanceApiKey = data['binanceApiKey']
        binanceSecretKey = data['binanceSecretKey']
        #time = data['time']
        # Initialize the Binance CMFutures client
        cm_futures_client = UMFutures(key=binanceApiKey, secret=binanceSecretKey)
        
        # Debugging account info

        # Debugging symbol info
        try:
            symbol_info = cm_futures_client.exchange_info()
            # print(f"Symbol Info: {symbol_info}")
            symbol_details = next((s for s in symbol_info['symbols'] if s['symbol'] == data["ticker"]), None)
            if not symbol_details:
                raise Exception("Symbol details not found")
            precision = symbol_details['quantityPrecision']
            print("Precision: ", precision)
            min_qty = float(symbol_details['filters'][2]['minQty'])  # Assumes the third filter is MIN_NOTIONAL
        except Exception as e:
            print(f"Error retrieving symbol info: {e}")
            raise

        usdt = 300.0
        calculated_qty = round(usdt / price, precision)
        final_qty = max(calculated_qty, min_qty)

        available_margin = 0
        try:
            account_info = cm_futures_client.account()
            for asset in account_info['assets']:
                if asset['asset'] == 'USDT':
                    available_margin = float(asset['availableBalance'])
            print(f"Available Margin: {available_margin}")
        except Exception as e:
            print(f"Error retrieving available margin: {e}")
            raise
        
        if available_margin < usdt:
            raise Exception("Insufficient margin available")

        params = {
            "symbol": data["ticker"],
            "side": side,
            "type": 'MARKET',
            "quantity": final_qty,
            "isIsolated": "TRUE",
        }
        print(usdt, price, usdt / price, params['quantity'])
        
        # Changing leverage
        try:
            cm_futures_client.change_leverage(symbol=data["ticker"], leverage=5, recvWindow=6000)
        except Exception as e:
            print(f"Error changing leverage: {e}")
            raise

        # Placing the order
        try:
            cm_futures_client.new_order(**params)
            print("Order placed successfully")
        except Exception as e:
            print(f"Error placing order: {e}")
            raise

        telebot.TeleBot(telegramBotApi).send_message(telegramUserId,
                                                     f"{ticker} ----> {side}ING \nPrice: {price} \nQuantity : {final_qty} ")
    except Exception as e:
        print(f"An error occurred: {e}")
    return {
        "code": "success",
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8031)
