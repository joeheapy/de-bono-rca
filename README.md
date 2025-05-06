De Bono Lateral Thinking Tool
A powerful AI-powered lateral thinking application that helps identify root causes and generate innovative solutions for complex problems using cross-domain inspiration.

🧠 Overview
This tool applies Edward de Bono's lateral thinking principles combined with modern AI to help users analyze problems more deeply and generate creative solutions. By systematically exploring root causes and borrowing KEY_IDEAs from diverse knowledge domains, it breaks conventional thinking patterns and promotes innovation.

✨ Key Features
Root Cause Analysis: Recursively asks "why" to dig deeper into systemic causes
Cross-Domain Inspiration: Generates solutions inspired by concepts from diverse fields
Solution Evaluation: Scores solutions on novelty, feasibility, impact, and relevance
Clean Visualization: Presents findings in an intuitive, well-structured HTML report

🔍 How It Works
Problem Definition: Enter a clear problem statement (75-300 characters)
Root Cause Identification: The system analyzes your problem and identifies potential root causes
Causal Exploration: For each root cause, the system builds a tree of deeper causes
Knowledge Domain Generation: Random domains are selected to inspire lateral thinking
Creative Solution Generation: The system creates solutions by applying KEY_IDEAs from these domains
Evaluation: Each solution is scored on multiple dimensions
Results Presentation: A comprehensive report is generated with all findings

🚀 Installation
📋 Usage
A web browser will automatically open with the application interface. Enter your problem statement (minimum 75 characters) and click "Generate Solutions" to begin the analysis.

⚙️ Configuration
The application behavior can be customized by modifying parameters in config.py:

NUM_DOMAINS: Number of knowledge domains to generate (default: 5)
NUM_INITIAL_CAUSES: Number of initial root causes to identify (default: 3)
ROOT_CAUSE_DEPTH: Depth of "why" questions to explore (default: 3)
SOLUTIONS_PER_DOMAIN: Number of solutions per domain (default: 2)
API_REQUEST_TIMEOUT: Timeout for API calls in seconds (default: 30)

🏗️ Architecture
The application follows a clean, modular architecture:

main.py: Entry point and web server
lateral_thinking.py: Core analysis and solution generation logic
evaluation.py: Solution parsing and evaluation utilities
report_builder.py: HTML report generation
form_handler.py: HTTP request handling
config.py: Configuration settings
style.css: Visual styling

🌟 Examples
The default problem statement explores food access challenges for low-income families in the UK:

Try modifying this with your own problem statements!

🎓 About Edward de Bono
This tool is inspired by Edward de Bono's lateral thinking methodology. De Bono was a physician, psychologist, and author known for his work on thinking processes and creativity. His lateral thinking techniques encourage breaking conventional thought patterns to solve problems creatively.

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgements
OpenAI for providing the API that powers the analysis
LangChain for simplifying interactions with language models
Edward de Bono for his groundbreaking work on lateral thinking

"The purpose of lateral thinking is to generate ideas that may not be obtainable by traditional step-by-step logic." - Edward de Bono
