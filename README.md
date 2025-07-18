n
# TheSchedulePlus

> A centralized GUI application integrating Client & Project, Time Log, and Employ & Subconsultant management systems built with Tkinter.

[![License: Not specified](https://img.shields.io/badge/License-Not%20specified-yellow.svg)](https://github.com/TheGodAnnihilator/TheSchedulePlus)
[![GitHub stars](https://img.shields.io/github/stars/TheGodAnnihilator/TheSchedulePlus?style=social)](https://github.com/TheGodAnnihilator/TheSchedulePlus)

## Description

The Schedule Plus is a desktop application designed to streamline client, project, time log, employee, and subconsultant management. Built using Python and the Tkinter GUI library, it provides a tabbed interface for managing different aspects of project workflows. This application aims to centralize key operational tasks, making it easier to track project progress, manage time logs, and handle employee/subconsultant information. It leverages lazy loading to optimize performance, instantiating manager classes only when their corresponding tabs are accessed. The application also features a custom style configuration for a consistent and modern user experience. Data storage is handled through `mysql.connector`, implying a MySQL database backend.

## ✨ Key Features

- **Client & Project Management:** Allows users to manage client information and project details within a dedicated tab.
- **Time Log Management:** Provides functionality for tracking and managing time logs associated with projects and employees.
- **Employ & Subconsultant Management:** Enables users to manage employee and subconsultant information, potentially including assignments and payment details.

## 🛠️ Technology Stack

- **Frontend:** Tkinter, ttk (themed Tkinter widgets)
- **Backend:** Python
- **Database:** MySQL (using `mysql.connector`)

## 🚀 Getting Started

### Prerequisites

- Python 3.x (with Tkinter support)
- MySQL Database Server

### Installation

1.  Clone the repository:
    ```sh
    git clone https://github.com/TheGodAnnihilator/TheSchedulePlus
    ```
2.  Navigate to the project directory:
    ```sh
    cd TheSchedulePlus
    ```
3.  Install dependencies:
    ```sh
    pip install mysql-connector-python
    ```
                
### Running the Project
```sh
python main.py
```

## 🤝 Contributing

Contributions are welcome! Please check the [issues page](https://github.com/TheGodAnnihilator/TheSchedulePlus/issues) for ways to contribute.

## 📝 License

This project is licensed under the **Not specified**.
