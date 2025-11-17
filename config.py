import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Crawler Configuration
MAX_CONCURRENT_DOWNLOADS = 5
REQUEST_TIMEOUT = 30
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Output Configuration
OUTPUT_DIR = 'output'
EXCEL_FILENAME = 'academic_catalog.xlsx'
JSON_FILENAME = 'academic_catalog.json'

# Subject Classification Categories
SUBJECT_CATEGORIES = [
    "Computer Science",
    "Mathematics",
    "Physics",
    "Chemistry",
    "Biology",
    "Medicine",
    "Engineering",
    "Social Sciences",
    "Economics",
    "Psychology",
    "Education",
    "Literature",
    "History",
    "Philosophy",
    "Law",
    "Business",
    "Environmental Science",
    "Other"
]
