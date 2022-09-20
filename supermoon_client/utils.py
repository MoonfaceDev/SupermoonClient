import time
from multiprocessing import Process
from typing import Callable, Iterator

import cv2
import numpy as np
from playsound import playsound

audio_process: Process | None = None


def get_frames(get_image: Callable[[], np.ndarray], fps: float, resolution: tuple[int, int]) -> Iterator[bytes]:
    while True:
        start_time = time.time()
        frame = get_image()
        frame = cv2.resize(frame, resolution)
        ret, jpeg = cv2.imencode('.jpg', frame)
        buffer = jpeg.tobytes()
        yield f'--frame\r\n' \
              f'Content-Type: image/jpeg\r\n' \
              f'Cache-Control: no-cache\r\n' \
              f'Content-length: {len(buffer)}\r\n' \
              f'\r\n'.encode() + buffer
        time_elapsed = time.time() - start_time
        time.sleep(max([0, 1 / fps - time_elapsed]))


def play_sound(path: str, wait: bool = True):
    global audio_process
    audio_process = Process(target=playsound, args=(path,))
    audio_process.start()
    if wait:
        audio_process.join()


def stop_sound():
    global audio_process
    audio_process.terminate()
    audio_process.join()
