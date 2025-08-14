CREATE_TABLE_USER_STATS = """
    CREATE TABLE IF NOT EXISTS GENERAL_USAGE (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT UNIQUE,
    screen_time INTEGER DEFAULT 0,
    break_time INTEGER DEFAULT 0
);
"""

CREATE_TABLE_APPLICATION_USAGE = """
    CREATE TABLE IF NOT EXISTS APP_USAGE (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_name TEXT,
    date TEXT,
    usage_duration INTEGER DEFAULT 0,
    user_stat_id INTEGER,
    FOREIGN KEY(user_stat_id) REFERENCES GENERAL_USAGE(id) ON DELETE CASCADE,
    UNIQUE(app_name, date)
    );
"""

CREATE_TABLE_BLOCKED_APPS = """
    CREATE TABLE IF NOT EXISTS blocked_apps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_name TEXT UNIQUE
    );
"""

CREATE_TABLE_BLOCKED_URLS = """
    CREATE TABLE IF NOT EXISTS blocked_urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE
    );
"""

CREATE_TABLE_APP_SETTINGS = """
    CREATE TABLE IF NOT EXISTS app_settings (
        id INTEGER PRIMARY KEY,
        setting_name TEXT,
        reminder_threshold INTEGER,
        pomodoro_enabled INTEGER,
        pomodoro_cycle INTEGER
    );
"""

CREATE_TABLE_BREAK_SETTINGS = """
    CREATE TABLE IF NOT EXISTS break_settings(
        id INTEGER PRIMARY KEY,
        break_setiing TEXT,
        break_threshold INTEGER DEFAULT 60
    )
"""

CREATE_TABLE_DONT_NOTIFY_APPS = """
    CREATE TABLE IF NOT EXISTS dont_notify_apps(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_name TEXT UNIQUE
    )
"""
