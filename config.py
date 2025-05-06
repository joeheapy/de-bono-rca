import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API key settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Problem statement
PROBLEM_STATEMENT = "Low-income families in the United Kingdom face significant challenges accessing and affording fresh, nutritious foods. This problem creates and perpetuates health disparities, reduces quality of life, and imposes substantial long-term costs on individuals, communities, and healthcare systems."

# API and processing parameters
NUM_DOMAINS = 3
NUM_INITIAL_CAUSES = 2
ROOT_CAUSE_DEPTH = 1
MAX_LEAF_CAUSES = 2
SOLUTIONS_PER_DOMAIN = 1
API_REQUEST_TIMEOUT = 30
API_CALL_DELAY = 0.8

# LLM temperature settings
ANALYST_TEMPERATURE = 0.3
CHALLENGER_TEMPERATURE = 0.8
EVALUATOR_TEMPERATURE = 0.2
DOMAIN_TEMPERATURE = 0.9

# HTML styling variables
HTML_STYLE = {
    "primary_color": "#15263C",  # Dark blue
    "secondary_color": "#A0D7E4", # Light blue
    "accent_color": "#0071bc",   # Blue accent
    "text_color": "#2e3132",     # Dark gray for text
    "light_gray": "#ffffff",     # White for content sections
    "mid_gray": "#e6e6e6",       # Borders
    "dark_gray": "#6d6e71"       # Secondary text
}