from setuptools import setup, find_packages

setup(
    name='supermoon_client',
    version='0.1.0',
    author='Elai Corem',
    description='Supermoon client for Windows 10',
    url='https://github.com/MoonfaceDev',
    python_requires='>=3.10, <4',
    packages=find_packages(include=['supermoon_client', 'supermoon_client.*']),
    install_requires=[
        'fastapi~=0.85.0',
        'starlette~=0.20.4',
        'uvicorn~=0.18.3',
        'pyautogui~=0.9.53',
        'Pillow~=9.2.0',
        'websockets~=10.3',
        'psutil~=5.9.2',
        'browser-history~=0.3.2',
        'pycaw==20220416',
        'numpy~=1.23.3',
        'opencv-python~=4.6.0.66',
        'mss~=6.1.0',
        'pyaudio~=0.2.12',
        'python-multipart~=0.0.5',
        'playsound==1.2.2',
        'requests~=2.28.1',
        'supermoon_common~=0.1.0'
    ],
    entry_points={
        'console': [
            'supermoon=supermoon_client.main:main',
        ]
    }
)
