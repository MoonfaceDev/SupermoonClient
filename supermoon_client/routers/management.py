import os
from logging.handlers import TimedRotatingFileHandler

from fastapi import APIRouter, HTTPException, Query, UploadFile
from starlette.background import BackgroundTasks
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
async def get_log():
    if not os.path.isfile(LOG_FILE_NAME):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f'Log file could not be found')
    try:
        return FileResponse(LOG_FILE_NAME)
    except OSError as e:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=str(e))


@router.delete('/clear_log')
@supermoon_api
async def clear_log():
    for handler in get_logger().handlers:
        if isinstance(handler, TimedRotatingFileHandler):
            handler.doRollover()


async def suicide():
    os.system(f'taskkill /F /PID {os.getpid()}')


@router.post('/remove_client')
@supermoon_api
async def remove_client(background_tasks: BackgroundTasks):
    bat_path = os.path.join(
        rf'C:\Users\{os.getlogin()}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup',
        STARTUP_SCRIPT_NAME
    )
    try:
        os.remove(bat_path)
    except Exception as e:
        get_logger().exception(e)
    executable = os.path.join(os.getcwd(), EXECUTABLE_NAME)
    os.system(f'start /min cmd /c "timeout {EXE_REMOVAL_TIME} & del "{os.path.join(os.getcwd(), LOG_FILE_NAME)}" & del "{executable}""')
    background_tasks.add_task(suicide)


@router.post('/update_client')
@supermoon_api
async def update_client(background_tasks: BackgroundTasks, content: UploadFile, path: str = Query(default=os.getcwd())):
    old_executable = os.path.join(os.getcwd(), EXECUTABLE_NAME)
    new_executable = os.path.join(path, EXECUTABLE_NAME)
    with open(new_executable + '.tmp', 'wb') as file:
        file.write(await content.read())
    os.system(f'start /min cmd /c "timeout {EXE_REMOVAL_TIME} & '
              f'del "{old_executable}" & '
              f'move "{new_executable}.tmp" "{new_executable}" & '
              f'cd {path} & '
              f'start "" "{EXECUTABLE_NAME}""')
    background_tasks.add_task(suicide)


@router.post('/stop_process')
@supermoon_api
async def stop_process(background_tasks: BackgroundTasks):
    background_tasks.add_task(suicide)
