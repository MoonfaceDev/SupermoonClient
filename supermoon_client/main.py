import logging
import os

import uvicorn

from supermoon_client.app import app


def main():
    try:
        logging.basicConfig(level=logging.DEBUG)
        file_handler = logging.FileHandler('log.txt')
        file_handler.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(file_handler)
        logging.getLogger('supermoon').addHandler(file_handler)
    except Exception as e:
        print(e)

    executable = os.getcwd() + '\\main.exe'
    os.system(
        f'netsh advfirewall firewall add rule name="main" program="{executable}" dir=in action=allow protocol=TCP')
    os.system(
        f'netsh advfirewall firewall add rule name="main" program="{executable}" dir=in action=allow protocol=UDP')

    bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % os.getlogin()
    with open(bat_path + '\\' + "open.bat", "w+") as bat_file:
        bat_file.write(rf'cd {os.getcwd()} & start "" "%s"' % executable)

    uvicorn.run(app, host='0.0.0.0', port=8080)
