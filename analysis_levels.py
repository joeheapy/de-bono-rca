def get_analysis_config(level):
    """Return configuration parameters based on analysis level"""
    if level == 'fastest':
        return {
            'num_domains': 1,  # Minimal domains for fastest analysis 2
            'num_initial_causes': 2,
            'root_cause_depth': 1, 
            'max_leaf_causes': 2,
            'solutions_per_domain': 1
        }
    elif level == 'deepest':
        return {
            'num_domains': 4,  # More domains for deeper analysis
            'num_initial_causes': 4,
            'root_cause_depth': 3,
            'max_leaf_causes': 4,
            'solutions_per_domain': 1
        }
    else:  # balanced (default)
        return {
            'num_domains': 3,  # Standard number of domains
            'num_initial_causes': 3,
            'root_cause_depth': 2,
            'max_leaf_causes': 3,
            'solutions_per_domain': 1
        }