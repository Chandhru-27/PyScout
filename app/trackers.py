from userstate import UserActivityState
from utilities import shutdown_event
import notification
from utilities import Utility
from app_logger import logger
from datetime import datetime , timedelta
import keywords
import db

# ====== Initialize the Database ======= #

user_db = db.Database()
user_db.create_general_user_stats()
user_db.create_appwise_usage()

# ====== Activity Tracker Logic ======= #

def activity_tracker(state: UserActivityState):
    """Track screen/break time and appwise usage, persisting periodic snapshots to the DB."""
    def activity_logic(gap_seconds = 0):
        try:
            if shutdown_event.is_set():
                return

            if state.is_paused:
                logger.warning("Tracker Paused")
                return
            
            state.update()
            with state.lock:
                date = datetime.now().strftime("%Y-%m-%d")
                app_data = state.screentime_per_app.copy()
                screen = state.screen_time
                brk = state.total_break_duration

            user_db.update_daily_state(
                date=date,
                screen_time=screen,
                break_time=brk,
                app_usage_dict=app_data
            )

        except Exception as e:
            logger.exception("Crash in activity_logic:")
                
    Utility.run_precise_timer(2, activity_logic)


# ===== Reminder Logic ======= #

def reminder_logic(state):
    """Compute break detection over time, handling idle/sleep gaps and merging short active periods."""
    if shutdown_event.is_set():
        return

    reminder_threshold = 45 * 60  # minutes before reminder
    idle_threshold = 60  # idle threshold in seconds
    break_merge_gap = 15  # seconds between breaks to merge

    def main_logic(gap_seconds=0):
        try:
            if state.is_paused:
                return

            with state.lock:
                now = datetime.now()

                # Reminder notification
                if state.total_stretch_time >= reminder_threshold:
                    if Utility.is_notification_disabled() or Utility.is_focus_assist_on():
                        notification.customnotify()
                    notification.notify()
                    state.total_stretch_time = 0

                # Detect break: either user idle or device asleep
                is_video_playback = any(
                    kw in state.active_window.lower() for kw in keywords.video_keywords
                )
                is_sleeping = (gap_seconds > idle_threshold)
                is_user_idle = (state.idle_time >= idle_threshold and not is_video_playback)

                if is_sleeping or is_user_idle:
                    state.total_break_duration += gap_seconds

                    # Clamp so break time never exceeds 24h minus screen time
                    max_break = max(0, 86400 - state.screen_time)
                    if state.total_break_duration > max_break:
                        state.total_break_duration = max_break

                    logger.info(
                        f"Break detected. Added {state.get_formatted_screen_time(gap_seconds)}. "
                        f"Total Break Time: {state.get_formatted_screen_time(state.total_break_duration)}"
                    )

        except Exception:
            logger.exception("Crash in reminder_logic:")

    Utility.run_precise_timer(2, main_logic)