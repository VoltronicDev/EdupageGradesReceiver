# Edupage Scripts

Small utilities to login to Edupage and print grades.

Files
- `login-to-edupage.py` — interactive login helper. Prompts for username, password and subdomain, can save a session and optionally persist credentials (environment or encrypted local store).
- `print_grades.py` — loads a saved session (or credentials) and prints grades grouped by subject.
- `edupage_session.py` — helper that saves/loads session cookies and can login using env vars or encrypted local creds.
- `creds_store.py` — Windows DPAPI-backed encrypted local credential store (`.edupage_creds`).

Requirements
- Python 3.8+ (the project was tested on Windows with Python 3.13)
- `edupage_api` package (install with `pip install edupage-api` or check the package name your environment uses)

Quick Setup (PowerShell)

1. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install edupage-api
```

2. Run the interactive login once to create a session and (optionally) save encrypted credentials:

```powershell
python .\login-to-edupage.py
```

This will prompt for:
- `Edupage username` (shows `EDUPAGE_USER` default if set)
- `Password` (hidden)
- `Edupage subdomain` (shows `EDUPAGE_SUBDOMAIN` default if set)
- Optionally save session cookies to `.edupage_session.json`
- Optionally persist username/subdomain to Windows user environment (via `setx`) and/or save encrypted credentials to `.edupage_creds` (recommended instead of storing password in environment).

Usage

- Print grades (reuses saved session / encrypted creds automatically):

```powershell
python .\print_grades.py
```

If no saved session or credentials are found, run `login-to-edupage.py` or set the following environment variables in your shell before running `print_grades.py`:

```powershell
$env:EDUPAGE_USER = "your_username"
$env:EDUPAGE_PASS = "your_password"
$env:EDUPAGE_SUBDOMAIN = "your_subdomain"
python .\print_grades.py
```

Security notes
- `.edupage_creds` is encrypted using Windows DPAPI and is only decryptable by the same Windows user account. It is safer than storing plaintext credentials in environment variables but not suitable for multi-user or cross-machine sharing.
- `.edupage_session.json` stores session cookies. If an attacker obtains these files while running as your user, they may be able to reuse your session. Keep them private.
- Add these files to `.gitignore` (this repo includes a `.gitignore` entry for them).

Removing stored data
- Remove saved session:
```powershell
Remove-Item .\.edupage_session.json -ErrorAction SilentlyContinue
```
- Remove encrypted creds:
```powershell
Remove-Item .\.edupage_creds -ErrorAction SilentlyContinue
```

Extending or changing behavior
- If you want cross-platform encrypted storage, consider switching `creds_store.py` to use the `cryptography` package and a master passphrase.
- If the `edupage_api` internals change, session saving/loading may need adjustments.

Contact
- If you want further changes (auto-login prompting in `print_grades.py`, CLI flags, or cross-platform encryption), open an issue or ask for specific changes.
