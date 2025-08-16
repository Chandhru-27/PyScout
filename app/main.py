from utilities import Utility
from app_logger import logger
import sys
import os

def run_silent_updates():
    update_url = Utility.check_for_updates()
    if update_url:
        import subprocess
        try:
            local_path = Utility.download_latest_version(url=update_url)
            if local_path:
                logger.info("Installing update silently...")
                process = subprocess.Popen([local_path, "/VERYSILENT", "/NORESTART"], shell=True)
                process.wait()  

                logger.info("Update installed. Restarting application...")
                exe_path = sys.executable  
                os.execv(exe_path, sys.argv)  

        except Exception as e:
            logger.exception(f"Updater failed {e}")
    else:
        logger.info("No updates found.")


def run_with_admin_privileges():
    """Check if running with administrator privileges."""
    import ctypes
    try:
        if not Utility.is_admin():
            logger.warning("Application not running as administrator")
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            logger.info("Running as admin")
            sys.exit(0)
    except Exception as e:
        logger.error(f"Error giving admin privileges: {e}")

def initialize_database():
    """Initialize database with error handling."""
    import db
    try:
        logger.info("Initializing database...")
        user_db = db.Database()
        logger.info("Database initialized successfully")
        return user_db
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return None

def initialize_state(user_db):
    """Initialize user state with existing data."""
    from datetime import datetime
    from userstate import UserActivityState
    try:
        state = UserActivityState()
        
        today = datetime.now().strftime("%Y-%m-%d")
        existing = user_db.load_existing_general_usage(date=today)
        
        blocked_apps = user_db.load_blocked_apps()
        blocked_urls = user_db.load_blocked_urls()
        state.blocked_apps = blocked_apps
        state.blocked_urls = blocked_urls
        state.dont_notify_apps = user_db.load_dont_notify_apps()
        is_set_to, threshold, pomodoro_enabled, pomodoro_cycle = user_db.load_settings()
        state.setting_name = is_set_to
        state.reminder_threshold = threshold
        state.pomodoro = pomodoro_enabled
        state.pomodoro_cycle = pomodoro_cycle
        state.break_setting_name , state.break_threshold = user_db.load_break_settings()
        logger.info(f"Loaded settings: {state.break_setting_name}, idle threshold: {state.idle_threshold}.")
        
        if existing:
            screen_time, break_time = existing
            app_usage = user_db.load_existing_appwise_usage(today)
            state.load_existing_data(screen_time, break_time, app_usage, blocked_apps, blocked_urls)
            logger.info(f"Loaded previous usage: Screen Time: {screen_time}, Break Time: {break_time}")
        else:
            logger.info("No previous usage found. Starting fresh.")
        
        return state
        
    except Exception as e:
        logger.error(f"Failed to initialize state: {e}")
        return None

def start_background_services(state, user_db):
    """Start background tracking and reminder services."""
    import threading
    import trackers
    try:
        if state.blocked_apps:
            Utility.start_app_blocker(state.blocked_apps, scan_interval=1)
            logger.info("App blocker started")
        
        tracker_thread = threading.Thread(
            target=trackers.activity_tracker, 
            args=(state,), 
            daemon=True,
            name="ActivityTracker"
        )
        reminder_thread = threading.Thread(
            target=trackers.reminder_logic, 
            args=(state,), 
            daemon=True,
            name="ReminderLogic"
        )
        
        tracker_thread.start()
        reminder_thread.start()
        logger.info("Background services started")
        
        return tracker_thread, reminder_thread
        
    except Exception as e:
        logger.error(f"Failed to start background services: {e}")
        return None, None

def main():
    """Main application entry point."""
    try:
        logger.info("Starting PyScout...")
        
        run_with_admin_privileges()
        
        user_db = initialize_database()
        
        if not user_db:
            logger.error("Failed to initialize database. Exiting.")
            sys.exit(1)
        
        state = initialize_state(user_db)
        if not state:
            logger.error("Failed to initialize state. Exiting.")
            sys.exit(1)
        
        tracker_thread, reminder_thread = start_background_services(state, user_db)
        if not tracker_thread or not reminder_thread:
            logger.error("Failed to start background services. Exiting.")
            sys.exit(1)
         
        from base_layout import PyScout
        logger.info("Starting user interface...")
        app = PyScout(state=state)
        app.tracker_thread = tracker_thread
        app.reminder_thread = reminder_thread
        
        app.title("PyScout")
        app.minsize(900,700)
        # img_path = Utility.resource_path("assets/icon.ico") # Development
        img_path = Utility.resource_path("app/assets/icon.ico") # Production
        app.iconbitmap(default=img_path)
        logger.info("Application started successfully")
        app.mainloop()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.exception(f"Unexpected error in main: {e}")
        sys.exit(1)
    finally:
        logger.info("Application shutting down")
    
if __name__ == "__main__":
    Utility.add_to_startup()
    run_silent_updates()
    main()