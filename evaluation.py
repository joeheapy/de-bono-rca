from typing import Dict, Any

def parse_evaluation(eval_text: str) -> Dict[str, Any]:
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

def parse_solution_content(content: str) -> Dict[str, str]:
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
        if "KEY_IDEAICAL INSIGHT:" in remaining:
            title_parts = remaining.split("KEY_IDEAICAL INSIGHT:", 1)
            sections["title"] = title_parts[0].strip()
            remaining = "KEY_IDEAICAL INSIGHT:" + title_parts[1]  # Add the header back for next split
        else:
            sections["title"] = remaining.strip()
            remaining = ""
    else:
        # If no title found, continue with the regular parsing
        remaining = full_content
    
    # Continue with existing parsing logic
    if "KEY_IDEAICAL INSIGHT:" in remaining:
        parts = remaining.split("KEY_IDEAICAL INSIGHT:", 1)
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