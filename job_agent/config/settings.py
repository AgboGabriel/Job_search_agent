
# Agent credentials (change these for your environment)
AGENT_JID = "skillscout@localhost"
AGENT_PASSWORD = "password"

# XMPP server settings (for local development)
XMPP_SERVER = "localhost"
XMPP_PORT = 5222

# File paths
SAMPLE_JOBS_PATH = "data/sample_jobs.json"
USER_PROFILES_PATH = "data/user_profiles.json"
LEARNING_RESOURCES_PATH = "data/learning_resources.json"

# Match score thresholds
MINIMUM_MATCH_SCORE = 60  # Below this, jobs won't be shown
GOOD_MATCH_SCORE = 80      # Above this, highlight as strong match
EXCELLENT_MATCH_SCORE = 90 # Above this, send immediate alert

# Behavior periods (in seconds)
SEARCH_PERIOD = 60  # Check for new jobs every 60 seconds (for demo)
LEARNING_ANALYSIS_PERIOD = 300  # Analyze patterns every 5 minutes
REPORTING_PERIOD = 86400  # Send daily digest (24 hours)

# Learning resources
LEARNING_RESOURCES = {
    "cmake": [
        {"name": "CMake for Qt Developers", "url": "https://qt.io/learn/cmake", "duration": "3 hours", "cost": "free"},
        {"name": "Modern CMake", "url": "https://cliutils.gitlab.io/modern-cmake/", "duration": "2 hours", "cost": "free"}
    ],
    "qml": [
        {"name": "QML for Beginners", "url": "https://qt.io/learn/qml", "duration": "4 hours", "cost": "free"},
        {"name": "QML Advanced", "url": "https://udemy.com/qml-advanced", "duration": "10 hours", "cost": "$20"}
    ],
    "python_backend": [
        {"name": "Flask Mega-Tutorial", "url": "https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial", "duration": "15 hours", "cost": "free"},
        {"name": "FastAPI Course", "url": "https://fastapi.tiangolo.com/learn/", "duration": "5 hours", "cost": "free"}
    ],
    "sql": [
        {"name": "SQL for Beginners", "url": "https://sqlbolt.com/", "duration": "2 hours", "cost": "free"},
        {"name": "Advanced SQL", "url": "https://mode.com/sql-tutorial/", "duration": "4 hours", "cost": "free"}
    ],
    "machine_learning": [
        {"name": "Machine Learning Crash Course", "url": "https://developers.google.com/machine-learning/crash-course", "duration": "15 hours", "cost": "free"},
        {"name": "Fast.ai Practical Deep Learning", "url": "https://course.fast.ai/", "duration": "20 hours", "cost": "free"}
    ]
}

# Message templates
WELCOME_MESSAGE = """
Hello {name}! I'm your SkillScout agent. I've received your profile and will help you find jobs that match your actual skills.

I'll start by asking a few questions to understand your preferences better. Then I'll scan job platforms daily and alert you when I find good matches.

Let's get started!
"""

PROFILE_COMPLETE_MESSAGE = """
Great! Your profile is now complete. I'll start searching for jobs matching:
- Primary focus: {focus}
- Industries: {industries}
- Work arrangement: {arrangement}

You'll hear from me within 24-48 hours with your first matches.
"""