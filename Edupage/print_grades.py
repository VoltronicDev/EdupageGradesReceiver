from edupage_session import get_edupage

# Try to load a saved session or login via environment variables.
edupage = get_edupage()
if edupage is None:
    print("No saved session and no credentials found.")
    print("Set EDUPAGE_USER, EDUPAGE_PASS and EDUPAGE_SUBDOMAIN environment variables,")
    print("or run `login-to-edupage.py` to create a session first.")
    raise SystemExit(1)

try:
    grades = edupage.get_grades()
except Exception as e:
    print("Failed to fetch grades using the loaded session:", e)
    print("Try running `login-to-edupage.py` to refresh the session or verify credentials.")
    raise

grades_by_subject = {}

for grade in grades:
    if grades_by_subject.get(grade.subject_name):
        grades_by_subject[grade.subject_name] += [grade]
    else:
        grades_by_subject[grade.subject_name] = [grade]

for subject in grades_by_subject:
    print(f"{subject}:")
    for grade in grades_by_subject[subject]:

        print(f"    {grade.title} -> ", end="")

        if grade.max_points != 100:
            print(f"{grade.grade_n}/{grade.max_points}")
        else:
            print(f"{grade.percent}%")
    print("----------------")
