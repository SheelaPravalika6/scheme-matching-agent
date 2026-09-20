import json
import os

def load_schemes():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "schemes.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_single_scheme(profile, scheme):
    rules = scheme["eligibility"]
    reasons_passed = []
    reasons_failed = []

    if rules.get("min_age") is not None or rules.get("max_age") is not None:
        age = profile.get("age")
        min_age = rules.get("min_age", 0)
        max_age = rules.get("max_age", 200)
        if age is not None and min_age <= age <= max_age:
            reasons_passed.append(f"Age {age} is within the allowed range ({min_age}-{max_age})")
        else:
            reasons_failed.append(f"Age must be between {min_age} and {max_age}")

    if rules.get("category"):
        user_category = profile.get("category")
        if user_category in rules["category"]:
            reasons_passed.append(f"Category '{user_category}' is eligible")
        else:
            reasons_failed.append(f"Category must be one of {rules['category']}")

    if rules.get("occupation"):
        user_occupation = profile.get("occupation")
        if user_occupation in rules["occupation"]:
            reasons_passed.append(f"Occupation '{user_occupation}' is eligible")
        else:
            reasons_failed.append(f"Occupation must be one of {rules['occupation']}")

    if rules.get("education_min"):
        user_education = profile.get("education")
        if user_education == rules["education_min"]:
            reasons_passed.append(f"Education meets the minimum requirement")
        else:
            reasons_failed.append(f"Education must be at least {rules['education_min']}")

    total_checks = len(reasons_passed) + len(reasons_failed)
    if total_checks == 0:
        status = "match"
    elif len(reasons_failed) == 0:
        status = "match"
    elif len(reasons_failed) <= 1:
        status = "near_miss"
    else:
        status = "not_eligible"

    return {
        "scheme_id": scheme["scheme_id"],
        "name": scheme["name"],
        "status": status,
        "reasons_passed": reasons_passed,
        "reasons_failed": reasons_failed,
        "documents_required": scheme.get("documents_required", [])
    }


def check_eligibility(profile):
    schemes = load_schemes()
    results = [check_single_scheme(profile, s) for s in schemes]
    matches = [r for r in results if r["status"] == "match"]
    near_misses = [r for r in results if r["status"] == "near_miss"]
    return {"matches": matches, "near_misses": near_misses}


if __name__ == "__main__":
    test_profile = {
        "age": 25,
        "category": "obc",
        "occupation": "entrepreneur",
        "education": "8th pass"
    }
    result = check_eligibility(test_profile)
    print(json.dumps(result, indent=2))