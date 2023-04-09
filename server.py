import asyncio
import websockets
import json
import schedule
import time
import os

join_data = []
music_data = []
password = os.environ['PASSWORD']
clients = set()

async def server(websocket, path):
    global join_data
    global music_data
    global clients
    global password

    clients.add(websocket)
    if path == '/join':
        await websocket.send(json.dumps(join_data))
    elif path == '/music':
        await websocket.send(json.dumps(music_data))

    async for message in websocket:
        message = json.loads(message)
        
        if path == '/join':
            try:
                if message['event'] == 'add':
                    join_data.append([message['user'], message['nickname']])
                    await websockets.broadcast(clients, json.dumps(join_data))
                elif message['event'] == 'leave':
                    for i, elem in enumerate(join_data):
                        if elem[0] == message['user']:
                            join_data.pop(i)
                            break
                    await websockets.broadcast(clients, json.dumps(join_data))
                elif message['event'] == 'next':
                    join_data = join_data[4:]
                    await websockets.broadcast(clients, json.dumps(join_data))
                elif message['event'] == 'delete':
                    join_data = []
                    await websockets.broadcast(clients, json.dumps(join_data))
                elif message['event'] == 'remove':
                    join_data.pop(message['id'])
                    await websockets.broadcast(clients, json.dumps(join_data))
                
            except:
                pass
            
        elif path == '/music':
            try:
                if message['event'] == 'add':
                    music_data.append([message['track'], message['nickname'], message['image'], message['url'], message['listened']])
                    await websockets.broadcast(clients, json.dumps(music_data))
                elif message['event'] == 'set-listened':
                    music_data[message['id']][-1] = 'listened'
                    await websockets.broadcast(clients, json.dumps(music_data))
                elif message['event'] == 'clear':
                    music_data = []
                    await websockets.broadcast(clients, json.dumps(music_data))
            except:
                pass
            
        elif path == '/auth':
            if message['event'] == 'login':
                if message['password'] == password:
                    await websocket.send('ok')
    clients.remove(websocket)
    print('Connection closed:', websocket)

def clear_data():
    global join_data
    global music_data
    join_data = []
    music_data = []

schedule.every().day.at("00:00").do(clear_data)

async def main():
    async with websockets.serve(server, "", port=int(os.environ["PORT"])):
        while True:
            schedule.run_pending()
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
