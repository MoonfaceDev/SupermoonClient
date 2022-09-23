import os

import uvicorn

from supermoon_client.app import app
from supermoon_client.communication_methods import CommunicationMethod
from supermoon_client.consts import STARTUP_SCRIPT_NAME, EXECUTABLE_NAME, SERVER_HOST, \
    SERVER_PORT, COMMUNICATION_METHOD
from supermoon_client.logger import get_logger
from supermoon_client.poll_client import start_polling


def enable_firewall(executable: str):
    # Requires admin
    try:
        os.system(
            f'netsh advfirewall firewall add rule name="main" program="{executable}" dir=in action=allow protocol=TCP')
        os.system(
            f'netsh advfirewall firewall add rule name="main" program="{executable}" dir=in action=allow protocol=UDP')
    except Exception as e:
        get_logger().exception(e)


def add_to_startup(executable: str):
    bat_path = os.path.join(
        rf'C:\Users\{os.getlogin()}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup',
        STARTUP_SCRIPT_NAME
    )
    try:
        with open(bat_path, "w+") as bat_file:
            bat_file.write(rf'cd {os.getcwd()} & start "" "{executable}"')
    except Exception as e:
        get_logger().exception(e)


def main():
    executable = os.path.join(os.getcwd(), EXECUTABLE_NAME)
    add_to_startup(executable)

    if COMMUNICATION_METHOD == CommunicationMethod.SERVER:
        enable_firewall(executable)
        uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)
    elif COMMUNICATION_METHOD == CommunicationMethod.POLL:
        start_polling()
