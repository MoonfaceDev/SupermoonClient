import asyncio
import subprocess
from asyncio import StreamWriter, StreamReader

from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect

from supermoon_client.api_decorator import supermoon_api

router = APIRouter(
    prefix='/shell',
    tags=['Shell']
)


async def handle_shell_websocket(websocket: WebSocket, command: str):
    async def websocket_consumer(destination_stream: StreamWriter):
        while True:
            try:
                data = await websocket.receive_text()
            except WebSocketDisconnect:
                return
            destination_stream.write(data.encode() + b'\r\n')

    async def websocket_producer(source_stream: StreamReader):
        while True:
            data = await source_stream.read(1)
            if not data:
                return
            await websocket.send_text(data.decode())

    await websocket.accept()
    process = await asyncio.create_subprocess_shell(
        command, shell=True,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdin_task = asyncio.create_task(websocket_consumer(process.stdin))
    stdout_task = asyncio.create_task(websocket_producer(process.stdout))
    stderr_task = asyncio.create_task(websocket_producer(process.stderr))
    await asyncio.wait([stdin_task, stdout_task, stderr_task], return_when=asyncio.FIRST_COMPLETED)
    if process.returncode is None:
        process.stdin.close()
        process.stdout.feed_eof()
        process.stderr.feed_eof()
        process.terminate()
    await process.wait()


@router.websocket('/cmd')
@supermoon_api
async def cmd(websocket: WebSocket):
    return await handle_shell_websocket(websocket, 'cmd')


@router.websocket('/python')
@supermoon_api
async def python(websocket: WebSocket):
    return await handle_shell_websocket(websocket, 'python -i')
