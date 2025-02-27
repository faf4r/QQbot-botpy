import asyncio

import psutil


def _get_disk_usage(path: str):
    try:
        return psutil.disk_usage(path)
    except Exception as e:
        print(f"Could not get disk usage for {path}: {e!r}")


def get_disk_usage():
    """Get the disk usage status."""
    disk_parts = psutil.disk_partitions()
    return {
        d.mountpoint: usage.percent
        for d in disk_parts
        if (usage := _get_disk_usage(d.mountpoint))
    }


async def get_status():
    """Get the server usage status."""
    psutil.cpu_percent()
    await asyncio.sleep(0.5)
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = get_disk_usage()
    disk = "\n".join(f"\t\t{k}\t{v}%" for k, v in disk.items())
    status_msg = f"\nCPU usage: {cpu}%\nMemory usage: {mem}%\ndisk usage: \n{disk}"
    return status_msg
