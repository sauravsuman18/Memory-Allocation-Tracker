# monitor.py
import psutil

def get_processes_info():
    process_list = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            mem = proc.info['memory_info'].rss / (1024 * 1024)  # in MB
            process_list.append({
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'memory': round(mem, 2)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return sorted(process_list, key=lambda x: x['memory'], reverse=True)
