# GmailFetcher

GmailFetcher is an open-source Python project that automatically fetches new email messages from your Gmail account and stores the message details, including subject, sender, date, and content, into a PostgreSQL database. This tool is useful for archiving emails, processing or analyzing emails programmatically, or integrating email data into other applications.

**Note:** This project has been successfully tested on macOS.

## Features

- Fetches new emails from Gmail using the Gmail API.
- Stores email details in a PostgreSQL database.
- Continuous monitoring with adjustable fetch intervals.

## Prerequisites

- Python 3.x
- PostgreSQL
- A Google Cloud Platform account

## Getting Started

### Step 1: Clone the Repository

```sh
git clone https://github.com/inabakumori/GmailFetcher.git
cd GmailFetcher
```

### Step 2: Set Up a Virtual Environment

Create and activate a virtual environment to manage dependencies:

```sh
python3 -m venv env
source env/bin/activate # On Windows use `env\Scripts\activate`
```

### Step 3: Install Dependencies

Install the required Python packages:

```sh
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib psycopg2-binary
```

### Step 4: Set Up Google Cloud Platform (GCP)

1. Create a new project in the Google Cloud Console.
2. Enable the Gmail API for your project:
   - Navigate to "APIs & Services" > "Dashboard" > "+ ENABLE APIS AND SERVICES".
   - Search for "Gmail API" and enable it.
3. Create credentials to access the Gmail API:
   - Go to "APIs & Services" > "Credentials".
   - Click "Create Credentials" > "OAuth client ID".
   - Application type: "Desktop app".
   - Name your OAuth 2.0 client and click "Create".
   - Download the JSON credentials file by clicking the download icon next to your new OAuth client ID.

### Step 5: Prepare the PostgreSQL Database

#### Install PostgreSQL

If you haven't installed PostgreSQL yet, please refer to the official PostgreSQL installation guides for detailed instructions tailored to your operating system.

#### Create a New PostgreSQL Database and User

1. Open the PostgreSQL command line tool: This is `psql` on most systems.
   - On Windows, you can find it as "SQL Shell (psql)" in the Start menu.
   - On Linux/macOS, open a terminal and run `psql` to enter the PostgreSQL command line interface.
2. Log in: If prompted, enter the default username (`postgres`) and the password you set during installation.
3. Create a new database:
   ```sql
   CREATE DATABASE gmail;
   ```
4. Create a new user (optional): You might want to create a user specific to your application. Replace `your_username` and `your_password` with your desired username and password.
   ```sql
   CREATE USER your_username WITH ENCRYPTED PASSWORD 'your_password';
   ```
5. Grant privileges to the new user on your database (skip this step if you're using the default `postgres` user):
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE gmail TO your_username;
   ```
6. Exit psql:
   ```sql
   \q
   ```

#### Create the `emails` Table

1. Connect to your new database using psql:
   ```sh
   psql -d gmail -U your_username
   ```
   Replace `your_username` with the username you created or `postgres` if you're using the default.
2. Create the table by executing the SQL command:
   ```sql
   CREATE TABLE emails (
     id SERIAL PRIMARY KEY,
     email_id TEXT UNIQUE,
     subject TEXT,
     sender TEXT,
     date TIMESTAMP,
     content TEXT
   );
   ```
3. Verify the table creation (optional):
   ```sql
   \dt
   ```

### Step 6: Update GmailFetcher Script

Update the `gmail_automation.py` script with the PostgreSQL connection details. Replace `localhost`, `gmail`, `your_username`, and `your_password` with your actual database host, database name, username, and password:

```python
conn = psycopg2.connect(
    host="localhost",
    database="gmail",
    user="your_username",
    password="your_password"
)
```

### Step 7: Running the Script

1. Rename the downloaded JSON credentials file to `client_secret.json` and place it in the project root.
2. Run the script:
   ```sh
   python3 gmail_automation.py
   ```
3. Follow the on-screen instructions to authenticate with your Google account. This process will generate a `token.json` file for subsequent authentications.

## Usage Notes

- The script runs in a continuous loop, fetching new emails every second. Adjust the `time.sleep(1)` call as needed.
- To stop the script, use `CTRL+C` in the terminal.

## Troubleshooting

### Fixing the error: psql: FATAL: role "postgres" does not exist

If you're trying to access PostgreSQL with:

```sh
psql -U postgres
```

And encounter the error: "psql: FATAL: role "postgres" does not exist", follow these steps to resolve it:

1. Install PostgreSQL
   If you haven't installed PostgreSQL yet, you can install it using Homebrew:
   ```sh
   brew install postgresql
   ```

2. Start PostgreSQL
   To start the PostgreSQL service with Homebrew, use:
   ```sh
   brew services start postgresql
   ```

3. Fixing the Role Error
   If the error regarding the missing `postgres` role occurs, you can create the `postgres` user (role) with the following command. Note that the exact path might vary based on your PostgreSQL installation version and how you installed PostgreSQL (e.g., if you used Homebrew or another method). Typically, for Homebrew installations, you can use:
   ```sh
   /usr/local/Cellar/postgresql/<version>/bin/createuser -s postgres
   ```
   Or, more generally for Homebrew installations:
   ```sh
   /usr/local/opt/postgres/bin/createuser -s postgres
   ```
   This command creates the `postgres` superuser, allowing you access to PostgreSQL with this role.

   Make sure to replace `<version>` with your actual installed version of PostgreSQL. You can find out your PostgreSQL version with `postgres --version` and adjust the command accordingly.

## Contributing

Contributions to GmailFetcher are welcome! Please follow the standard fork, branch, and pull request workflow.

## License

GmailFetcher is open-source software licensed under the GNU General Public License v3.0.
