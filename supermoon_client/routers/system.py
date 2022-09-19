import platform
from datetime import datetime

import psutil
from fastapi import APIRouter
from supermoon_common.models.client.connections import ConnectionsResponse, Address, Connection
from supermoon_common.models.client.info import InfoResponse, System, CPUFrequency, CPU, Memory, PartitionUsage, Disk, \
    Partition, Network, NetworkAddress, Battery
from supermoon_common.models.client.process_list import ProcessListResponse, Process

from supermoon_client.api_decorator import supermoon_api

router = APIRouter(
    prefix='/system',
    tags=['System']
)


@router.get('/process_list', response_model=ProcessListResponse)
@supermoon_api
async def process_list():
    return [Process(**process.as_dict([
        'pid', 'memory_percent', 'name', 'cmdline', 'create_time', 'nice', 'username', 'cwd', 'cpu_percent',
        'num_handles', 'environ', 'ppid', 'exe'
    ])) for process in psutil.process_iter()]


@router.get('/info', response_model=InfoResponse)
@supermoon_api
async def info():
    # system
    uname = platform.uname()
    system = System(
        system=uname.system,
        node=uname.node,
        release=uname.release,
        version=uname.version,
        machine=uname.machine,
        processor=uname.processor,
    )

    # boot time
    boot_time_timestamp = psutil.boot_time()
    boot_time = datetime.fromtimestamp(boot_time_timestamp)

    # cpu
    cpufreq = psutil.cpu_freq()
    frequency = CPUFrequency(max=cpufreq.max, min=cpufreq.min, current=cpufreq.current)
    cpu = CPU(
        physical_cores=psutil.cpu_count(logical=False),
        total_cores=psutil.cpu_count(logical=True),
        frequency=frequency,
        usage=psutil.cpu_percent(interval=1),
        core_usage=psutil.cpu_percent(percpu=True, interval=1),
    )

    # memory
    virtual_memory = psutil.virtual_memory()
    memory = Memory(
        total=virtual_memory.total,
        available=virtual_memory.available,
        used=virtual_memory.used,
        percent=virtual_memory.percent,
    )

    # disk
    def disk_usage(partition):
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            return PartitionUsage(
                total=usage.total,
                used=usage.used,
                free=usage.free,
                percent=usage.percent
            )
        except PermissionError:
            return None

    disk_io = psutil.disk_io_counters()
    disk = Disk(
        partitions=[Partition(
            device=partition.device,
            mountpoint=partition.mountpoint,
            fstype=partition.fstype,
            usage=disk_usage(partition)
        ) for partition in psutil.disk_partitions()],
        read_bytes=disk_io.read_bytes,
        write_bytes=disk_io.write_bytes,
    )

    net_io = psutil.net_io_counters()
    network = Network(
        interfaces=[{
            interface_name: [NetworkAddress(
                family=address.family.name,
                address=address.address,
                netmask=address.netmask,
            ) for address in interface_addresses]
        } for interface_name, interface_addresses in psutil.net_if_addrs().items()],
        bytes_sent=net_io.bytes_sent,
        bytes_recv=net_io.bytes_recv,
    )

    sensors_battery = psutil.sensors_battery()
    battery = Battery(
        percent=sensors_battery.percent,
        secsleft=sensors_battery.secsleft,
        power_plugged=sensors_battery.power_plugged
    ) if sensors_battery else None

    users = [user.name for user in psutil.users()]

    return InfoResponse(
        system=system,
        boot_time=boot_time,
        cpu=cpu,
        memory=memory,
        disk=disk,
        network=network,
        battery=battery,
        users=users,
    )


@router.get('/connections', response_model=ConnectionsResponse)
@supermoon_api
async def connections():
    def get_address(address: tuple[str, int] | tuple[...] | str):
        if isinstance(address, str):
            return address
        if isinstance(address, tuple) and len(address) == 2:
            return Address(host=address[0], port=address[1])
        return None

    return [Connection(
        family=connection.family.name,
        type=connection.type.name,
        pid=connection.pid,
        status=connection.status,
        local_address=get_address(connection.laddr),
        remote_address=get_address(connection.raddr),
    ) for connection in psutil.net_connections()]
