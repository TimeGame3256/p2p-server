import asyncio
import websockets
import json
import os

peers = {}

async def handler(websocket):
    peer_id = None
    try:
        async for message in websocket:
            data = json.loads(message)
            cmd = data.get("cmd")

            if cmd == "register":
                peer_id = data["id"]
                peers[peer_id] = {
                    "ip": data["ip"],
                    "port": data["port"],
                    "ws": websocket
                }
                print(f"[+] {peer_id} онлайн: {data['ip']}:{data['port']}")

            elif cmd == "get_peer":
                target = data["target"]
                if target in peers:
                    await websocket.send(json.dumps({
                        "cmd": "peer_info",
                        "ip": peers[target]["ip"],
                        "port": peers[target]["port"]
                    }))
                else:
                    await websocket.send(json.dumps({"cmd": "waiting"}))

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if peer_id and peer_id in peers:
            del peers[peer_id]
            print(f"[-] {peer_id} офлайн")

async def main():
    port = int(os.environ.get("PORT", 9000))
    print(f"СЕРВЕР P2P МЕССЕНДЖЕРА ЗАПУЩЕН (порт {port})")
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()

asyncio.run(main())
