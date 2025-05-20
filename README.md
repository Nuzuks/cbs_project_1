# Project 1:

This Django notes application is deliberately built with several security vulnerabilities for educational purposes.

### Prerequisites
- Python 3.x  
- Django (installed via requirements.txt)  

### Installation

```
# Create and activate a virtual environment
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Navigate to the Django project directory
cd project_1

# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Run the development server
python manage.py runserver
```
### Notes
- I used sqlitebrowser for SQLite to manually give users admin rights when needed. 

## Flaws Implemented:

1.  **SQL Injection (Injection)**
    *   **Location**: `project_1/views.py` in the `view_notes` function's search feature.
    *   **Description**: User input from the search GET parameter is directly concatenated into a raw SQL query.
    *   **Exploitation**:
        *   Search for: `' AND 0 UNION SELECT null, username, password, null FROM project_1_customuser; --` (to extract usernames and plaintext passwords). The number of columns in `UNION SELECT` must match the original query.
    *   **Screenshot**:
        *   `screenshots/1_sql_injection_payload.png` (Inputting the payload)
        *   `screenshots/2_sql_injection_result.png` (Seeing user data or all notes)
    *   **Fix**:
        * Search parameters are passed in placeholders preventing SQL injection.
        * `sql_injection_fixed.png`

2.  **Stored Cross-Site Scripting (XSS)**
    *   **Location**: `project_1/views.py` (`add_note` saves raw input, `view_notes` displays it) and `project_1/templates/project_1/view_notes.html` (uses `|safe` filter).
    *   **Description**: User-supplied content for notes is stored as-is and rendered unescaped in the `view_notes.html` template using the `|safe` filter.
    *   **Exploitation**: Create a note with content like: `<script>alert('XSS by ' + document.cookie);</script>` or `<img src=x onerror=alert('XSS!')>`. When any user views the notes, the script will execute in their browser.
    *   **Screenshot**:
        *   `screenshots/3_xss_payload.png` (Inputting the XSS in note content)
        *   `screenshots/4_xss_result.png` (XSS alert popping up when viewing notes)
    *   **Fix**:
        *   'note.content' is not rendered with the safe flag anymore
        *   `3_xss_fix.png` 

3.  **Broken Access Control**
    *   **Location**: `project_1/views.py` in the `admin_panel_view` function.
    *   **Description**: The `/super-secret-admin-panel/` URL and its corresponding view do not check if the user has administrative privileges before displaying sensitive information (list of users with passwords). It only checks if a user is logged in.
    *   **Exploitation**:
        1. Register a new user (e.g., `testuser`/`testpass`). By default, new users are NOT admins.
        2. Log in as `testuser`.
        3. Directly navigate to `/super-secret-admin-panel/`. You will see the admin content.
    *   **Screenshot**:
        *   `screenshots/5_broken_access_control.png` (Non-admin user accessing the admin panel and seeing all users/passwords)
    *   **Fix**:
        *   views.py now checks admin status and returns a HttpResponseForbidden access denied error
        *   `5_broken_access_control_fixed.png`

4.  **Sensitive Data Exposure (Plaintext Passwords)**
    *   **Location**:
        *   `project_1/models.py` (`CustomUser` model stores `password` as `CharField`).
        *   `project_1/views.py` (`register_user` saves plaintext, `login_user` checks plaintext).
        *   `project_1/templates/project_1/admin_panel.html` (displays plaintext passwords if BAC is also exploited).
    *   **Description**: User passwords are stored directly in the database as plaintext strings without any hashing.
    *   **Exploitation**: If an attacker gains database access (e.g., via SQL Injection) or access to the admin panel (via Broken Access Control), they can retrieve all user passwords in clear text.
    *   **Screenshot**:
        *   `screenshots/5_broken_access_control.png` (Plaintext password are seen in the admin panel)
    *   **Fix**:
        * Use djangos own user model to ensure that passwords are hashed
        * `sensitive_data_exposure_fixed.png` (This screenshot is only for demostration purposes of the hashing)
        * `sensitive_data_exposure_fixed_real.png` Removed passwords from the admin panel alltogether

5.  **Security Misconfiguration**
    *   **Location**: `vulnerable_project/settings.py`
    *   **Description**:
        *   `DEBUG = True`: In a production environment, this would expose detailed error pages with stack traces, settings, and other sensitive information.
        *   `SECRET_KEY = '...'`: The secret key is hardcoded directly in `settings.py`. If the source code is compromised, this key is also compromised, which can lead to session forgery and other attacks.
    *   **Exploitation**:
        *   `DEBUG = True`: Trigger an unhandled error in the application (e.g., by navigating to a non-existent complex URL if no 404 handler is robust) to see the debug page.
        *   `SECRET_KEY`: An attacker with source code access can use this key to forge signed cookies or tokens. This is a large problem if the program is open source, as everyone will have access to the key.
    *   **Screenshot**:
        *   `screenshots/6_security_misconfiguration.png` (Screenshot of the `settings.py` file showing `DEBUG = True` and the hardcoded `SECRET_KEY`).
    *   **Fix**:
        *   The `SECRET_KEY` is now stored in a `.env` file and accessed via the `dotenv` module at runtime.
        *   The `.env` file is excluded from version control by adding it to `.gitignore`.
        *   `DEBUG` is now set to `False` to prevent the exposure of internal application data in error messages.     
        *   `screenshots/6_security_misconfiguration_fixed.png` (Screenshot of the `settings.py` file showing `DEBUG = False` and the fetched `SECRET_KEY` from an .env fule.).




