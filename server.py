import asyncio
import websockets
import threading
import json

# Dictionary to hold connected agents with their unique IDs
connected_agents = {}
agent_id_counter = 0

async def send_status_request(websocket):
    """Continuously send status request to the agent every minute."""
    while True:
        request_message = {"message": "request_report_status"}
        await websocket.send(json.dumps(request_message))
        await asyncio.sleep(60)  # Wait for 60 seconds before sending again

async def handler(websocket, path):
    global agent_id_counter
    # Assign a unique ID to the new agent
    agent_id = agent_id_counter
    connected_agents[websocket] = agent_id
    agent_id_counter += 1

    print(f"Agent {agent_id} connected")

    # Start sending status requests to the newly connected agent
    asyncio.create_task(send_status_request(websocket))

    try:
        async for message in websocket:
            print(f"Received from agent {agent_id}: {message}")
    except websockets.exceptions.ConnectionClosedError:
        print(f"Connection closed with agent {agent_id}")
    finally:
        del connected_agents[websocket]
        print(f"Agent {agent_id} disconnected")

async def start_server():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("WebSocket server started on ws://0.0.0.0:8765")
        await asyncio.Future()  # Run forever
        
def send_message(message):
    if connected_agents:
        for agent in connected_agents.keys():
            asyncio.run(agent.send(message))

def start():
    server_thread = threading.Thread(target=lambda: asyncio.run(start_server()))
    server_thread.start()

if __name__ == "__main__":
    start()