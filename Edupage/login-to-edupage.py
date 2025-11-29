from edupage_api import Edupage
from edupage_api.exceptions import BadCredentialsException, CaptchaException
import os
import getpass
import subprocess
import argparse

from edupage_session import save_session
from creds_store import save_creds, remove_creds
from pathlib import Path


def prompt_with_default(prompt: str, default: str | None) -> str:
    if default:
        resp = input(f"{prompt} [{default}]: ").strip()
        return resp if resp else default
    return input(f"{prompt}: ").strip()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Interactive Edupage login helper. Prompts for credentials and can save session/credentials."
    )
    parser.add_argument("--no-save", action="store_true", help="Do not save session cookies to disk")
    parser.add_argument("--save-creds", action="store_true", help="Save encrypted credentials locally without prompting")
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
    # Show env defaults in prompts so you can press Enter to reuse them for this session
    default_user = os.getenv("EDUPAGE_USER")
    default_sub = os.getenv("EDUPAGE_SUBDOMAIN")

    username = prompt_with_default("Edupage username (or e-mail)", default_user)
    password = getpass.getpass("Password: ")
    subdomain = prompt_with_default("Edupage subdomain (the part before .edupage.org)", default_sub)

    if not all([username, password, subdomain]):
        print("Username, password and subdomain are required to login.")
        raise SystemExit(1)

    edupage = Edupage()
    try:
        edupage.login(username, password, subdomain)
    except BadCredentialsException:
        print("Wrong username or password!")
        raise
    except CaptchaException:
        print("Captcha required!")
        raise

    print("Logged in successfully")

    # Ask whether to save session cookies for reuse by `print_grades.py`.
    if args.no_save:
        saved = False
    else:
        save_choice = input("Save session for reuse? [Y/n]: ").strip().lower()
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

    # Offer to persist the entered credentials to user environment variables
    print()
    print("You can persist these values to your Windows user environment so the prompts")
    print("will be pre-filled on future runs. Storing the password in your environment is")
    print("insecure and visible to processes running as your user. Proceed only if you accept the risk.")
    # Persist to environment if requested via flag, otherwise prompt
    if args.persist_env:
        persist = "y"
    else:
        persist = input("Persist username and subdomain to user environment? [y/N]: ").strip().lower()

    if persist in ("y", "yes"):
        try:
            # setx persists to user environment; also update current process env for immediate use
            subprocess.run(["setx", "EDUPAGE_USER", username], check=False)
            subprocess.run(["setx", "EDUPAGE_SUBDOMAIN", subdomain], check=False)
            os.environ["EDUPAGE_USER"] = username
            os.environ["EDUPAGE_SUBDOMAIN"] = subdomain
            print("Saved EDUPAGE_USER and EDUPAGE_SUBDOMAIN to user environment. New shells will see them.")
        except Exception as e:
            print("Failed to persist environment variables:", e)

        if args.persist_env:
            store_pass = "n"
        else:
            store_pass = input("Also persist password to EDUPAGE_PASS? This is insecure. [y/N]: ").strip().lower()

        if store_pass in ("y", "yes"):
            try:
                subprocess.run(["setx", "EDUPAGE_PASS", password], check=False)
                os.environ["EDUPAGE_PASS"] = password
                print("Saved EDUPAGE_PASS to user environment. New shells will see it.")
            except Exception as e:
                print("Failed to persist EDUPAGE_PASS:", e)
        else:
            print("Password not persisted.")
    # Offer to persist encrypted credentials locally (safer than storing password in env)
    if args.save_creds:
        enc_choice = "y"
    else:
        enc_choice = input("Also save encrypted credentials locally for automatic login? [Y/n]: ").strip().lower()

    if enc_choice in ("", "y", "yes"):
        try:
            ok = save_creds({"user": username, "pass": password, "subdomain": subdomain})
            if ok:
                print("Credentials saved to .edupage_creds (encrypted for your Windows user).")
            else:
                print("Failed to save encrypted credentials.")
        except Exception as e:
            print("Failed to save encrypted credentials:", e)


if __name__ == "__main__":
    main()
