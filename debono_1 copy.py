import os
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from dotenv import load_dotenv

# Hard-coded problem statement
DEFAULT_PROBLEM = "The UK property market disincentivises the development of affordable housing"

# Load environment variables
load_dotenv()

# Get the OpenAI API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
    
# Set the OpenAI API key
os.environ["OPENAI_API_KEY"] = api_key


def research_root_causes(problem_statement):
    """Research and identify 5 systemic root causes of the problem."""
    llm = OpenAI(temperature=0.7)
    
    research_prompt = PromptTemplate(
        input_variables=["problem_statement"],
        template="""Analyze the following problem statement and identify 5 systemic root causes:
        
        Problem: {problem_statement}
        
        Focus on broad systemic issues that contribute to this problem. For each root cause:
        1. Provide a clear title
        2. Explain how it contributes to the problem
        3. Identify any relevant stakeholders affected
        
        Return 5 root causes, each clearly separated and numbered."""
    )
    
    research_chain = research_prompt | llm
    results = research_chain.invoke({"problem_statement": problem_statement})
    
    # Parse out the root causes
    root_causes = results.strip().split("\n\n")
    if len(root_causes) > 5:
        root_causes = root_causes[:5]
    
    print("--- Identified Root Causes ---")
    for cause in root_causes:
        print(f"\n{cause.strip()}")
    print("\n" + "-"*50)
    
    return root_causes


def generate_solutions(problem_statement, root_causes):
    llm = OpenAI(temperature=1.0)

    # Generate three random domains
    topic_prompt = PromptTemplate(
        input_variables=[],
        template="Please provide three random domains of knowledge.",
    )
    
    # Use the pipe operator instead of LLMChain
    topics_chain = topic_prompt | llm
    topics_result = topics_chain.invoke({})
    topics = topics_result.strip().split('\n')

    solutions = []
    for topic in topics:
        # Format root causes for the prompt
        formatted_causes = "\n".join([f"- {cause.split('.')[0].strip()}" if '.' in cause else f"- {cause.strip()}" for cause in root_causes])
        
        # Ask how the domain can inspire a solution
        inspiration_prompt = PromptTemplate(
            input_variables=["problem_statement", "topic", "root_causes"],
            template="""Considering the problem statement: '{problem_statement}',
            and these root causes:
            {root_causes}
            
            How can the domain of '{topic}' inspire a novel solution?
            Focus on addressing one or more of these root causes through the lens of {topic}.
            Describe a potential solution that tackles the systemic issues identified."""
        )
        
        # Use the pipe operator instead of LLMChain
        inspiration_chain = inspiration_prompt | llm
        solution = inspiration_chain.invoke({
            "problem_statement": problem_statement, 
            "topic": topic,
            "root_causes": formatted_causes
        })
        solutions.append(f"**Inspired by {topic}:**\n{solution.strip()}")

    return solutions


def main():
    # Use the default problem statement
    problem_statement = DEFAULT_PROBLEM
    print(f"Problem statement: {problem_statement}")

    # Research root causes first
    root_causes = research_root_causes(problem_statement)
    
    # Generate and print solutions based on root causes
    solutions = generate_solutions(problem_statement, root_causes)
    print("\n--- Lateral Thinking Solutions ---")
    for solution in solutions:
        print(f"\n{solution}\n")
        print("-"*50)


if __name__ == "__main__":
    main()