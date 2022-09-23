from supermoon_client.communication_methods import CommunicationMethod

# Logging
LOGGER_NAME = 'supermoon'
LOG_FILE_NAME = 'log.txt'

# General
EXECUTABLE_NAME = 'main.exe'
STARTUP_SCRIPT_NAME = 'open.bat'
EXE_REMOVAL_TIME = 2  # seconds
COMMUNICATION_METHOD = CommunicationMethod.SERVER

# Server
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8080

# Polling
INITIAL_POLL_INTERVAL = 60  # seconds
SERVER_GET_REQUEST_URL = 'http://moonitor:16703/request'
SERVER_SEND_RESPONSE_URL = 'http://moonitor:16703/request'
