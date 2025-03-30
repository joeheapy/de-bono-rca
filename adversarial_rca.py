import os
from typing import List, Dict, Any
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
import numpy as np
import json
from dotenv import load_dotenv
import time
import webbrowser
from datetime import datetime
import html

# Problem statement
PROBLEM_STATEMENT = "Low-income families in the United Kingdom face significant challenges accessing and affording fresh, nutritious foods. This problem creates and perpetuates health disparities, reduces quality of life, and imposes substantial long-term costs on individuals, communities, and healthcare systems:"

# API and processing parameters
NUM_DOMAINS = 1                  # Number of knowledge domains to generate for inspiration
NUM_INITIAL_CAUSES = 1           # Number of initial causes to identify
ROOT_CAUSE_DEPTH = 1             # Number of times to ask 'why'
MAX_LEAF_CAUSES = 1              # Max number of leaf causes to generate solutions for
SOLUTIONS_PER_DOMAIN = 1         # Generate multiple solutions per domain
API_REQUEST_TIMEOUT = 30         # Timeout for API calls in seconds
API_CALL_DELAY = 1               # Delay between API calls in seconds

# LLM temperature settings (higher = more creative, lower = more focused)
ANALYST_TEMPERATURE = 0.3        # For analytical tasks (identifying causes)
CHALLENGER_TEMPERATURE = 0.8     # For creative solutions
EVALUATOR_TEMPERATURE = 0.2      # For evaluation
DOMAIN_TEMPERATURE = 0.9         # For generating diverse domains

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

class LateralThinkingEnhanced:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get the OpenAI API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
        # Set the OpenAI API key
        os.environ["OPENAI_API_KEY"] = api_key
        
        # Initialize different language models with timeouts
        self.analyst_llm = OpenAI(temperature=ANALYST_TEMPERATURE, request_timeout=API_REQUEST_TIMEOUT)
        self.challenger_llm = OpenAI(temperature=CHALLENGER_TEMPERATURE, request_timeout=API_REQUEST_TIMEOUT)
        self.evaluator_llm = OpenAI(temperature=EVALUATOR_TEMPERATURE, request_timeout=API_REQUEST_TIMEOUT)
        self.domain_llm = OpenAI(temperature=DOMAIN_TEMPERATURE, request_timeout=API_REQUEST_TIMEOUT)
    
    def generate_random_domains(self, num_domains: int = NUM_DOMAINS) -> List[str]:
        """Generate random knowledge domains for cross-pollination of ideas"""
        
        domain_prompt = PromptTemplate(
            input_variables=[],
            template=f"""Generate {num_domains} specific knowledge domains or fields.
            
            These should be diverse across different areas of human knowledge.
            Format each as a concise domain name (1-4 words) with NO numbering or bullets.
            """
        )
        
        # Use pipe operator instead of LLMChain
        domains_chain = domain_prompt | self.domain_llm
        try:
            domains_result = domains_chain.invoke({})
            domains = [domain.strip() for domain in domains_result.strip().split('\n') if domain.strip()]
            return domains[:num_domains]
        except Exception as e:
            print(f"Error generating domains: {e}")
            return ["Biology", "Magical Realism", "Game Theory", "Neuroscience", "Mycology"]  # Fallback domains
    
    def identify_initial_causes(self, problem: str, num_causes: int = NUM_INITIAL_CAUSES) -> List[str]:
        """Identify the initial set of potential root causes for the problem"""
        
        cause_prompt = PromptTemplate(
            input_variables=["problem", "num_causes"],
            template="""For the problem: '{problem}'

Identify EXACTLY {num_causes} potential root cause(s) that might be contributing to the problem.
Do NOT provide more than {num_causes} cause(s).
Format the cause as a clear, concise statement without numbering.
"""
        )
        
        # Use pipe operator
        cause_chain = cause_prompt | self.analyst_llm
        try:
            causes_result = cause_chain.invoke({"problem": problem, "num_causes": num_causes})
            causes = [cause.strip() for cause in causes_result.strip().split('\n') if cause.strip()]
            # Add this right before returning causes:
            if len(causes) > num_causes:
                causes = causes[:num_causes]  # Take only the first num_causes items
            return causes
        except Exception as e:
            print(f"Error identifying causes: {e}")
            return ["Market prioritizes profit over social needs", "Regulatory barriers"]
    
    def dig_deeper(self, problem: str, cause: str, depth: int = ROOT_CAUSE_DEPTH) -> Dict[str, Any]:
        """Recursively ask 'why' to dig deeper into root causes"""
        
        if depth <= 0:
            return {"cause": cause, "children": []}
        
        why_prompt = PromptTemplate(
            input_variables=["problem", "cause"],
            template="""For the problem: '{problem}'
            Given the potential cause: '{cause}'
            Ask why this cause exists. Identify 2 deeper underlying causes that might explain why '{cause}' is happening.
            """
        )
        
        # Use pipe operator
        why_chain = why_prompt | self.analyst_llm
        
        try:
            sub_causes_result = why_chain.invoke({"problem": problem, "cause": cause})
            sub_causes = [sc.strip() for sc in sub_causes_result.strip().split('\n') if sc.strip()]
            sub_causes = sub_causes[:2]  # Limit to 2 sub-causes to reduce API calls
            
            # Add delay to avoid rate limiting
            time.sleep(API_CALL_DELAY)
            
            # Build the tree recursively with reduced complexity
            children = []
            for sub_cause in sub_causes:
                child_tree = self.dig_deeper(problem, sub_cause, depth - 1)
                children.append(child_tree)
            
            return {"cause": cause, "children": children}
        except Exception as e:
            print(f"Error in dig_deeper for cause '{cause}': {e}")
            return {"cause": cause, "children": []}
    
    def challenge_assumptions(self, problem: str, cause_tree: Dict[str, Any], domains: List[str]) -> List[Dict[str, Any]]:
        """Generate solutions using metaphor-based lateral thinking"""
        
        # Extract leaf nodes (deepest causes)
        def extract_leaf_nodes(node):
            if not node["children"]:
                return [node["cause"]]
            leaves = []
            for child in node["children"]:
                leaves.extend(extract_leaf_nodes(child))
            return leaves
        
        leaf_causes = extract_leaf_nodes(cause_tree)
        # Limit to configured max leaf causes
        if len(leaf_causes) > MAX_LEAF_CAUSES:
            leaf_causes = leaf_causes[:MAX_LEAF_CAUSES]
            
        solutions = []
        
        for leaf_cause in leaf_causes:
            # Use ALL domains instead of just the first one
            for domain in domains:
                # Generate multiple solutions per domain-cause pair
                for solution_num in range(1, SOLUTIONS_PER_DOMAIN + 1):
                    # STEP 1: Generate a powerful metaphor from the domain
                    metaphor_prompt = PromptTemplate(
                        input_variables=["domain"],
                        template="""From the domain of '{domain}', generate a powerful, unexpected metaphor or conceptual model.
                        
                        Choose something non-obvious that could provide a fresh perspective on other problems.
                        Explain the key dynamics, patterns, or principles that make this metaphor interesting.
                        
                        Format as:
                        METAPHOR: [The metaphor/model from {domain}]
                        DYNAMICS: [How this system/pattern works]
                        """
                    )
                    
                    try:
                        # Generate the metaphor first
                        metaphor_chain = metaphor_prompt | self.challenger_llm
                        metaphor_response = metaphor_chain.invoke({"domain": domain})
                        
                        # Add delay to avoid rate limiting
                        time.sleep(API_CALL_DELAY)
                        
                        # STEP 2: Apply the metaphor to generate a creative solution
                        solution_prompt = PromptTemplate(
                            input_variables=["problem", "cause", "metaphor", "solution_num"],
                            template="""For the problem: '{problem}'
                            Addressing this root cause: '{cause}'
                            
                            Consider this metaphor:
                            {metaphor}
                            
                            For solution #{solution_num}, create an innovative solution by applying this metaphor to the problem.
                            Think of how the dynamics in this metaphor could inspire a completely new approach to addressing the root cause.
                            Be bold, imaginative, and avoid conventional thinking.
                            
                            ONLY Format your response as:
                            SOLUTION TITLE: [A concise, marketable title for your solution - max 5 words]
                            METAPHORICAL INSIGHT: [How the metaphor reveals a new perspective]
                            CREATIVE SOLUTION: [Detailed explanation of an idea inspired by the metaphor]
                            IMPLEMENTATION: [A practical business model and service design including the reason to invest]
                            """
                        )
                        
                        # Use the metaphor to generate the solution
                        solution_chain = solution_prompt | self.challenger_llm
                        solution_response = solution_chain.invoke({
                            "problem": problem,
                            "cause": leaf_cause,
                            "metaphor": metaphor_response,
                            "solution_num": solution_num
                        })
                        
                        # Store both the metaphor and the solution
                        solution = {
                            "root_cause": leaf_cause,
                            "type": "domain_inspired",
                            "domain": domain,
                            "solution_number": solution_num,
                            "metaphor": metaphor_response,
                            "content": solution_response,
                            "scores": {"overall": 5.0}  # Default score, will be replaced
                        }
                        solutions.append(solution)
                        
                        # Add delay to avoid rate limiting
                        time.sleep(API_CALL_DELAY)
                        
                    except Exception as e:
                        print(f"Error generating metaphorical solution for {domain}: {e}")
        
        return solutions
    
    def evaluate_solutions(self, problem: str, solutions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluate and score each solution on multiple dimensions"""
        print("5. Evaluating solutions...")
        
        for i, solution in enumerate(solutions):
            print(f"   Evaluating solution {i+1}/{len(solutions)}...")
            
            evaluation_prompt = PromptTemplate(
                input_variables=["problem", "root_cause", "solution_content"],
                template="""For the problem: '{problem}'
                And root cause: '{root_cause}'
                Evaluate this solution:
                
                {solution_content}
                
                Score the solution on a scale of 1-10 for:
                1. Novelty - how innovative and unique
                2. Feasibility - how practical to implement
                3. Impact - potential effectiveness
                4. Relevance - how well it addresses the root cause
                
                Format your response as:
                NOVELTY: [score]
                FEASIBILITY: [score]
                IMPACT: [score]
                RELEVANCE: [score]
                OVERALL: [average score]
                """
            )
            
            try:
                # Generate evaluation
                eval_chain = evaluation_prompt | self.evaluator_llm
                eval_result = eval_chain.invoke({
                    "problem": problem,
                    "root_cause": solution["root_cause"],
                    "solution_content": solution["content"]
                })
                
                # Parse scores (without feedback)
                scores = self._parse_evaluation(eval_result)
                solution["scores"] = scores
                
                # Add delay to avoid rate limiting
                time.sleep(API_CALL_DELAY)
                
            except Exception as e:
                print(f"Error evaluating solution: {e}")
                # Keep default scores if evaluation fails
        
        # Sort solutions by overall score
        return sorted(solutions, key=lambda x: x["scores"].get("overall", 0), reverse=True)

    def _parse_evaluation(self, eval_text: str) -> Dict[str, Any]:
        """Parse evaluation results into a structured format"""
        scores = {
            "novelty": 0,
            "feasibility": 0,
            "impact": 0,
            "relevance": 0,
            "overall": 0
        }
        
        # Extract scores using simple parsing
        lines = eval_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith("NOVELTY:"):
                try:
                    scores["novelty"] = float(line.split("NOVELTY:")[1].strip())
                except:
                    pass
            elif line.startswith("FEASIBILITY:"):
                try:
                    scores["feasibility"] = float(line.split("FEASIBILITY:")[1].strip())
                except:
                    pass
            elif line.startswith("IMPACT:"):
                try:
                    scores["impact"] = float(line.split("IMPACT:")[1].strip())
                except:
                    pass
            elif line.startswith("RELEVANCE:"):
                try:
                    scores["relevance"] = float(line.split("RELEVANCE:")[1].strip())
                except:
                    pass
            elif line.startswith("OVERALL:"):
                try:
                    scores["overall"] = float(line.split("OVERALL:")[1].strip())
                except:
                    pass
        
        # Calculate overall score if not provided
        if scores["overall"] == 0 and (scores["novelty"] + scores["feasibility"] + scores["impact"] + scores["relevance"] > 0):
            scores["overall"] = (scores["novelty"] + scores["feasibility"] + scores["impact"] + scores["relevance"]) / 4
        
        return scores

    def _parse_solution_content(self, content: str) -> Dict[str, str]:
        """Parse solution content into structured sections including title"""
        sections = {
            "title": "",
            "insight": "",
            "solution": "",
            "implementation": "",
            "other": ""
        }
        
        # Normalize line endings and ensure proper handling of the content
        full_content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # First check for the solution title
        if "SOLUTION TITLE:" in full_content:
            parts = full_content.split("SOLUTION TITLE:", 1)
            # If there's content before the title, save it as other
            if parts[0].strip():
                sections["other"] = parts[0].strip()
            
            remaining = parts[1]
            
            # Extract title section
            if "METAPHORICAL INSIGHT:" in remaining:
                title_parts = remaining.split("METAPHORICAL INSIGHT:", 1)
                sections["title"] = title_parts[0].strip()
                remaining = "METAPHORICAL INSIGHT:" + title_parts[1]  # Add the header back for next split
            else:
                sections["title"] = remaining.strip()
                remaining = ""
        else:
            # If no title found, continue with the regular parsing
            remaining = full_content
        
        # Continue with existing parsing logic
        if "METAPHORICAL INSIGHT:" in remaining:
            parts = remaining.split("METAPHORICAL INSIGHT:", 1)
            # If there's content before the insight and no title was found, it goes to other
            if parts[0].strip() and not sections["title"] and not sections["other"]:
                sections["other"] = parts[0].strip()
            
            remaining = parts[1]
            
            # Extract insight section
            if "CREATIVE SOLUTION:" in remaining:
                insight_parts = remaining.split("CREATIVE SOLUTION:", 1)
                sections["insight"] = insight_parts[0].strip()
                remaining = insight_parts[1]
            else:
                sections["insight"] = remaining.strip()
                remaining = ""
            
            # Extract solution section
            if "IMPLEMENTATION:" in remaining:
                solution_parts = remaining.split("IMPLEMENTATION:", 1)
                sections["solution"] = solution_parts[0].strip()
                # Everything after IMPLEMENTATION: is the implementation section
                sections["implementation"] = solution_parts[1].strip()
            elif remaining:
                sections["solution"] = remaining.strip()
        else:
            # If no section headers found, put everything in other
            if not sections["other"]:  # Only if other doesn't already have content
                sections["other"] = remaining.strip()
        
        return sections

    def analyze_problem(self, problem: str) -> Dict[str, Any]:
        """Complete analysis with evaluation"""
        print("1. Generating knowledge domains...")
        domains = self.generate_random_domains(NUM_DOMAINS)
        
        print("2. Identifying initial causes...")
        initial_causes = self.identify_initial_causes(problem, NUM_INITIAL_CAUSES)
        
        print("3. Building root cause trees...")
        cause_trees = []
        for i, cause in enumerate(initial_causes):
            print(f"   Analyzing cause {i+1}/{len(initial_causes)}: {cause[:30]}...")
            tree = self.dig_deeper(problem, cause, depth=ROOT_CAUSE_DEPTH)
            cause_trees.append(tree)
        
        print("4. Generating solutions...")
        all_solutions = []
        for i, tree in enumerate(cause_trees):
            print(f"   Generating solutions for tree {i+1}/{len(cause_trees)}...")
            solutions = self.challenge_assumptions(problem, tree, domains)
            all_solutions.extend(solutions)
        
        # Add evaluation step
        evaluated_solutions = self.evaluate_solutions(problem, all_solutions)
        
        return {
            "problem": problem,
            "domains": domains,
            "cause_trees": cause_trees,
            "solutions": evaluated_solutions  # Now sorted by score
        }
    
    def visualize_tree(self, tree, indent=0):
        """Pretty print the root cause tree"""
        print("  " * indent + f"- {tree['cause']}")
        for child in tree['children']:
            self.visualize_tree(child, indent + 1)
            
    def print_solution(self, solution):
        """Format and print a solution"""
        print(f"\n[Solution for Root Cause: {solution['root_cause']}]")
        print(f"Type: {solution['type']}")
        
        if solution['type'] == 'domain_inspired':
            print(f"Inspiration Domain: {solution['domain']}")
            
        print("\nContent:")
        print(solution['content'])
        print("-" * 80)

    def generate_html_report(self, results: Dict[str, Any]) -> str:
        """Generate an HTML report styled with external CSS"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create HTML content with a link to the external stylesheet
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>De Bono Thinking: {html.escape(results['problem'])}</title>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Text&family=Lexend:wght@300;400&display=swap" rel="stylesheet">
            <link rel="stylesheet" href="style.css">
        </head>
        <body>
            <div class="top-bar"></div>
            <header class="header">
                <div class="header-content">
                    <a href="#" class="logo">De Bono Lateral Thinking</a>
                    <div class="timestamp">Generated on: {timestamp}</div>
                </div>
            </header>

            <div class="hero">
                <div class="hero-content">
                    <h1>Problem statement</h1>
                    <p>{html.escape(results['problem'])}</p>
                </div>
            </div>

            <div class="main-container">
                <section>
                    <h2>Systemic Root Causes</h2>
                    <p class="section-intro">By repeatedly asking "why," we identify deeper systemic causes behind the affordable housing crisis. Each branch explores a different causal pathway.</p>
        """
        
        # Add root cause trees
        for i, tree in enumerate(results['cause_trees'], 1):
            html_content += f'<div class="cause-tree">\n<h3>Root Cause {html.escape(tree["cause"])}</h3>\n'
            html_content += self._tree_to_html(tree)
            html_content += '</div>\n'
        
        html_content += """
                </section>
                
                <section>
                    <h2>Knowledge Domains</h2>
                    <p class="section-intro">These domains provide cross-disciplinary inspiration for innovative solutions, encouraging lateral thinking that breaks conventional problem-solving patterns.</p>
                    <div class="domains-section">
        """
        
        # Add domains
        for domain in results['domains']:
            html_content += f'<div class="domain-tag">{html.escape(domain)}</div>\n'
        
        html_content += """
                    </div>
                </section>

                <section>
                    <h2>Innovative Solutions</h2>
                    <p class="section-intro">These solutions draw inspiration from diverse knowledge domains to tackle the affordable housing crisis. Each solution addresses specific root causes identified in our analysis.</p>
                    <div class="solutions-grid">
        """
        
        # Add solutions
        for i, solution in enumerate(results['solutions'], 1):
            overall_score = solution['scores'].get('overall', 0)
            
            # Parse solution content into sections (do this earlier to get the title)
            sections = self._parse_solution_content(solution['content'])
            
            # Get the title or use a default
            solution_title = sections.get('title', '').strip()
            display_title = f" - {solution_title}" if solution_title else ""
            
            html_content += f'''
                        <div class="solution-card">
                            <h3>Solution {i}{display_title} (Score: {overall_score:.1f}/10)</h3>
                            <div class="tags-container">
                                <div class="solution-type">Based on: {html.escape(solution['root_cause'][:40])}{"..." if len(solution['root_cause']) > 40 else ""}</div>
                    '''
            
            if solution['type'] == 'domain_inspired':
                html_content += f'<div class="domain-inspiration">Inspired by: {html.escape(solution["domain"])}</div>'


            
            # Close the tags-container properly, then start the score-grid on a new line
            html_content += f'''
                            </div>
                            
                            <div class="score-grid">
                    '''
            
            html_content += f'''
                                <div class="score-item">
                                    <div class="score-label">Novelty:</div>
                                    <div class="score-value">{solution['scores'].get('novelty', 'N/A')}</div>
                                </div>
                                <div class="score-item">
                                    <div class="score-label">Feasibility:</div>
                                    <div class="score-value">{solution['scores'].get('feasibility', 'N/A')}</div>
                                </div>
                                <div class="score-item">
                                    <div class="score-label">Impact:</div>
                                    <div class="score-value">{solution['scores'].get('impact', 'N/A')}</div>
                                </div>
                                <div class="score-item">
                                    <div class="score-label">Relevance:</div>
                                    <div class="score-value">{solution['scores'].get('relevance', 'N/A')}</div>
                                </div>
                            </div>
                    '''
            
            html_content += f'''
                            <div class="solution-content">
                                <div class="solution-section">
                                    <div class="section-title">Domain Insight</div>
                                    <div class="section-content">{html.escape(sections['insight'])}</div>
                                </div>
                                
                                <div class="solution-section">
                                    <div class="section-title">Creative Step</div>
                                    <div class="section-content">{html.escape(sections['solution'])}</div>
                                </div>
                                
                                <div class="solution-section">
                                    <div class="section-title">Investment Opportunity</div>
                                    <div class="section-content">{html.escape(sections['implementation'])}</div>
                                </div>
                                
                                {f'<div class="solution-section"><div class="section-content">{html.escape(sections["other"])}</div></div>' if sections["other"] else ''}
                            </div>
                        </div>
                    '''
            
        html_content += """
                    </div>
                </section>
            </div>

            <footer>
                <div class="footer-content">
                    <div class="footer-logo">De Bono Lateral Thinking</div>
                    <p>&copy; <script>document.write(new Date().getFullYear())</script> Your Company Name. All rights reserved. </p>
                    <p class="footer-text"></p>
                </div>
            </footer>
        </body>
        </html>
        """
        
        # Save the HTML content to a file
        report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rca_report.html")
        with open(report_path, 'w') as f:
            f.write(html_content)
        
        return report_path

    def _tree_to_html(self, tree, level=0):
        """Helper method to convert a cause tree to HTML"""
        html_content = f'<div style="margin-left: {level*20}px">\n'
        html_content += f'<p><strong>{html.escape(tree["cause"])}</strong></p>\n'
        
        if tree['children']:
            html_content += '<div class="cause-node">\n'
            for child in tree['children']:
                html_content += self._tree_to_html(child, level + 1)
            html_content += '</div>\n'
        
        html_content += '</div>\n'
        return html_content

def main():
    # Initialize the analyzer
    analyzer = LateralThinkingEnhanced()
    
    # Use the default problem statement
    problem = PROBLEM_STATEMENT
    print(f"Problem statement: {problem}")
    
    # Run the analysis with progress indicators
    print("\nAnalyzing problem...\n")
    results = analyzer.analyze_problem(problem)
    
    # Generate HTML report and open in browser
    print("\nGenerating HTML report...")
    report_path = analyzer.generate_html_report(results)
    
    print(f"Opening report in browser: {report_path}")
    webbrowser.open('file://' + report_path)
    
    # Also print a summary to the console
    print("\n=== ANALYSIS COMPLETE ===")
    print(f"- Problem: {problem}")
    print(f"- Domains: {', '.join(results['domains'])}")
    print(f"- Root causes identified: {len(results['cause_trees'])}")
    print(f"- Solutions generated: {len(results['solutions'])}")
    print(f"- Full report available at: {report_path}")

if __name__ == "__main__":
    main()