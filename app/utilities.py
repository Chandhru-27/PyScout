from datetime import datetime, timedelta
from app_logger import logger
import threading
import time
import json
import sys
import os

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# with open(os.path.join(BASE_DIR, "app", "config.json"), 'r', encoding='utf-8') as f:
#     config = json.load(f)

with open(os.path.join(BASE_DIR,'config.json') , 'r' , encoding='utf-8') as f:
    config = json.load(f)
    
APP_VERSION = config["app_version"]
UPDATE_MANIFEST_URL = config["update_manifest_url"]


""" Global application shutdown event (used by timers/trackers)."""
shutdown_event = threading.Event()

"""Dedicated shutdown for app blocker threads only."""
app_blocker_shutdown_event = threading.Event()

app_blocker_threads = []

class Utility:
    """Collection of system utilities for activity tracking and app/URL blocking."""
    audio_lock = threading.Lock()
    
    @staticmethod
    def add_to_startup(app_name="PyScout", exe_path=None):
        import winreg
        if exe_path is None:
            exe_path = sys.executable  
        key = winreg.HKEY_CURRENT_USER
        key_val = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(key, key_val, 0, winreg.KEY_SET_VALUE) as registry_key:
            winreg.SetValueEx(registry_key, app_name, 0, winreg.REG_SZ, exe_path)

    @staticmethod
    def check_for_updates():
        try:
            import requests
            response = requests.get(UPDATE_MANIFEST_URL , timeout=2)
            response.raise_for_status()
            latest_config = response.json()
            
            if 'app_version' not in latest_config or 'update_manifest_url' not in latest_config:
                logger.error("Missing required manifest key.")
                return None
            
            from packaging import version
            if version.parse(latest_config["app_version"]) > version.parse(APP_VERSION):
                return latest_config["update_manifest_url"]
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while checking for update: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in update manifest: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while checking for update: {e}")
        return None

    @staticmethod
    def download_latest_version(url):
        import tempfile
        import requests
        try:
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir,'PyScoutUpdate.exe')
            with requests.get(url , stream=True) as r:
                r.raise_for_status()
                with open(temp_path , "wb") as f:
                    for chunk in r.iter_content(8192):
                        f.write(chunk)
            return temp_path
        except Exception as e:
            logger.exception("Unable to download latest version.")

    @staticmethod
    def get_idle_time():
        """Return user idle time in seconds using Windows APIs."""
        import ctypes
        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

        lii = LASTINPUTINFO()
        lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
        ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
        millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
        return millis / 1000.0
    
    def get_formatted_screen_time(arg):
        """
        Converts total screen time in seconds to HH:MM:SS format.
        """
        return str(timedelta(seconds=int(arg)))

    @staticmethod
    def get_active_window_title():
        """Return process name of the foreground window (lower-level via Win32)."""
        import win32process
        import win32gui
        import psutil
        handle = win32gui.GetForegroundWindow()
        try:
            _,process_id = win32process.GetWindowThreadProcessId(handle)
            process_obj = psutil.Process(pid=process_id)
            return process_obj.name()
        except Exception:
            return 'Unknow'

    @staticmethod
    def get_installed_apps():
        """Enumerate installed applications from common registry locations."""
        apps = set()
        reg_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]

        for reg_path in reg_paths:
            try:
                import winreg
                reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                for i in range(0, winreg.QueryInfoKey(reg_key)[0]):
                    sub_key_name = winreg.EnumKey(reg_key, i)
                    sub_key = winreg.OpenKey(reg_key, sub_key_name)
                    try:
                        app_name, _ = winreg.QueryValueEx(sub_key, "DisplayName")
                        apps.add(app_name)
                    except FileNotFoundError:
                        continue
            except Exception:
                continue

        return sorted(apps)

    @staticmethod
    def get_active_audio_status():
        """Return True if there is any active audio session with non-zero volume."""
        with Utility.audio_lock:
            import comtypes
            from comtypes import CoInitialize, CoUninitialize
            try:
                CoInitialize()
            except Exception:
                pass 
            from pycaw.pycaw import AudioUtilities
            try:
                sessions = AudioUtilities.GetAllSessions()
                for session in sessions:
                    try:
                        volume = session.SimpleAudioVolume
                        if session.State == 1: 
                            level = volume.GetMasterVolume()
                            if level > 0.0:
                                return True
                    except Exception:
                        continue
                return False
            finally:
                try:
                    CoUninitialize()
                except Exception:
                    pass

    @staticmethod
    def terminate_blocked_app(process_name, blocked_apps):
        """Terminate a process by name if it is present in the blocked set."""
        try:
            if process_name in blocked_apps:
                import psutil
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'] == process_name:
                        proc.kill()
                logger.info(f"Terminated blocked app {process_name}")
        except Exception as e:
            logger.error(f"Failed to terminate blocked app {process_name}: {e}")

    @staticmethod
    def kill_process_tree(pid):
        """Kill a process and all of its child processes by PID."""
        import psutil
        try:
            parent = psutil.Process(pid)
            for child in parent.children(recursive=True):
                try:
                    child.kill()
                except psutil.NoSuchProcess:
                    pass
            parent.kill()
        except psutil.NoSuchProcess:
            pass
        except psutil.AccessDenied:
            logger.debug(f"Access denied for PID {pid} - try running as admin.")

    @staticmethod
    def background_scanner(blocked_apps: set, scan_interval: int = 5):
        """Scan processes periodically and kill those matching blocked apps (fast shutdown)."""
        import psutil
        while not app_blocker_shutdown_event.is_set():
            try:
                for proc in psutil.process_iter(['name', 'pid']):
                    if app_blocker_shutdown_event.is_set():
                        break
                    try:
                        proc_name = proc.info['name']
                        if proc_name and proc_name.lower() in blocked_apps:
                            logger.info(f"[SCAN] Blocking {proc_name} (PID: {proc.info['pid']})")
                            Utility.kill_process_tree(proc.info['pid'])
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                for _ in range(scan_interval):
                    if app_blocker_shutdown_event.is_set():
                        break
                    time.sleep(5)
            except Exception as e:
                logger.error(f"[SCAN] Unexpected error: {e}", exc_info=True)
                if app_blocker_shutdown_event.is_set():
                    break

    @staticmethod
    def wmi_event_watcher(blocked_apps: set):
        """Watch process creation events and terminate newly started blocked apps."""
        import pythoncom
        import wmi
        pythoncom.CoInitialize()
        try:
            while not app_blocker_shutdown_event.is_set():
                try:
                    c = wmi.WMI()
                    watcher = c.Win32_Process.watch_for("creation")

                    while not app_blocker_shutdown_event.is_set():
                        try:
                            new_proc = watcher(timeout_ms=1000)

                            if new_proc and new_proc.Name.lower() in blocked_apps:
                                logger.info(f"Blocking {new_proc.Name} (PID: {new_proc.ProcessId})")
                                Utility.kill_process_tree(new_proc.ProcessId)

                        except wmi.x_wmi as e:
                            if "timed out" in str(e):
                                continue 
                            else:
                                break 

                        except Exception as e:
                            logger.error(f"[WMI] Unexpected error: {e}", exc_info=True)
                            break

                except Exception as e:
                    logger.error(f"[WMI] Connection failed: {e}")
                    if app_blocker_shutdown_event.is_set():
                        break
                    time.sleep(5) 

        finally:
            pythoncom.CoUninitialize()

    @staticmethod
    def start_app_blocker(blocked_apps: set, scan_interval: int = 5 ):
        """Start both background scanner and WMI watcher for the given blocked apps."""
        global app_blocker_threads
        if not blocked_apps:
            return  
        
        app_blocker_shutdown_event.clear()
        t1 = threading.Thread(target=Utility.background_scanner, args=(blocked_apps, scan_interval), daemon=True)
        t2 = threading.Thread(target=Utility.wmi_event_watcher, args=(blocked_apps,), daemon=True)

        t1.start()
        t2.start()

        app_blocker_threads = [t1 , t2]
        logger.info(f"App blocker started for: {', '.join(blocked_apps)}")

    @staticmethod
    def stop_app_blocker():
        """Stop app blocker threads and reset internal state safely."""
        global app_blocker_threads
        if not app_blocker_threads:
            return

        app_blocker_shutdown_event.set()

        def join_threads():
            for thread in app_blocker_threads:
                if thread.is_alive():
                    thread.join(timeout=5) 
            logger.info("App blocker threads stopped.")

        threading.Thread(target=join_threads, daemon=True).start()
        app_blocker_threads = []
    
    @staticmethod
    def block_url(HOST_PATH , website):
        """Append a hosts-file entry for the given website if not already present."""
        try:
            with open(HOST_PATH , 'r+') as file:
                file_data = file.read()
                if website not in file_data:
                    file.write(f"128.0.0.1 {website}\n")
                    file.write(f"128.0.0.1 www.{website}\n")
                    logger.info(f"Written to host file and blocked {website}")
        except Exception as e:
            logger.error("Error opening host file and Blocking website")
        
    @staticmethod
    def clean_hosts_file(HOST_PATH: str, BLOCKED_DOMAIN: str):
        """Remove lines containing the domain from hosts file to unblock it."""
        try:
            with open(HOST_PATH, 'r') as file:
                lines = file.readlines()

            new_lines = [line for line in lines if BLOCKED_DOMAIN not in line]

            with open(HOST_PATH, 'w') as file:
                file.writelines(new_lines)

            logger.info(f"[+] '{BLOCKED_DOMAIN}' removed from hosts file.")
        except PermissionError:
            logger.warning("[-] Permission denied: Run this script as administrator.")
            pass
        except Exception as e:
            logger.error(f"[-] Error cleaning hosts file: {e}")
            pass
    
   
    @staticmethod
    def restart_dns_service():
        import subprocess
        """Restart the Windows DNS Client service to apply hosts changes."""
        try:
            subprocess.run(["net", "stop", "dnscache"], check=True)
            subprocess.run(["net", "start", "dnscache"], check=True)
            logger.info("[+] DNS Client service restarted.")
        except subprocess.CalledProcessError:
            logger.error("[-] Could not restart DNS Client (might require reboot or higher privileges).")

    @staticmethod
    def flush_dns():
        import subprocess
        """Flush DNS cache to apply hosts changes immediately."""
        try:
            subprocess.run(["ipconfig", "/flushdns"], check=True)
            logger.info("[+] DNS cache flushed.")
        except subprocess.CalledProcessError as e:
            logger.info(f"[-] Failed to flush DNS: {e}")
        
    @staticmethod
    def is_admin():
        """Return True if the process has administrative privileges."""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    
    @staticmethod
    def is_notification_disabled():
        import winreg
        """Return True/False if Windows toast notifications are disabled; None if unknown."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\PushNotifications"
            )
            value , _ = winreg.QueryValueEx(key , "ToastEnabled")
            winreg.CloseKey(key)
            return value == 0
        except FileNotFoundError:
            return None
    
    @staticmethod
    def is_focus_assist_on():
        import winreg
        """Return True/False if Focus Assist is active; None if unknown."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\PushNotifications"
            )
            value , _ = winreg.QueryValueEx(key , "QuietHoursActive")
            winreg.CloseKey(key)
            return value == 1
        except FileNotFoundError:
            return None

    @staticmethod
    def run_precise_timer(interval: float, func: callable, *args, **kwargs):
        """High-precision timer that passes detected sleep/idle gaps to the callback."""
        next_time = time.time()
        last_real_time = datetime.now() 

        while not shutdown_event.is_set():
            try:
                now_real = datetime.now()
                gap_seconds = (now_real - last_real_time).total_seconds()
                last_real_time = now_real

                func(*args, gap_seconds=gap_seconds, **kwargs)

                next_time += interval
                sleep_time = next_time - time.time()

                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    next_time = time.time()

            except Exception as e:
                logger.error(f"Precise timer crashed: {e}", exc_info=True)
                if shutdown_event.is_set():
                    return
                time.sleep(1) 

    @staticmethod
    def thread_monitor():
        """Continuously print a summary of active threads for diagnostics."""
        while True:
            active_threads = threading.active_count()
            logger.info("\n[THREAD MONITOR] Active threads:", active_threads)
            for t in threading.enumerate():
                logger.info(f"  - Name: {t.name}, Daemon: {t.daemon}")
            time.sleep(5)

    @staticmethod
    def resource_path(relative_path):
        if getattr(sys, 'frozen', False):
            # Nuitka onefile (and PyInstaller) temp extraction folder
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        else:
            base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        return os.path.join(base_path, relative_path)
