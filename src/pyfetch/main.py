"""
pyfetch - a minimal fastfetch-style system info tool
"""

import os
import re
import time
import platform
import socket
import shutil
from datetime import timedelta

import psutil


class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    WHITE = "\033[97m"
    BLACK = "\033[30m"
    YELLOW = "\033[33m"
    GREY = "\033[90m"


# Tux-inspired palette: white/grey body, yellow beak & feet
LOGO_LINES = [
    f"{C.WHITE}{C.BOLD}   .--.{C.RESET}",
    f"{C.WHITE}{C.BOLD}  |o_o |{C.RESET}",
    f"{C.WHITE}{C.BOLD}  |:_/ |{C.RESET}",
    f"{C.WHITE}{C.BOLD} //   {C.YELLOW}\\ \\{C.RESET}",
    f"{C.WHITE}{C.BOLD}(|     | ){C.RESET}",
    f"{C.YELLOW}{C.BOLD}/'\\_   _/`\\{C.RESET}",
    f"{C.YELLOW}{C.BOLD}\\___)=(___/{C.RESET}",
]

ANSI_RE = re.compile(r"\033\[[0-9;]*m")


def visible_len(s):
    """Length of a string ignoring ANSI color codes."""
    return len(ANSI_RE.sub("", s))


def get_size(bytes_val):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024:
            return f"{bytes_val:.2f}{unit}"
        bytes_val /= 1024
    return f"{bytes_val:.2f}PB"


def get_uptime():
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    return str(timedelta(seconds=int(uptime_seconds)))


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "N/A"
    finally:
        s.close()
    return ip


def get_info():
    user = platform.node()
    os_name = f"{platform.system()} {platform.release()}"
    kernel = platform.release()

    shell_path = os.environ.get("SHELL", "unknown")
    shell = shell_path.split("/")[-1] if shell_path != "unknown" else "unknown"

    cpu = platform.processor() or "Unknown CPU"
    cpu_cores = psutil.cpu_count(logical=True)
    cpu_freq = psutil.cpu_freq()
    cpu_str = (
        f"{cpu} ({cpu_cores}) @ {cpu_freq.current / 1000:.2f} GHz"
        if cpu_freq else f"{cpu} ({cpu_cores})"
    )

    mem = psutil.virtual_memory()
    mem_str = f"{get_size(mem.used)} / {get_size(mem.total)} ({mem.percent}%)"

    disk = psutil.disk_usage(os.path.abspath(os.sep))
    disk_str = f"{get_size(disk.used)} / {get_size(disk.total)} ({disk.percent}%)"

    local_ip = get_local_ip()

    battery_str = "N/A"
    if hasattr(psutil, "sensors_battery"):
        batt = psutil.sensors_battery()
        if batt:
            status = "Charging" if batt.power_plugged else "Discharging"
            battery_str = f"{int(batt.percent)}% [{status}]"

    term_size = shutil.get_terminal_size()

    return {
        "User": user,
        "OS": os_name,
        "Kernel": kernel,
        "Shell": shell,
        "Uptime": get_uptime(),
        "CPU": cpu_str,
        "Memory": mem_str,
        "Disk (/)": disk_str,
        "Local IP": local_ip,
        "Battery": battery_str,
        "Terminal Size": f"{term_size.columns}x{term_size.lines}",
    }


def print_fetch():
    info = get_info()
    labels = list(info.keys())
    values = list(info.values())

    label_width = max(len(label) for label in labels)

    logo_width = max(visible_len(line) for line in LOGO_LINES)

    max_rows = max(len(LOGO_LINES), len(labels))

    for i in range(max_rows):
        if i < len(LOGO_LINES):
            line = LOGO_LINES[i]
            pad = logo_width - visible_len(line)
            left = line + (" " * pad)
        else:
            left = " " * logo_width

        if i < len(labels):
            label = labels[i].ljust(label_width)
            right = f"{C.BOLD}{C.YELLOW}{label}{C.RESET} : {values[i]}"
        else:
            right = ""

        print(f"{left}   {right}")


def main():
    print_fetch()


if __name__ == "__main__":
    main()