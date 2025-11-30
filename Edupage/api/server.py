"""Minimal API server exposing Edupage grades."""

from collections import defaultdict
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from edupage_api.exceptions import NotLoggedInException

from edupage_session import get_edupage

app = FastAPI(title="Edupage Grades API")


def _serialize_grade(grade: Any) -> Dict[str, Any]:
    """Convert a grade object returned by `edupage_api` to a JSON-serializable dict."""

    return {
        "title": getattr(grade, "title", None),
        "score": getattr(grade, "grade_n", None),
        "max_points": getattr(grade, "max_points", None),
        "percent": getattr(grade, "percent", None),
    }


@app.get("/grades")
def get_grades() -> Dict[str, List[Dict[str, Any]]]:
    """Return grades grouped by subject.

    Tries to reuse a stored Edupage session; if it is expired or no credentials
    are found, returns a 401 error that callers can use to prompt for login.
    """

    edupage = get_edupage()
    if edupage is None:
        raise HTTPException(
            status_code=401,
            detail="No Edupage credentials or saved session found. Please log in again.",
        )

    try:
        grades = edupage.get_grades()
    except NotLoggedInException as exc:
        raise HTTPException(
            status_code=401, detail="Edupage session expired. Please log in again."
        ) from exc
    except Exception as exc:  # pragma: no cover - passthrough for unexpected failures
        raise HTTPException(
            status_code=500, detail="Failed to fetch grades from Edupage."
        ) from exc

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for grade in grades:
        grouped[getattr(grade, "subject_name", "Unknown subject")].append(
            _serialize_grade(grade)
        )

    subjects = [
        {"subject": subject, "items": items}
        for subject, items in grouped.items()
    ]

    return {"subjects": subjects}


if __name__ == "__main__":  # pragma: no cover - manual run helper
    import uvicorn

    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=True)
