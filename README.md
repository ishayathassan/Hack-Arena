# Hack Arena

Hack Arena is a comprehensive competitive programming and coding learning platform built with Django. It provides a full-featured environment for learning, practicing, and competing in algorithmic challenges.

## Features

- **Home**: User dashboard, profile overview, login & signup system to keep track of progress and subscriptions.
- **Practice**: An extensive archive of algorithmic problems to practice coding. Includes problem descriptions, sample test cases, and a submission system to evaluate code.
- **Compete**: A dedicated section for hosting and participating in coding contests. Features include contest registration, problem sets, real-time leaderboard, and submission history.
- **Learn**: Educational modules tailored for programming languages like Python and C++. Learn the language syntax and basic algorithms before jumping into problem-solving.
- **Admin Panel**: A centralized dashboard to manage the platform contents. Admins can efficiently add, modify, or remove coding problems and manage coding contests.

## Technology Stack

- **Backend**: Python, Django
- **Database**: MySQL (Make sure to configure the database credentials in `hack_arena/settings.py`)
- **Frontend**: HTML, CSS (Templates stored in app-specific and project-level template directories)

## Getting Started

### Prerequisites

- Python 3.8+
- MySQL database server

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd "Hack Arena/Hack-Arena"
   ```

2. **Set up virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On MacOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   Make sure to install required packages like Django and MySQL client.
   ```bash
   pip install django mysqlclient
   ```

4. **Database Configuration:**
   Update the `DATABASES` dictionary in `hack_arena/hack_arena/settings.py` with your MySQL credentials:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'hackarena',
           'USER': 'root', # Your database user
           'PASSWORD': 'admin12345', # Your database password
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   ```
   *Make sure you create a database named `hackarena` in your MySQL server before running migrations.*

5. **Apply Migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a Superuser (Admin):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Development Server:**
   ```bash
   python manage.py runserver
   ```
   Visit `http://localhost:8000` to browse the platform or `http://localhost:8000/admin/` for the Django admin.

## Apps Overview

- `home/`: Manages user authentication, dashboards, and profiles.
- `practice/`: Problem repository for users to test their algorithm skills.
- `compete/`: Contest tracking, leaderboards, and timed competitions.
- `learn/`: Educational content for learning Python, C++, etc.
- `admin_panel/`: Platform management tool for admins to create and organize content.
