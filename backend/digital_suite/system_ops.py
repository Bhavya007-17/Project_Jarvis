"""
System Ops (Module D – Sentinel): CPU, RAM, battery, process list/kill.
Uses psutil for local diagnostics; no API key required.
"""

import psutil
from typing import Optional


def get_system_status() -> dict:
    """
    Returns a summary of system health: CPU, RAM, battery (if present).
    GPU temperature may not be available on all systems (platform-specific).
    """
    cpu_percent = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    status = {
        "cpu_percent": round(cpu_percent, 1),
        "ram_percent": round(mem.percent, 1),
        "ram_used_gb": round(mem.used / (1024**3), 2),
        "ram_total_gb": round(mem.total / (1024**3), 2),
        "battery": None,
        "gpu_note": None,
    }

    # Battery (laptops)
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            status["battery"] = "No battery (desktop)"
        else:
            pct = battery.percent
            status["battery"] = f"{pct}%"
            if battery.power_plugged:
                status["battery"] += " (plugged in)"
            else:
                status["battery"] += " (on battery)"
    except Exception:
        status["battery"] = "Unknown"

    # Optional: try GPU temp (platform-dependent; psutil doesn't provide GPU temp on Windows by default)
    try:
        import subprocess
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0 and result.stdout.strip():
            gpu_temp = result.stdout.strip().split("\n")[0].strip()
            status["gpu_temp_c"] = gpu_temp
            status["gpu_note"] = f"GPU temp: {gpu_temp}°C"
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        status["gpu_note"] = "GPU temp not available (nvidia-smi not found or unsupported)"

    return status


def format_system_status_for_speech(status: dict) -> str:
    """Turn status dict into a short sentence for the assistant to speak."""
    parts = [
        f"CPU at {status['cpu_percent']}%",
        f"RAM at {status['ram_percent']}% ({status['ram_used_gb']} of {status['ram_total_gb']} GB used)",
    ]
    if status.get("battery"):
        parts.append(f"Battery: {status['battery']}")
    if status.get("gpu_note") and "temp" in status["gpu_note"].lower():
        parts.append(status["gpu_note"])
    return ". ".join(parts)


def list_top_processes(n: int = 10) -> list[dict]:
    """Return top N processes by CPU usage (for 'what's using CPU' / 'kill that process' context)."""
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent"]):
        try:
            pinfo = p.info
            cpu = p.cpu_percent()
            if cpu is not None and cpu > 0:
                procs.append({
                    "pid": pinfo.get("pid"),
                    "name": pinfo.get("name") or "unknown",
                    "cpu_percent": round(cpu, 1),
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    procs.sort(key=lambda x: x["cpu_percent"], reverse=True)
    return procs[:n]


def kill_process_by_name(name_substring: str) -> tuple[bool, str]:
    """
    Try to kill processes whose name contains the given substring.
    Returns (success, message). Use with care; may require elevated privileges for system processes.
    """
    killed = []
    for p in psutil.process_iter(["pid", "name"]):
        try:
            if name_substring.lower() in (p.info.get("name") or "").lower():
                proc = psutil.Process(p.info["pid"])
                proc.terminate()
                killed.append(f"{p.info['name']} (PID {p.info['pid']})")
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            continue
    if killed:
        return True, f"Terminated: {', '.join(killed)}"
    return False, f"No process matching '{name_substring}' found or could not terminate."


def kill_process_by_pid(pid: int) -> tuple[bool, str]:
    """Kill a single process by PID."""
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        return True, f"Terminated process {pid} ({proc.name()})."
    except psutil.NoSuchProcess:
        return False, f"Process {pid} does not exist."
    except psutil.AccessDenied:
        return False, f"Access denied to terminate process {pid}."
