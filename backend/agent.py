import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.eligibility import check_eligibility

# Load the API key from .env
load_dotenv()

# Set up the Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)


def collect_profile_from_answers(age, category, occupation, education):
    """
    Takes the raw answers and builds a clean profile dictionary,
    the same shape check_eligibility() expects.
    """
    return {
        "age": int(age),
        "category": category.strip().lower(),
        "occupation": occupation.strip().lower(),
        "education": education.strip().lower()
    }


def explain_results_with_llm(profile, results):
    """
    Takes the raw eligibility results (matches + near-misses) and asks
    Gemini to turn them into a clear, friendly explanation for the user.
    """
    prompt = f"""
You are a helpful assistant explaining government scheme eligibility results to a user.

User profile: {profile}

Matched schemes (user is eligible): {results['matches']}

Near-miss schemes (user is close but missing something): {results['near_misses']}

Write a short, friendly, clear explanation for the user. For each matched scheme,
say why they qualify in plain language. For each near-miss, say what's missing and
what would make them eligible. Do not invent any information beyond what's given above.
Keep it concise and easy to read.
"""
    response = llm.invoke(prompt)
    return response.content


def run_eligibility_check(age, category, occupation, education):
    """
    Main function the UI will call. Takes raw answers, runs the full pipeline,
    and returns both the structured results and the LLM's friendly explanation.
    """
    profile = collect_profile_from_answers(age, category, occupation, education)
    results = check_eligibility(profile)
    explanation = explain_results_with_llm(profile, results)

    return {
        "profile": profile,
        "raw_results": results,
        "explanation": explanation
    }


# Quick manual test — only runs if you execute this file directly
if __name__ == "__main__":
    result = run_eligibility_check(
        age=25,
        category="obc",
        occupation="entrepreneur",
        education="8th pass"
    )
    print("---- Explanation from AI ----")
    print(result["explanation"])