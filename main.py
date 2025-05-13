# main.py
import asyncio
import websockets
import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()
bot_token = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")

async def connect():
    uri = "wss://rpc.hyperliquid.xyz/ws"
    data = []

    # 載入 JSON 檔案
    with open('tokens.json', 'r') as f:
        data = json.load(f)

    async with websockets.connect(uri) as websocket:
        await websocket.send('{"method": "subscribe", "subscription": {"type": "explorerTxs"}}')
        while True:
            try:
                response = await websocket.recv()
                data = json.loads(response)
                for tx in data:
                    if isinstance(tx, dict):
                        action_type = tx.get("action", {}).get("type")
                        if action_type == "order":
                            tx_hash = tx.get("hash", "")
                            for order in tx["action"]["orders"]:
                                asset_index = int(order["a"])
                                price = order["p"]
                                size = order["s"]
                                if asset_index < len(data):
                                    name = data[asset_index].get("name", "")
                                    volume = float(size) * float(price)
                                    print(f"{asset_index} - {price} - {size} - {volume}")
                                    if (volume >= 100_000):
                                        message = f"🟩 多 🐳 - {name} 價值${volume}"
                                        if order["b"] == False:
                                            message = f"🟥 空 🐳 - {name} 價值${volume}"

                                        url = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}'
                                        requests.get(url)
                                else:
                                    print(f"Index {asset_index} is out of range.")

            except websockets.ConnectionClosed:
                print("Connection closed.")
                break


try:
    print("Starting...")
    asyncio.run(connect())
except KeyboardInterrupt:
    print("程序被中斷..")
