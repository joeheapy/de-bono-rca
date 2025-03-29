import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms import OpenAI  # Updated import
from typing import List, Dict, Any
from dotenv import load_dotenv

# Hard-coded problem statement
DEFAULT_PROBLEM = "The UK property market disincentivises the development of affordable housing"

class LateralThinkingEngine:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get the OpenAI API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
        # Set the OpenAI API key
        os.environ["OPENAI_API_KEY"] = api_key
        
        # Initialize the language model
        self.llm = OpenAI(temperature=0.7)

    def generate_random_domains(self, num_domains: int = 3) -> List[str]:
        """
        Generate random knowledge domains using OpenAI
        """
        domain_prompt = PromptTemplate(
            input_variables=[],
            template=f"Please provide {num_domains} very specific and unique domains of knowledge that are not commonly used. Be precise and creative."
        )
        domain_chain = LLMChain(llm=self.llm, prompt=domain_prompt)
        
        # Run the chain to generate domains
        domains_str = domain_chain.run({}).strip()
        
        # Split and clean the domains
        domains = [domain.strip() for domain in domains_str.split('\n') if domain.strip()]
        
        return domains[:num_domains]

    def domain_inspired_solution(self, problem: str, domain: str) -> str:
        """
        Generate a solution inspired by a specific domain
        """
        inspiration_prompt = PromptTemplate(
            input_variables=["problem", "domain"],
            template="""Given the problem statement: '{problem}', 
            explore how the domain of '{domain}' can provide a unique and innovative solution. 
            
            Approach this by:
            1. Identifying the core principles or unique characteristics of the domain
            2. Metaphorically or directly applying these principles to the problem
            3. Generating a novel solution that challenges conventional thinking
            
            Provide a detailed, creative solution that demonstrates lateral thinking."""
        )
        
        inspiration_chain = LLMChain(llm=self.llm, prompt=inspiration_prompt)
        solution = inspiration_chain.run({
            "problem": problem, 
            "domain": domain
        }).strip()
        
        return f"**Inspired by {domain}:**\n{solution}"

    def provocation_technique(self, problem: str, num_solutions: int = 3) -> List[str]:
        """
        Provocation Technique with dynamic domain generation
        """
        # Generate random domains
        domains = self.generate_random_domains(num_solutions)
        
        solutions = []
        for domain in domains:
            # Generate a provocative solution based on the domain
            provocation_prompt = PromptTemplate(
                input_variables=["problem", "domain"],
                template="""Considering the problem '{problem}' and the domain of '{domain}', 
                create a provocative and seemingly impossible approach that challenges 
                conventional thinking. 
                
                Develop a solution that:
                1. Seems absurd at first glance
                2. Contains a kernel of innovative potential
                3. Deliberately inverts or radically reinterprets the problem
                
                Explain how this provocative approach might lead to breakthrough thinking."""
            )
            
            provocation_chain = LLMChain(llm=self.llm, prompt=provocation_prompt)
            solution = provocation_chain.run({
                "problem": problem, 
                "domain": domain
            }).strip()
            
            solutions.append(f"**Provocation from {domain}:**\n{solution}")
        
        return solutions

    def solve_problem(self, problem: str, num_solutions: int = 3) -> Dict[str, List[str]]:
        """
        Comprehensive lateral thinking problem-solving method
        Applies multiple techniques to generate innovative solutions
        """
        return {
            "Domain-Inspired Solutions": [
                self.domain_inspired_solution(problem, domain) 
                for domain in self.generate_random_domains(num_solutions)
            ],
            "Provocation Techniques": self.provocation_technique(problem, num_solutions)
        }

def main():
    # Initialize the lateral thinking engine
    engine = LateralThinkingEngine()
    
    # Use the default problem statement
    problem = DEFAULT_PROBLEM
    print(f"Problem statement: {problem}")
    
    # Solve the problem using lateral thinking techniques
    solutions = engine.solve_problem(problem)
    
    print("\n--- Lateral Thinking Solutions ---")
    for technique, results in solutions.items():
        print(f"\n{technique}:")
        for i, solution in enumerate(results, 1):
            print(f"{i}. {solution}\n{'-'*50}")

if __name__ == "__main__":
    main()