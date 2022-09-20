import os
import subprocess
import sys

from fastapi import APIRouter, HTTPException
from starlette.responses import FileResponse
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN

from supermoon_client.api_decorator import supermoon_api
from supermoon_client.consts import LOG_FILE_NAME, EXECUTABLE_NAME, STARTUP_SCRIPT_NAME, EXE_REMOVAL_TIME
from supermoon_client.logger import get_logger

router = APIRouter(
    prefix='/management',
    tags=['Management']
)


@router.get('/log')
@supermoon_api
def get_log():
    if not os.path.isfile(LOG_FILE_NAME):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f'Log file could not be found')
    try:
        return FileResponse(LOG_FILE_NAME)
    except OSError as e:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=str(e))


@router.post('/remove_client')
def remove_client():
    bat_path = os.path.join(
        rf'C:\Users\{os.getlogin()}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup',
        STARTUP_SCRIPT_NAME
    )
    try:
        os.remove(bat_path)
    except Exception as e:
        get_logger().exception(e)
    try:
        os.remove(LOG_FILE_NAME)
    except Exception as e:
        print(e)
    executable = os.path.join(os.getcwd(), EXECUTABLE_NAME)
    subprocess.Popen(f"python -c \"import os, time; time.sleep({EXE_REMOVAL_TIME}); os.remove('{executable}');\"")
    sys.exit(0)


@router.post('/stop_process')
@supermoon_api
def stop_process():
    sys.exit(0)
