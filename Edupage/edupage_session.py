from pathlib import Path
import json
import os
import requests

from edupage_api import Edupage
from edupage_api.exceptions import NotLoggedInException
from creds_store import load_creds

_SESSION_FILE = Path(__file__).parent / ".edupage_session.json"


def save_session(edupage, path: Path | None = None) -> bool:
    """Save cookies from an `Edupage` instance to a JSON file.

    Returns True on success, False otherwise.
    """
    path = Path(path) if path else _SESSION_FILE
    session = getattr(edupage, "session", None) or getattr(edupage, "_session", None)
    if session is None or not hasattr(session, "cookies"):
        return False

    cookies = requests.utils.dict_from_cookiejar(session.cookies)
    # try to capture identifying attributes so the session can be restored properly
    attrs = {}
    for name in ("subdomain", "_subdomain", "base_url", "_base_url", "_logged_in", "logged_in"):
        if hasattr(edupage, name):
            try:
                attrs[name] = getattr(edupage, name)
            except Exception:
                pass

    data = {"cookies": cookies, "attrs": attrs}
    path.write_text(json.dumps(data))
    return True


def load_session(path: Path | None = None) -> Edupage | None:
    """Load cookies from file and return an `Edupage` instance with those cookies attached.

    If the file does not exist, returns None.
    """
    path = Path(path) if path else _SESSION_FILE
    if not path.exists():
        return None

    try:
        data = json.loads(path.read_text())
        cookies = data.get("cookies", {})
        attrs = data.get("attrs", {})
    except Exception:
        return None

    ed = Edupage()
    # restore identifying attributes if present
    for k, v in attrs.items():
        try:
            setattr(ed, k, v)
        except Exception:
            pass

    session = getattr(ed, "session", None) or getattr(ed, "_session", None)
    if session is None:
        # can't attach cookies, but return a fresh instance
        return ed

    session.cookies = requests.utils.cookiejar_from_dict(cookies)
    return ed


def get_edupage(auto_save: bool = True) -> Edupage | None:
    """Return an `Edupage` instance.

    Flow:
    - Try to load saved cookies from disk and return an `Edupage` with those cookies.
    - If no saved session, try to login using environment variables
      `EDUPAGE_USER`, `EDUPAGE_PASS`, `EDUPAGE_SUBDOMAIN` and save the session.
    - On failure, return None.
    """
    ed = load_session()
    if ed is not None:
        # validate that the loaded session is actually logged in
        try:
            # try a lightweight API call to detect authentication state
            ed.get_grades()
            return ed
        except NotLoggedInException:
            # session expired or invalid; continue to login via env
            pass
        except Exception:
            # other errors (network, API changes) — still attempt env login
            pass

    # Try to load encrypted local credentials if env vars are not present
    user = os.getenv("EDUPAGE_USER")
    pw = os.getenv("EDUPAGE_PASS")
    sub = os.getenv("EDUPAGE_SUBDOMAIN")
    if not all([user, pw, sub]):
        creds = None
        try:
            creds = load_creds()
        except Exception:
            creds = None
        if creds:
            user = creds.get("user")
            pw = creds.get("pass")
            sub = creds.get("subdomain")

    if not all([user, pw, sub]):
        return None

    ed = Edupage()
    try:
        ed.login(user, pw, sub)
    except Exception:
        return None

    if auto_save:
        try:
            save_session(ed)
        except Exception:
            pass

    return ed
