"""
System monitor: CPU and memory usage for Dashboard tab.
Uses psutil for cross-platform stats.
"""

try:
    import psutil
except ImportError:
    psutil = None


def get_system_stats():
    """
    Return current CPU and memory usage.
    :return: dict with cpu_percent, memory_percent, memory_used_gb, memory_total_gb, or error
    """
    if psutil is None:
        return {
            "ok": False,
            "error": "psutil not installed",
            "cpu_percent": 0,
            "memory_percent": 0,
            "memory_used_gb": 0,
            "memory_total_gb": 0,
        }
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        memory_percent = mem.percent
        memory_used_gb = round(mem.used / (1024 ** 3), 2)
        memory_total_gb = round(mem.total / (1024 ** 3), 2)
        return {
            "ok": True,
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "memory_used_gb": memory_used_gb,
            "memory_total_gb": memory_total_gb,
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "cpu_percent": 0,
            "memory_percent": 0,
            "memory_used_gb": 0,
            "memory_total_gb": 0,
        }
