import base64
import os
import tempfile

import cv2
import pyaudio
from fastapi import APIRouter, Query
from playsound import playsound
from pycaw.api.audioclient import ISimpleAudioVolume
from pycaw.api.endpointvolume import IAudioEndpointVolume
from pycaw.utils import AudioUtilities
from starlette.background import BackgroundTasks
from starlette.responses import StreamingResponse
from supermoon_common.models.client.play_audio import PlayAudioBufferRequest

from supermoon_client.api_decorator import supermoon_api
from supermoon_client.utils import get_frames

router = APIRouter(
    prefix='/devices',
    tags=['Devices']
)


@router.post('/set_volume')
@supermoon_api
async def set_volume(level: float = Query(ge=0, le=1)):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        volume: IAudioEndpointVolume = session._ctl.QueryInterface(ISimpleAudioVolume)
        volume.SetMasterVolume(level, None)


@router.post('/play_audio_file')
@supermoon_api
async def play_audio_file(path: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(playsound, path)


@router.post('/play_audio_buffer')
@supermoon_api
async def play_audio_buffer(request: PlayAudioBufferRequest, background_tasks: BackgroundTasks):
    with tempfile.NamedTemporaryFile(suffix=f'.{request.type}', delete=False) as file:
        file.write(base64.b64decode(request.data))

    def play_and_remove(path: str):
        playsound(path)
        os.remove(path)

    background_tasks.add_task(play_and_remove, file.name)


@router.get('/camera')
@supermoon_api
async def camera(fps: float = Query(24), resolution: tuple[int, int] = Query((1920, 1080)),
                 camera_index: int = Query(0)):
    capture = cv2.VideoCapture(camera_index)

    def get_image():
        _, frame = capture.read()
        return frame

    return StreamingResponse(get_frames(get_image=get_image, fps=fps, resolution=resolution),
                             media_type='multipart/x-mixed-replace; boundary=--frame')


FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
BITS_PER_SAMPLE = 16


@router.get('/microphone')
@supermoon_api
async def microphone():
    def get_header(sample_rate: int, bits_per_sample: int, channels: int):
        datasize = 2000 * 10 ** 6
        o = bytes("RIFF", 'ascii')  # (4byte) Marks file as RIFF
        o += (datasize + 36).to_bytes(4, 'little')  # (4byte) File size in bytes excluding this and RIFF marker
        o += bytes("WAVE", 'ascii')  # (4byte) File type
        o += bytes("fmt ", 'ascii')  # (4byte) Format Chunk Marker
        o += (16).to_bytes(4, 'little')  # (4byte) Length of above format data
        o += (1).to_bytes(2, 'little')  # (2byte) Format type (1 - PCM)
        o += channels.to_bytes(2, 'little')  # (2byte)
        o += sample_rate.to_bytes(4, 'little')  # (4byte)
        o += (sample_rate * channels * bits_per_sample // 8).to_bytes(4, 'little')  # (4byte)
        o += (channels * bits_per_sample // 8).to_bytes(2, 'little')  # (2byte)
        o += bits_per_sample.to_bytes(2, 'little')  # (2byte)
        o += bytes("data", 'ascii')  # (4byte) Data Chunk Marker
        o += datasize.to_bytes(4, 'little')  # (4byte) Data size in bytes
        return o

    def sound():
        wav_header = get_header(RATE, BITS_PER_SAMPLE, CHANNELS)

        stream = audio1.open(format=FORMAT, channels=CHANNELS,
                             rate=RATE, input=True, input_device_index=1,
                             frames_per_buffer=CHUNK)
        first_run = True
        while True:
            if first_run:
                data = wav_header + stream.read(CHUNK)
                first_run = False
            else:
                data = stream.read(CHUNK)
            yield data

    audio1 = pyaudio.PyAudio()

    return StreamingResponse(sound(), media_type='audio/wav')
