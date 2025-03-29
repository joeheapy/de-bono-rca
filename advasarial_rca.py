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
PROBLEM_STATEMENT = "The United Kingdom faces a significant housing crisis characterized by persistent shortages of affordable homes across the country. This crisis stems from a property market structure that systematically disincentivizes the development of affordable housing through multiple interconnected mechanisms:"

# API and processing parameters
NUM_DOMAINS = 2                  # Number of knowledge domains to generate for inspiration
NUM_INITIAL_CAUSES = 1           # Number of initial causes to identify
ROOT_CAUSE_DEPTH = 2             # Number of times to ask 'why'
MAX_LEAF_CAUSES = 5              # Max number of leaf causes to generate solutions for
SOLUTIONS_PER_DOMAIN = 2         # Generate multiple solutions per domain
API_REQUEST_TIMEOUT = 30         # Kept the same
API_CALL_DELAY = 1               # Kept the same

# LLM temperature settings (higher = more creative, lower = more focused)
ANALYST_TEMPERATURE = 0.3        # For analytical tasks (identifying causes)
CHALLENGER_TEMPERATURE = 0.8     # For creative solutions
EVALUATOR_TEMPERATURE = 0.2      # For evaluation (unused in simplified version)
DOMAIN_TEMPERATURE = 0.9         # For generating diverse domains

# HTML styling variables
HTML_STYLE = {
    "primary_color": "#5829a7",  # JRF purple
    "secondary_color": "#9175c5", # JRF light purple
    "accent_color": "#0071bc",   # JRF blue
    "text_color": "#2e3132",     # Dark gray for text
    "light_gray": "#f7f7f7",     # Background for content sections
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
            return ["Biology", "Magical Realism", "Game Theory", "Neuroscience", "mycology"]  # Fallback domains
    
    def identify_initial_causes(self, problem: str, num_causes: int = NUM_INITIAL_CAUSES) -> List[str]:
        """Identify the initial set of potential root causes for the problem"""
        
        cause_prompt = PromptTemplate(
            input_variables=["problem", "num_causes"],
            template="""For the problem: '{problem}'
            
            Identify {num_causes} potential root causes that might be contributing to the problem.
            Format each root cause as a clear, concise statement.
            """
        )
        
        # Use pipe operator
        cause_chain = cause_prompt | self.analyst_llm
        try:
            causes_result = cause_chain.invoke({"problem": problem, "num_causes": num_causes})
            causes = [cause.strip() for cause in causes_result.strip().split('\n') if cause.strip()]
            return causes
        except Exception as e:
            print(f"Error identifying causes: {e}")
            return ["Market prioritizes profit over social needs", "Regulatory barriers to affordable housing"]
    
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
                            
                            Format your response as:
                            METAPHORICAL INSIGHT: [How the metaphor reveals a new perspective]
                            CREATIVE SOLUTION: [Detailed explanation of your solution]
                            IMPLEMENTATION: [How it would work in practice]
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
                FEEDBACK: [brief critical assessment]
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
                
                # Parse scores and feedback
                scores = self._parse_evaluation(eval_result)
                solution["scores"] = scores
                solution["feedback"] = scores.get("feedback", "")
                
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
            "overall": 0,
            "feedback": ""
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
            elif line.startswith("FEEDBACK:"):
                scores["feedback"] = line.split("FEEDBACK:")[1].strip()
        
        # Calculate overall score if not provided
        if scores["overall"] == 0 and (scores["novelty"] + scores["feasibility"] + scores["impact"] + scores["relevance"] > 0):
            scores["overall"] = (scores["novelty"] + scores["feasibility"] + scores["impact"] + scores["relevance"]) / 4
        
        return scores

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
        """Generate an HTML report styled like JRF website"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Root Cause Analysis: {html.escape(results['problem'])}</title>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
            <style>
                :root {{
                    --jrf-purple: #5829a7;
                    --jrf-purple-dark: #4a1e94;
                    --jrf-purple-light: #9175c5;
                    --jrf-text: #2e3132;
                    --jrf-blue: #0071bc;
                    --jrf-yellow: #ffc845;
                    --jrf-light-gray: #f7f7f7;
                    --jrf-mid-gray: #e6e6e6;
                    --jrf-dark-gray: #6d6e71;
                }}
                
                * {{
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }}
                
                body {{
                    font-family: 'Open Sans', Arial, sans-serif;
                    line-height: 1.6;
                    color: var(--jrf-text);
                    background-color: #fff;
                    margin: 0;
                    padding: 0;
                }}
                
                .top-bar {{
                    background-color: var(--jrf-purple);
                    height: 8px;
                    width: 100%;
                }}
                
                .header {{
                    padding: 20px 5%;
                    background-color: white;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                    position: sticky;
                    top: 0;
                    z-index: 100;
                }}
                
                .header-content {{
                    max-width: 1200px;
                    margin: 0 auto;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                
                .logo {{
                    font-family: 'Poppins', sans-serif;
                    font-weight: 700;
                    font-size: 24px;
                    color: var(--jrf-purple);
                    text-decoration: none;
                }}
                
                .main-container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 40px 5%;
                }}
                
                .hero {{
                    background-color: var(--jrf-purple);
                    color: white;
                    padding: 60px 5%;
                    margin-bottom: 40px;
                }}
                
                .hero-content {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                
                h1, h2, h3, h4 {{
                    font-family: 'Poppins', sans-serif;
                    margin-bottom: 20px;
                    color: var(--jrf-purple);
                }}
                
                .hero h1 {{
                    color: white;
                    font-size: 42px;
                    margin-bottom: 15px;
                    font-weight: 700;
                }}
                
                .hero p {{
                    font-size: 20px;
                    max-width: 800px;
                    margin-bottom: 0;
                }}
                
                h1 {{
                    font-size: 36px;
                    font-weight: 600;
                }}
                
                h2 {{
                    font-size: 28px;
                    font-weight: 600;
                    padding-bottom: 10px;
                    margin-top: 50px;
                    position: relative;
                }}
                
                h2::after {{
                    content: '';
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    width: 60px;
                    height: 4px;
                    background-color: var(--jrf-purple);
                }}
                
                h3 {{
                    font-size: 22px;
                    font-weight: 600;
                    color: var(--jrf-text);
                }}
                
                p {{
                    margin-bottom: 20px;
                }}
                
                .timestamp {{
                    color: var(--jrf-dark-gray);
                    font-size: 14px;
                    text-align: right;
                }}
                
                .domains-section {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                    margin: 30px 0;
                }}
                
                .domain-tag {{
                    background-color: var(--jrf-purple);
                    color: white;
                    padding: 10px 16px;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: 600;
                    display: inline-block;
                    font-family: 'Poppins', sans-serif;
                }}
                
                .cause-tree {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                    border: 1px solid var(--jrf-mid-gray);
                    box-shadow: 0 2px 15px rgba(0,0,0,0.03);
                }}
                
                .cause-tree h3 {{
                    margin-top: 0;
                    color: var(--jrf-purple);
                    border-bottom: 2px solid var(--jrf-mid-gray);
                    padding-bottom: 15px;
                    margin-bottom: 20px;
                }}
                
                .cause-node {{
                    padding-left: 20px;
                    border-left: 3px solid var(--jrf-purple-light);
                    margin-left: 10px;
                    margin-top: 15px;
                    padding-top: 5px;
                    padding-bottom: 5px;
                }}
                
                .cause-node p {{
                    margin-bottom: 10px;
                }}
                
                .solutions-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(min(100%, 580px), 1fr));
                    gap: 30px;
                    margin-top: 30px;
                }}
                
                .solution-card {{
                    background-color: white;
                    border-radius: 8px;
                    padding: 30px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
                    border: 1px solid var(--jrf-mid-gray);
                    display: flex;
                    flex-direction: column;
                    height: 100%;
                }}
                
                .solution-card h3 {{
                    margin-top: 0;
                    color: var(--jrf-purple);
                    font-size: 20px;
                    border-bottom: 2px solid var(--jrf-mid-gray);
                    padding-bottom: 15px;
                    margin-bottom: 15px;
                }}
                
                .tags-container {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 8px;
                    margin-bottom: 15px;
                }}
                
                .solution-type {{
                    background-color: var(--jrf-purple-light);
                    color: white;
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 4px;
                    font-size: 13px;
                    font-weight: 600;
                    font-family: 'Poppins', sans-serif;
                }}
                
                .domain-inspiration {{
                    background-color: var(--jrf-blue);
                    color: white;
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 4px;
                    font-size: 13px;
                    font-weight: 600;
                    font-family: 'Poppins', sans-serif;
                }}
                
                .score-grid {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 15px;
                    margin: 20px 0;
                }}
                
                .score-item {{
                    background-color: var(--jrf-light-gray);
                    padding: 15px;
                    border-radius: 6px;
                }}
                
                .score-label {{
                    font-weight: 600;
                    color: var(--jrf-dark-gray);
                    font-family: 'Poppins', sans-serif;
                    font-size: 13px;
                    margin-bottom: 5px;
                }}
                
                .score-value {{
                    font-size: 22px;
                    font-weight: 700;
                    color: var(--jrf-purple);
                    font-family: 'Poppins', sans-serif;
                }}
                
                .score-bar-container {{
                    height: 6px;
                    background-color: var(--jrf-mid-gray);
                    border-radius: 3px;
                    margin-top: 8px;
                    overflow: hidden;
                }}
                
                .score-bar {{
                    height: 100%;
                    background-color: var(--jrf-purple);
                    border-radius: 3px;
                }}
                
                .feedback-section {{
                    background-color: var(--jrf-light-gray);
                    padding: 20px;
                    border-radius: 6px;
                    margin-bottom: 20px;
                    font-style: italic;
                    border-left: 4px solid var(--jrf-yellow);
                }}
                
                .content-section {{
                    white-space: pre-line;
                    line-height: 1.8;
                    background-color: var(--jrf-light-gray);
                    padding: 20px;
                    border-radius: 6px;
                    margin-top: auto;
                    font-size: 15px;
                }}
                
                .section-intro {{
                    max-width: 800px;
                    margin-bottom: 30px;
                    color: var(--jrf-dark-gray);
                }}
                
                footer {{
                    background-color: var(--jrf-purple);
                    color: white;
                    padding: 50px 5% 30px;
                    margin-top: 60px;
                }}
                
                .footer-content {{
                    max-width: 1200px;
                    margin: 0 auto;
                    text-align: center;
                }}
                
                .footer-logo {{
                    font-family: 'Poppins', sans-serif;
                    font-weight: 700;
                    font-size: 24px;
                    color: white;
                    margin-bottom: 20px;
                    display: inline-block;
                }}
                
                .footer-text {{
                    font-size: 14px;
                    margin-top: 20px;
                    color: rgba(255,255,255,0.8);
                }}
                
                @media (max-width: 768px) {{
                    .hero h1 {{
                        font-size: 32px;
                    }}
                    
                    .hero p {{
                        font-size: 18px;
                    }}
                    
                    h1 {{
                        font-size: 28px;
                    }}
                    
                    h2 {{
                        font-size: 24px;
                    }}
                    
                    .score-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .cause-node {{
                        padding-left: 15px;
                    }}
                }}
            </style>
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
                    <h1>Root Cause Analysis</h1>
                    <p>{html.escape(results['problem'])}</p>
                </div>
            </div>

            <div class="main-container">
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
                    <h2>Systemic Root Causes</h2>
                    <p class="section-intro">By repeatedly asking "why," we identify deeper systemic causes behind the affordable housing crisis. Each branch explores a different causal pathway.</p>
        """
        
        # Add root cause trees
        for i, tree in enumerate(results['cause_trees'], 1):
            html_content += f'<div class="cause-tree">\n<h3>Root Cause {i}</h3>\n'
            html_content += self._tree_to_html(tree)
            html_content += '</div>\n'
        
        html_content += """
                </section>

                <section>
                    <h2>Innovative Solutions</h2>
                    <p class="section-intro">These solutions draw inspiration from diverse knowledge domains to tackle the affordable housing crisis. Each solution addresses specific root causes identified in our analysis.</p>
                    <div class="solutions-grid">
        """
        
        # Add solutions
        for i, solution in enumerate(results['solutions'], 1):
            overall_score = solution['scores'].get('overall', 0)
            html_content += f'''
                        <div class="solution-card">
                            <h3>Solution {i} - Score: {overall_score:.1f}/10</h3>
                            <div class="tags-container">
                                <div class="solution-type">Based on: {html.escape(solution['root_cause'][:40])}{"..." if len(solution['root_cause']) > 40 else ""}</div>
                    '''
            
            if solution['type'] == 'domain_inspired':
                html_content += f'<div class="domain-inspiration">Inspired by: {html.escape(solution["domain"])}</div>'
            
            html_content += f'''
                            </div>
                            
                            <div class="score-grid">
                                <div class="score-item">
                                    <div class="score-label">Novelty</div>
                                    <div class="score-value">{solution['scores'].get('novelty', 'N/A')}</div>
                                    <div class="score-bar-container">
                                        <div class="score-bar" style="width: {solution['scores'].get('novelty', 0) * 10}%;"></div>
                                    </div>
                                </div>
                                <div class="score-item">
                                    <div class="score-label">Feasibility</div>
                                    <div class="score-value">{solution['scores'].get('feasibility', 'N/A')}</div>
                                    <div class="score-bar-container">
                                        <div class="score-bar" style="width: {solution['scores'].get('feasibility', 0) * 10}%;"></div>
                                    </div>
                                </div>
                                <div class="score-item">
                                    <div class="score-label">Impact</div>
                                    <div class="score-value">{solution['scores'].get('impact', 'N/A')}</div>
                                    <div class="score-bar-container">
                                        <div class="score-bar" style="width: {solution['scores'].get('impact', 0) * 10}%;"></div>
                                    </div>
                                </div>
                                <div class="score-item">
                                    <div class="score-label">Relevance</div>
                                    <div class="score-value">{solution['scores'].get('relevance', 'N/A')}</div>
                                    <div class="score-bar-container">
                                        <div class="score-bar" style="width: {solution['scores'].get('relevance', 0) * 10}%;"></div>
                                    </div>
                                </div>
                            </div>
                    '''
            
            # Add feedback if available
            if solution.get('feedback'):
                html_content += f'''
                            <div class="feedback-section">
                                <strong>Feedback:</strong> {html.escape(solution['feedback'])}
                            </div>
                        '''
            
            html_content += f'''
                            <div class="content-section">{html.escape(solution['content'])}</div>
                        </div>
                    '''
        
        html_content += """
                    </div>
                </section>
            </div>

            <footer>
                <div class="footer-content">
                    <div class="footer-logo">De Bono Lateral Thinking</div>
                    <p>Innovative systems-based approach to solving complex societal problems</p>
                    <p class="footer-text">Generated using LateralThinkingEnhanced™ - De Bono-inspired innovative problem solving</p>
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
    print("\nAnalyzing problem (simplified version with fewer API calls)...\n")
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