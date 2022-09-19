from io import BytesIO
from typing import Literal

import numpy as np
import pyautogui
from PIL import ImageGrab
from fastapi import APIRouter, Query
from mss import mss, windows
from starlette.responses import Response, StreamingResponse

from supermoon_client.api_decorator import supermoon_api
from supermoon_client.utils import get_frames

windows.CAPTUREBLT = 0

router = APIRouter(
    prefix='/screen',
    tags=['Screen']
)


@router.get('/screenshot')
@supermoon_api
async def screenshot():
    image = ImageGrab.grab(all_screens=True)
    buffer = BytesIO()
    image.save(buffer, 'png')
    return Response(buffer.getvalue(), media_type='image/png')


@router.get('/screen_share')
@supermoon_api
async def screen_share(fps: float = Query(24), resolution: tuple[int, int] = Query((1920, 1080)),
                       monitor_index: int = Query(1)):
    def get_image():
        with mss() as capture:
            monitor = capture.monitors[monitor_index]
            capture_img = capture.grab(monitor)
            return np.array(capture_img)

    return StreamingResponse(get_frames(get_image=get_image, fps=fps, resolution=resolution),
                             media_type='multipart/x-mixed-replace; boundary=--frame')


@router.post('/mouse')
@supermoon_api
async def mouse_event(event: Literal['click', 'double', 'right'] = Query(), x: float = Query(), y: float = Query(),
                      width: float = Query(), height: float = Query()):
    # coordinates of desktop event
    dx, dy = pyautogui.size()
    x, y = dx * (x / width), dy * (y / height)
    # handle event
    if event == 'click':
        pyautogui.click(x, y)
    elif event == 'dblclick':
        pyautogui.doubleClick(x, y)
    elif event == 'rightclick':
        pyautogui.click(x, y, button='right')


@router.post('/keyboard')
@supermoon_api
async def keyboard_event(event: Literal[tuple(['text', *pyautogui.KEYBOARD_KEYS])] = Query(), text: str = Query('')):
    if event == 'text':
        pyautogui.typewrite(text)
    else:
        pyautogui.press(event)
