# PyTracker

PyTracker is a modern desktop productivity tool for Windows that helps you monitor and manage your screen time, app usage, and break habits. It features a beautiful customtkinter UI, real-time analytics, distraction blocking, and a local SQLite database for history and stats.

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
   git clone https://github.com/Chandhru-27/PyTracker.git
   cd PyTracker
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running Locally

1. **Navigate to the app directory:**
   ```bash
   cd Testing_structure/app
   ```

2. **Run the main application:**
   ```bash
   python main.py
   ```

   > **Note:** For full functionality (app blocking), run as administrator.

## Usage

- The sidebar lets you switch between Dashboard, Restricted Apps/URLs, and History.
- Add or remove blocked apps and URLs from the Restricted page.
- View daily and weekly stats, and detailed app usage charts.
- The app minimizes to the tray when closed; restore from the tray icon.

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements or bug fixes.

## License

This project is under active development. License details will be added in a future release.

---

Let me know if you want to customize or expand any section!
