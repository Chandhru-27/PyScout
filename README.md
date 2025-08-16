# PyScout

PyScout is an intelligent Windows application that quietly watches over your digital habits, helping you reclaim control of your screen time and boost productivity. Like a trusted scout, it observes, reports, and guides you toward healthier computing habits.
It features a beautiful **CustomTkinter** UI, real-time analytics, distraction blocking, and a local SQLite database for history and stats.

## Features

- **Screen Time Tracking:** Monitors your daily computer usage.
- **App Usage Analytics:** Tracks time spent on individual apps.
- **Break Detection:** Reminds you to take breaks and logs break durations.
- **Distraction Blocking:** Block selected apps and websites to stay focused.
- **History & Stats:** View daily and weekly usage, trends, and app breakdowns.
- **Responsive UI:** Sidebar navigation, dashboard, history, and restricted management.
- **Tray Icon Integration:** Minimize to tray, restore, and graceful shutdown.
- **Performance Optimizations:** Runs smoothly on low-end devices.

## Folder Structure

- `app/` — Main application code (UI, logic, state, database, utilities)
- `logs/` — Log files for app and database events
- `assets/` — Icons and images for the UI
- `requirements.txt` — Python dependencies

## Requirements

- Windows 10 or later
- Python 3.8+
- Administrator privileges (for app blocking features)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Chandhru-27/PyScout.git
   cd PyScout
   ```

2. **Set up a virtual environment (recommended):**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment (Windows only):**
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Navigate to the application directory:**
   ```bash
   cd app
   ```

2. **Run the main application:**
   ```bash
   python main.py
   ```

> **Tip:** Run as administrator to enable all features (like app blocking).

## Usage

- Use the sidebar to switch between Dashboard, Restricted Apps/URLs, and History.
- Add or remove blocked apps and URLs from the Restricted page.
- View dailystats, and on-screen app usage charts.
- The app minimizes to the tray when closed; restore from the tray icon.

## Contributing

Contributions are welcome!  
Feel free to open an issue or submit a pull request for improvements or bug fixes.

## License
PyScout is under active development. License details will be added in a future release.

---

**Author:** Chandhru Loganathan

