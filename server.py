import asyncio
import websockets
import threading

connected_agents = set()

async def handler(websocket, path):
    print("Agent connected")
    connected_agents.add(websocket)
    try:
        async for message in websocket:
            print(f"Received from agent: {message}")
    except websockets.exceptions.ConnectionClosedError:
        print("Connection closed with agent")
    finally:
        connected_agents.remove(websocket)
        print("Agent disconnected")

async def start_server():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("WebSocket server started on ws://0.0.0.0:8765")
        await asyncio.Future()  # Run forever
        
def send_message(message):
    if connected_agents:
        for agent in connected_agents:
            asyncio.run(agent.send(message))

def start():
    server_thread = threading.Thread(target=lambda: asyncio.run(start_server()))
    server_thread.start()

    # Wait for both threads to finish (if they ever do)
    server_thread.join()