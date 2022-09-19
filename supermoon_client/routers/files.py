import os

from fastapi import APIRouter, HTTPException, Query, Body
from starlette.responses import FileResponse
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from supermoon_common.models.client.dirlist import DirlistResponse, DirlistEntry, DirlistEntryType
from supermoon_common.models.client.tree import TreeResponse, TreeDirEntry

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
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='No such directory')

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


@router.get('/tree', response_model=TreeResponse)
@supermoon_api
async def tree(root: str):
    async def get_child(entry: DirlistEntry) -> TreeDirEntry:
        if entry.type == 'dir':
            return TreeDirEntry(**entry.dict(), children=await tree(os.path.join(root, entry.name)))
        else:
            return TreeDirEntry(**entry.dict())

    return [await get_child(entry) for entry in (await dirlist(root))]


@router.get('/read')
@supermoon_api
async def read_file(path: str):
    try:
        return FileResponse(path)
    except FileNotFoundError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='File not found')
    except OSError as e:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=str(e))


@router.post('/write')
@supermoon_api
async def write_file(path: str = Query(), replace: bool = Query(default=False), content: bytes = Body()):
    if not replace and os.path.exists(path):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='File already exists')
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
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='File not found')
    except OSError as e:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=str(e))


@router.post('/move')
@supermoon_api
async def move_file(source_path: str, destination_path: str):
    try:
        os.rename(source_path, destination_path)
    except FileNotFoundError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Source path not found')
    except OSError as e:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=str(e))
