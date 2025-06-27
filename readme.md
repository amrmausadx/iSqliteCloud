# iSqliteCloud - Made by <a href='http://amrmausad.com'> Dr. Amr Mausad</a>

A fast, elegant PyQt5 application for browsing and executing SQL on SQLiteCloud databases.

## Features
- **Multiple Connections:** Manage multiple SQLiteCloud connections via a simple dropdown.
- **Elegant UI:** Modern dark theme, responsive layout, and SQLite icon branding.
- **Table Browser:** View tables and their data with a single click.
- **SQL Editor:** Execute any SQL (SELECT, INSERT, UPDATE, DELETE, etc.) and view results instantly.
- **Auto-setup:** On first run, creates a `connections.txt` file for you to add your database connections.
- **Cross-platform:** Works on Windows, macOS, and Linux (Python 3.7+).

## Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/amrmausadx/iSqliteCloud.git
   cd iSqliteCloud
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application:**
   ```bash
   python isqlitcloud.py
   ```

## Configuration
- On first run, a `connections.txt` file will be created (and opened) in the project directory.
- Add your SQLiteCloud connection strings in the following format:
  ```
  # Format: <connection_string>;<display_name>
  # Example:
  sqlitecloud://user:password@cloud.sqlite.com:443/db1?apikey=APIKEY1;Production DB
  sqlitecloud://xxxxxxxx.g3.sqlite.cloud:8860/projectname?apikey=YOUR_API_KEY;Project Cloud
  ```
- Each line represents a connection. The display name will appear in the dropdown.

## Notes
- The app will create and use `connections.txt` in the current working directory.

## License
This project is open source and available under the MIT License. 