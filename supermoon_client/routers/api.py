from fastapi import APIRouter

from supermoon_client.routers.devices import router as devices
from supermoon_client.routers.files import router as files
from supermoon_client.routers.misc import router as misc
from supermoon_client.routers.management import router as management
from supermoon_client.routers.screen import router as screen
from supermoon_client.routers.shell import router as shell
from supermoon_client.routers.system import router as system

router = APIRouter(
    prefix='/api'
)

router.include_router(devices)
router.include_router(files)
router.include_router(management)
router.include_router(misc)
router.include_router(screen)
router.include_router(shell)
router.include_router(system)
