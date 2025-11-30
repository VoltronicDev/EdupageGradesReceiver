from edupage_api import Edupage
from edupage_api.exceptions import BadCredentialsException, CaptchaException
import os
import getpass
import subprocess
import argparse

from edupage_session import save_session
from creds_store import remove_creds
from pathlib import Path


def prompt_with_default(prompt: str, default: str | None) -> str:
    if default:
        resp = input(f"{prompt} [{default}]: ").strip()
        return resp if resp else default
    return input(f"{prompt}: ").strip()


def print_section(title: str) -> None:
    print()
    print("=" * len(title))
    print(title)
    print("=" * len(title))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Interactive Edupage login helper. Prompts for credentials and can save session/credentials."
    )
    parser.add_argument("--no-save", action="store_true", help="Do not save session cookies to disk")
    parser.add_argument("--refresh-session", action="store_true", help="Force overwriting any existing saved session")
    parser.add_argument("--persist-env", action="store_true", help="Persist username/subdomain to Windows user environment without prompting")
    parser.add_argument("--clear-creds", action="store_true", help="Remove stored session and encrypted creds then exit")
    args = parser.parse_args()

    if args.clear_creds:
        # remove files if present and exit
        Path(".edupage_session.json").unlink(missing_ok=True)
        try:
            remove_creds()
        except Exception:
            pass
        print("Removed .edupage_session.json and .edupage_creds (if they existed).")
        return
    print_section("Welcome to Edupage onboarding")
    print("This guided flow collects your Edupage credentials, sends them securely to Edupage for authentication,"
          " and saves only the resulting session tokens locally.")
    print("Credentials are kept in-memory for this login attempt; do not rely on this tool to persist passwords."
          " If your backend handles DPAPI or other encryption, keep that logic server-side.")
    print("Never check session files or credentials into source control.")

    # Show env defaults in prompts so you can press Enter to reuse them for this session
    default_user = os.getenv("EDUPAGE_USER")
    default_sub = os.getenv("EDUPAGE_SUBDOMAIN")

    print_section("Step 1/3 — Capture account details")
    print("Enter your Edupage username, password, and school subdomain.")
    print("Only the session tokens created after login are written to disk; credentials are discarded once login finishes.")

    username = prompt_with_default("Edupage username (or e-mail)", default_user)
    password = getpass.getpass("Password: ")
    subdomain = prompt_with_default("Edupage subdomain (the part before .edupage.org)", default_sub)

    if not all([username, password, subdomain]):
        print("Username, password and subdomain are required to login.")
        raise SystemExit(1)

    print_section("Step 2/3 — Authenticate with Edupage")
    print("Posting your credentials to Edupage…")
    edupage = Edupage()
    try:
        edupage.login(username, password, subdomain)
    except BadCredentialsException:
        print("❌ Wrong username or password.")
        raise
    except CaptchaException:
        print("❌ Edupage requested a captcha; complete it in the web UI and retry.")
        raise

    print("✅ Logged in successfully. Session tokens are ready to be saved.")

    print_section("Step 3/3 — Session handling")
    existing_session = Path(".edupage_session.json").exists()
    if existing_session and not args.refresh_session:
        refresh = input("A saved session exists. Refresh/overwrite it now? [Y/n]: ").strip().lower()
        force_refresh = refresh in ("", "y", "yes")
    else:
        force_refresh = args.refresh_session or existing_session

    if args.no_save:
        saved = False
        print("Skipping session save because --no-save was provided.")
    else:
        if existing_session and not force_refresh:
            print("Keeping existing session on disk. Use --refresh-session to overwrite it.")
            saved = False
        else:
            save_choice = input("Save session tokens locally for reuse? [Y/n]: ").strip().lower()
            if save_choice in ("", "y", "yes"):
                try:
                    saved = save_session(edupage)
                    if saved:
                        print("Session saved to .edupage_session.json")
                    else:
                        print("Could not save session (library may not expose session object).")
                except Exception as e:
                    saved = False
                    print("Failed to save session:", e)
            else:
                saved = False

    print()
    print("⚠️  Avoid storing passwords locally. Session files contain short-lived tokens; keep them private and out of version control.")
    if args.persist_env:
        print("Persisting username and subdomain to the Windows user environment for convenience.")
        try:
            subprocess.run(["setx", "EDUPAGE_USER", username], check=False)
            subprocess.run(["setx", "EDUPAGE_SUBDOMAIN", subdomain], check=False)
            os.environ["EDUPAGE_USER"] = username
            os.environ["EDUPAGE_SUBDOMAIN"] = subdomain
            print("Saved EDUPAGE_USER and EDUPAGE_SUBDOMAIN to user environment. New shells will see them.")
        except Exception as e:
            print("Failed to persist environment variables:", e)

    if not saved and not args.no_save:
        print("You chose not to write session tokens locally. Provide credentials again next time or set environment variables.")


if __name__ == "__main__":
    main()
