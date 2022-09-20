import os

from fastapi import APIRouter, HTTPException, Query, Body
from starlette.responses import FileResponse
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from supermoon_common.models.client.dirlist import DirlistResponse, DirlistEntry, DirlistEntryType

from supermoon_client.api_decorator import supermoon_api

router = APIRouter(
    prefix='/files',
    tags=['Files']
)


@router.get('/dirlist', response_model=DirlistResponse)
@supermoon_api
async def dirlist(directory: str) -> list[DirlistEntry]:
    def get_type(entry: os.DirEntry) -> DirlistEntryType:
        if entry.is_symlink():
            return 'symlink'
        if entry.is_file():
            return 'file'
        if entry.is_dir():
            return 'dir'

    try:
        entries: list[os.DirEntry] = list(os.scandir(directory))
    except FileNotFoundError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f'Directory at {directory} could not be found')
    except NotADirectoryError:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=f'{directory} is not a directory')

    return [DirlistEntry(
        name=entry.name,
        type=get_type(entry),
        mode=entry.stat().st_mode,
        owner=entry.stat().st_uid,
        group=entry.stat().st_uid,
        device=entry.stat().st_dev,
        access_time=entry.stat().st_atime,
        modification_time=entry.stat().st_mtime,
        creation_time=entry.stat().st_ctime,
        size=entry.stat().st_size,
    ) for entry in entries]


@router.get('/read')
@supermoon_api
async def read_file(path: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f'File at {path} could not be found')
    if not os.path.isfile(path):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=f'{path} is not a file')
    try:
        return FileResponse(path)
    except OSError as e:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=str(e))


@router.post('/write')
@supermoon_api
async def write_file(path: str = Query(), replace: bool = Query(default=False), content: bytes = Body()):
    if not replace and os.path.exists(path):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN,
                            detail=f'File at {path} already exists (set replace=true to override)')
    try:
        with open(path, 'wb') as file:
            file.write(content)
    except OSError as e:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=str(e))


@router.delete('/delete')
@supermoon_api
async def delete_file(path: str):
    try:
        os.remove(path)
    except FileNotFoundError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f'File at {path} could not be found')
    except OSError as e:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=str(e))


@router.post('/move')
@supermoon_api
async def move_file(source_path: str, destination_path: str):
    try:
        os.rename(source_path, destination_path)
    except FileNotFoundError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f'Source file at {source_path} could not be found')
    except OSError as e:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=str(e))
