
# 📅 TheSchedulePlus

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![MySQL](https://img.shields.io/badge/Database-MySQL-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Mac-informational)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

> A comprehensive desktop-based **Database Management System** for managing **clients**, **employees**, **subconsultants**, **projects**, and **time logs**. Built with Python, Tkinter, and MySQL for organizations that need a customizable, local, and professional solution for operational tracking.

---

## 📚 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Screens & Functionalities](#-screens--functionalities)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

- ✅ GUI-powered MySQL database management
- ✅ Client and Project tracking
- ✅ Add, view, edit, and delete **employees** and **subconsultants**
- ✅ Time logging with project and task linking
- ✅ State → City cascading dropdowns
- ✅ Real-time validation and success/error messages
- ✅ Configurable MySQL connection via `config.ini`

---

## 🧱 Architecture

- **Frontend**: Tkinter (Python GUI toolkit)
- **Backend**: Python + `mysql.connector`
- **Database**: MySQL (local or remote)
- **Configuration**: `.ini` file (simple and editable)

---

## 🖥️ Screens & Functionalities

### 🔹 `main_manager.py`
Acts as the main dashboard. Launches other windows (e.g., employee manager, subconsultant manager, and time logger).

---

### 🔹 `employ_subconsultant.py`
**Features:**
- Add/View/Edit/Delete employees and subconsultants
- Fields include:
  - Name
  - Type (employee or subconsultant)
  - State and dynamic City
  - ZIP code
- Modern and structured layout with form validation

---

### 🔹 `timelog.py`
**Features:**
- Time tracking per task
- Linked to employee and subconsultant entries
- "View by Date" tab shows:
  - List of all activities on a selected date
  - **Total hours worked** per day

---

### 🔹 `config.ini`
```ini
[mysql]
host = ''
user = ''
password = ''
database = ''
```
> Used for database connection setup. Keep this file secure and **never commit with credentials in production.**

---

## 🛠️ Installation

### ✅ Prerequisites

- Python 3.8 or later
- MySQL Server
- `pip` (Python package manager)

### 🐍 Python Dependencies

Install required packages using:

```bash
pip install mysql-connector-python
```

---

## ⚙️ Configuration

Edit the `config.ini` file to match your MySQL credentials and database name:

```ini
[mysql]
host = localhost
user = root
password = your_password_here
database = your_database_name
```

---

## 🚀 Usage

1. Start MySQL Server.
2. Run the main application:

```bash
python main_manager.py
```

3. Use the GUI to:
   - Add/manage employees and subconsultants
   - Log time entries
   - View daily summaries of hours worked

---

## 📁 Project Structure

```text
TheSchedulePlus/
│
├── main_manager.py           # Entry point – launches submodules
├── employ_subconsultant.py   # GUI for employee/subconsultant management
├── timelog.py                # GUI for time logging and daily summary
├── config.ini                # MySQL credentials and database name
```

---

## 🧭 Roadmap

- [ ] Add search and filter functionality
- [ ] Export time logs as CSV or Excel
- [ ] Authentication/login system
- [ ] Project/task hierarchy with deadlines
- [ ] Admin panel for user access levels

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repo
2. Create your feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

## 📜 License

This project is under the **MIT License** – feel free to use and modify it.

---

## 📬 Contact

For issues, suggestions, or collaborations, open an issue or contact the repository owner.

---

> _Crafted with ❤️ to simplify scheduling and operations for teams._
