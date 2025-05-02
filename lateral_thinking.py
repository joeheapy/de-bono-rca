from typing import List, Dict, Any
from langchain_openai import OpenAI as LangchainOpenAI
from langchain.prompts import PromptTemplate
import os
import time
import html
from datetime import datetime
import numpy as np
from evaluation import parse_evaluation, parse_solution_content
from config import (
    OPENAI_API_KEY, 
    NUM_DOMAINS, 
    NUM_INITIAL_CAUSES, 
    ROOT_CAUSE_DEPTH, 
    MAX_LEAF_CAUSES,
    SOLUTIONS_PER_DOMAIN,
    API_REQUEST_TIMEOUT,
    API_CALL_DELAY,
    ANALYST_TEMPERATURE,
    CHALLENGER_TEMPERATURE,
    EVALUATOR_TEMPERATURE,
    DOMAIN_TEMPERATURE
)

class LateralThinkingEnhanced:
    def __init__(self):
        # Validate API key
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
        # Set the OpenAI API key
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
        
        # Initialize different language models with timeouts
        self.analyst_llm = LangchainOpenAI(
            temperature=ANALYST_TEMPERATURE,
            request_timeout=API_REQUEST_TIMEOUT,
            openai_api_key=os.environ.get("OPENAI_API_KEY")
        )
        self.challenger_llm = LangchainOpenAI(
            temperature=CHALLENGER_TEMPERATURE,
            request_timeout=API_REQUEST_TIMEOUT,
            openai_api_key=os.environ.get("OPENAI_API_KEY")
        )
        self.evaluator_llm = LangchainOpenAI(
            temperature=EVALUATOR_TEMPERATURE,
            request_timeout=API_REQUEST_TIMEOUT,
            openai_api_key=os.environ.get("OPENAI_API_KEY")
        )
        self.domain_llm = LangchainOpenAI(
            temperature=DOMAIN_TEMPERATURE,
            request_timeout=API_REQUEST_TIMEOUT,
            openai_api_key=os.environ.get("OPENAI_API_KEY")
        )
    
    def generate_random_domains(self, num_domains: int = NUM_DOMAINS) -> List[str]:
        """Generate random knowledge domains for cross-pollination of ideas"""
        
        domain_prompt = PromptTemplate(
            input_variables=[],
            template=f"""Generate {num_domains} specific knowledge domains or fields.
            
            These should be diverse across different areas of human knowledge.
            DO NOT INCLUDE 'Quantum physics' or 'Astrophysics' or 'Enviromental science'.
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
    
    def challenge_assumptions(self, problem: str, cause_tree: Dict[str, Any], domains: List[str], 
                              max_leaf_causes=MAX_LEAF_CAUSES, solutions_per_domain=SOLUTIONS_PER_DOMAIN) -> List[Dict[str, Any]]:
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
        # Limit to max leaf causes
        if len(leaf_causes) > max_leaf_causes:
            leaf_causes = leaf_causes[:max_leaf_causes]
        
        solutions = []
        
        for leaf_cause in leaf_causes:
            # Use ALL domains instead of just the first one
            for domain in domains:
                # Generate multiple solutions per domain-cause pair
                for solution_num in range(1, solutions_per_domain + 1):
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
                
                # Parse scores using imported function
                scores = parse_evaluation(eval_result)
                solution["scores"] = scores
                
                # Add delay to avoid rate limiting
                time.sleep(API_CALL_DELAY)
                
            except Exception as e:
                print(f"Error evaluating solution: {e}")
                # Keep default scores if evaluation fails
        
        # Sort solutions by overall score
        return sorted(solutions, key=lambda x: x["scores"].get("overall", 0), reverse=True)

    def analyze_problem(self, problem: str, config=None) -> Dict[str, Any]:
        """Complete analysis with evaluation"""
        # Use provided config or default to global constants
        cfg = config or {}
        num_domains = cfg.get('num_domains', NUM_DOMAINS)  # Add this line for domains
        num_initial_causes = cfg.get('num_initial_causes', NUM_INITIAL_CAUSES)
        root_cause_depth = cfg.get('root_cause_depth', ROOT_CAUSE_DEPTH)
        max_leaf_causes = cfg.get('max_leaf_causes', MAX_LEAF_CAUSES)
        solutions_per_domain = cfg.get('solutions_per_domain', SOLUTIONS_PER_DOMAIN)
        
        print("1. Generating knowledge domains...")
        domains = self.generate_random_domains(num_domains)  # Use configurable value
        
        print("2. Identifying initial causes...")
        initial_causes = self.identify_initial_causes(problem, num_initial_causes)
        
        print("3. Building root cause trees...")
        cause_trees = []
        for i, cause in enumerate(initial_causes):
            print(f"   Analyzing cause {i+1}/{len(initial_causes)}: {cause[:30]}...")
            tree = self.dig_deeper(problem, cause, depth=root_cause_depth)
            cause_trees.append(tree)
        
        print("4. Generating solutions...")
        all_solutions = []
        for i, tree in enumerate(cause_trees):
            print(f"   Generating solutions for tree {i+1}/{len(cause_trees)}...")
            solutions = self.challenge_assumptions(problem, tree, domains, max_leaf_causes, solutions_per_domain)
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