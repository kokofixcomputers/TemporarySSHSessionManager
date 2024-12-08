import asyncio
import websockets
import requests
import subprocess
import os

host = os.environ.get('CONTAINER_HOST')

async def listen_for_commands():
    uri = scheme + "://" + host + port
    try:
        async with websockets.connect(uri) as websocket:
            while True:
                command = await websocket.recv()
                print(f"{command}")
    except websockets.exceptions.ConnectionClosedError:
                print("Agent disconnected. Reconnecting...")

if __name__ == "__main__":
    response = requests.get(host + "/agent/handshake").json()
    if response['message'] == "OK" and response['code'] == 200:
        # Awesome! Ready to connect.
        port = int(response['port'])
        scheme = response['scheme']
    else:
        print("Error: Agent handshake failed.")
        exit(1)
    asyncio.run(listen_for_commands())