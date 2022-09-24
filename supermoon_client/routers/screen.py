import subprocess
from io import BytesIO
from typing import Literal

import numpy as np
import pyautogui
from PIL import ImageGrab
from fastapi import APIRouter, Query, HTTPException
from mss import mss, windows
from pyautogui._pyautogui_win import keyboardMapping
from starlette.responses import Response, StreamingResponse
from starlette.status import HTTP_403_FORBIDDEN

from supermoon_client.api_decorator import supermoon_api
from supermoon_client.logger import get_logger
from supermoon_client.utils import get_frames

windows.CAPTUREBLT = 0
stream_process: subprocess.Popen | None = None
screen_width, screen_height = pyautogui.size()

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


@router.post('/start_stream')
@supermoon_api
async def start_stream(fps: int = Query(16), resolution: tuple[int, int] = Query((screen_width, screen_height))):
    global stream_process
    if stream_process is not None:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='Stream process is already running')
    stream_process = subprocess.Popen([
        'ffmpeg',
        '-re',
        '-probesize', '32',
        '-framerate', f'{fps}',
        '-y',
        '-f', 'gdigrab',
        '-thread_queue_size', '64',
        '-video_size', f'{resolution[0]}x{resolution[1]}',
        '-i', 'desktop',
        '-vcodec', 'libx264',
        '-crf', '0',
        '-preset', 'ultrafast',
        '-color_range', '2',
        '-fflags', 'nobuffer',
        '-f', 'mpegts',
        'udp://localhost:8081',
    ], shell=True, stdin=subprocess.PIPE)


@router.post('/stop_stream')
@supermoon_api
async def stop_stream():
    global stream_process
    if stream_process is None:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='Stream process is not running')
    stream_process.communicate(bytes('q', 'UTF-8'))
    stream_process = None


@router.post('/mouse')
@supermoon_api
async def mouse_event(event: Literal['click', 'double', 'right'] = Query(), x: float = Query(), y: float = Query(),
                      width: float = Query(), height: float = Query()):
    # coordinates of desktop event
    x, y = screen_width * (x / width), screen_height * (y / height)
    get_logger().debug(f'Mouse event: ({x},{y})')
    # handle event
    if event == 'click':
        pyautogui.click(x, y)
    elif event == 'dblclick':
        pyautogui.doubleClick(x, y)
    elif event == 'rightclick':
        pyautogui.click(x, y, button='right')


@router.post('/keyboard')
@supermoon_api
async def keyboard_event(event: int = Query()):
    matches = [k for k, v in keyboardMapping.items() if v == event]
    if len(matches) == 0:
        get_logger().error('Bad key! found 0 matches')
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='Bad key! found 0 matches')
    key = matches[0]
    get_logger().debug(f'Key event: {key}')
    pyautogui.press(key)
