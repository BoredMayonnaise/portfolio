"""Single source of truth for the 90-Second Brief questionnaire.

Supports branching:
- Step 1 (Fork): respondents select whether they want to streamline an existing
  workflow (Track A) or build a new web application / digital product (Track B).
- Steps 2-7: 6 tailored questions for the chosen track.
- Step 8: Email capture for the initial assessment and next steps.

The wizard frontend reads this via the `brief_questions_json` template tag;
`BriefForm` validates submissions against it. Edit questions here only.
"""

TRACK_OPERATIONAL = "Streamline or automate an existing workflow"
TRACK_PRODUCT = "Build a new web application or digital product"

FORK_QUESTION = {
    "id": "track",
    "question": "What brings you here today?",
    "options": [
        TRACK_OPERATIONAL,
        TRACK_PRODUCT,
    ],
}

# Track A: Operational & Workflow Problem Solving
TRACK_A_QUESTIONS = [
    {
        "id": "business_type",
        "question": "What type of business do you operate?",
        "options": [
            "Restaurant / Food Service",
            "Retail",
            "Manufacturing",
            "Trading / Distribution",
            "Logistics",
            "Professional Services",
            "Other",
        ],
    },
    {
        "id": "biggest_problem",
        "question": "What is the biggest problem in your business right now?",
        "options": [
            "Too much manual work",
            "Slow operations",
            "Frequent mistakes",
            "Inventory problems",
            "Poor reporting / visibility",
            "Customer service problems",
            "Employee workflow problems",
            "Something else",
        ],
    },
    {
        "id": "problem_area",
        "question": "Where does this problem happen?",
        "multi": True,
        "options": [
            "Sales",
            "Operations",
            "Inventory",
            "Purchasing",
            "Finance / Accounting",
            "Customer Service",
            "HR / Employees",
            "Across multiple departments",
        ],
    },
    {
        "id": "current_handling",
        "question": "How is this process currently handled?",
        "options": [
            "Paper / handwritten",
            "Excel / Google Sheets",
            "Messaging apps",
            "Existing software",
            "Multiple disconnected systems",
            "Mostly manual",
            "I'm not sure",
        ],
    },
    {
        "id": "impact",
        "question": "What impact is the problem having?",
        "multi": True,
        "options": [
            "Wasting employee time",
            "Losing sales",
            "Increasing costs",
            "Creating mistakes",
            "Delaying customers/orders",
            "Making management difficult",
            "Preventing the business from growing",
        ],
    },
    {
        "id": "urgency",
        "question": "How urgent is this problem?",
        "options": [
            "I need it fixed now",
            "Within 1-3 months",
            "Within 3-6 months",
            "I'm researching possible solutions",
        ],
    },
]

# Track B: New Web Application / Digital Product Build
TRACK_B_QUESTIONS = [
    {
        "id": "app_type",
        "question": "What kind of application or digital product are you planning?",
        "options": [
            "Client portal / customer dashboard",
            "SaaS / subscription platform",
            "Internal tool / custom management system",
            "Interactive web application",
            "Bespoke website & content system",
            "Something else",
        ],
    },
    {
        "id": "project_stage",
        "question": "What stage is the project in right now?",
        "options": [
            "Early concept / idea phase",
            "Specifications or wireframes drafted",
            "Designs & UI ready, needs engineering",
            "Rebuilding or modernizing an existing system",
            "Ready to start immediately",
        ],
    },
    {
        "id": "target_users",
        "question": "Who will be using this product?",
        "multi": True,
        "options": [
            "Paying customers / clients",
            "Internal team / employees",
            "Business partners / vendors",
            "General public / online community",
        ],
    },
    {
        "id": "key_priorities",
        "question": "What are the most critical priorities for this build?",
        "multi": True,
        "options": [
            "Thoughtful UI & crafted design",
            "Fast performance & clean architecture",
            "Data privacy & rigorous security",
            "Complex workflows & custom logic",
            "Rapid launch / MVP to test the market",
        ],
    },
    {
        "id": "tech_foundation",
        "question": "What technical foundation or assets are in place?",
        "options": [
            "Starting fresh from scratch",
            "Existing API, database, or backend to integrate",
            "Existing codebase to refactor or extend",
            "Brand guidelines & design assets ready",
            "Open to recommendations / not sure yet",
        ],
    },
    {
        "id": "timeline",
        "question": "What is your target timeline for this project?",
        "options": [
            "As soon as possible",
            "Within 1–3 months",
            "Within 3–6 months",
            "Flexible / exploring possibilities",
        ],
    },
]

# Backwards compatibility and combined question sets
BRIEF_QUESTIONS = [FORK_QUESTION] + TRACK_A_QUESTIONS
ALL_BRIEF_QUESTIONS = [FORK_QUESTION] + TRACK_A_QUESTIONS + TRACK_B_QUESTIONS

BRIEF_EMAIL_STEP = "Where should we send your initial assessment?"
BRIEF_CTA = "Get my initial assessment →"


def get_questions_for_track(track_value):
    """Return [FORK_QUESTION] + track-specific questions for a given track value."""
    if track_value == TRACK_PRODUCT:
        return [FORK_QUESTION] + TRACK_B_QUESTIONS
    return [FORK_QUESTION] + TRACK_A_QUESTIONS


def get_questions_for_answers(answers):
    """Return the applicable questions list given a dictionary of answers."""
    track = answers.get("track") if isinstance(answers, dict) else None
    return get_questions_for_track(track)
