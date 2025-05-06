import os
import json
import time
from http.server import BaseHTTPRequestHandler
import urllib.parse
from config import PROBLEM_STATEMENT
from report_builder import generate_html_report
from analysis_levels import get_analysis_config

class FormHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, analyzer=None, **kwargs):
        self.analyzer = analyzer
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/style.css':
            # Serve CSS file
            css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.css")
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            with open(css_path, 'rb') as f:
                self.wfile.write(f.read())
        elif self.path == '/reset':
            # Return a clean form without any generated content
            results = {
                "problem": PROBLEM_STATEMENT,  # Reset to default problem
                "domains": [],
                "cause_trees": [],
                "solutions": []
            }
            
            # Generate fresh HTML content
            report_path = generate_html_report(results)
            
            # Read the generated HTML and serve it
            with open(report_path, 'r') as f:
                html_content = f.read()
                
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode())
        else:
            # Serve the main HTML page
            # Generate report data
            results = {
                "problem": PROBLEM_STATEMENT,
                "domains": [],
                "cause_trees": [],
                "solutions": []
            }
            
            # Generate HTML content
            report_path = generate_html_report(results)
            
            # Read the generated HTML file and serve it
            with open(report_path, 'r') as f:
                html_content = f.read()
                
            # Serve the HTML directly
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode())
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        form_data = urllib.parse.parse_qs(post_data)
        
        # Extract the problem statement from the form
        new_problem = form_data.get('problem', [PROBLEM_STATEMENT])[0]
        
        # Extract the analysis level
        analysis_level = form_data.get('analysis_level', ['balanced'])[0]
        
        # Validate character count
        if len(new_problem) < 75 or len(new_problem) > 300:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Problem statement must be between 75 and 300 characters.')
            return
        
        print(f"Problem statement: {new_problem}")
        print(f"Analysis level: {analysis_level}")
        
        # Configure analysis parameters based on selected level
        config = get_analysis_config(analysis_level)
        
        # Run the analysis with progress indicators and configuration
        print("\nAnalyzing problem...\n")
        results = self.analyzer.analyze_problem(new_problem, config)
        
        # Generate HTML report
        print("\nGenerating HTML report...")
        report_path = generate_html_report(results)
        
        # Print a summary to the console
        print("\n=== ANALYSIS COMPLETE ===")
        print(f"- Problem: {new_problem}")
        print(f"- Domains: {', '.join(results['domains'])}")
        print(f"- Root causes identified: {len(results['cause_trees'])}")
        print(f"- Solutions generated: {len(results['solutions'])}")
        
        # Read the generated HTML file and serve it
        with open(report_path, 'r') as f:
            html_content = f.read()
        
        html_content = html_content.replace('</body>', '''
        <script>
        // Hide the processing overlay if it exists
        if (window.hideProcessingOverlay) {
            window.hideProcessingOverlay();
        }
        </script>
        </body>''')
        
        # Serve the HTML directly
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
