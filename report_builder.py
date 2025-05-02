import os
import html
from datetime import datetime
from typing import Dict, Any
from evaluation import parse_solution_content
from config import PROBLEM_STATEMENT

def tree_to_html(tree, level=0):
    """Helper method to convert a cause tree to HTML"""
    html_content = f'<div style="margin-left: {level*20}px">\n'
    html_content += f'<p><strong>{html.escape(tree["cause"])}</strong></p>\n'
    
    if tree['children']:
        html_content += '<div class="cause-node">\n'
        for child in tree['children']:
            html_content += tree_to_html(child, level + 1)
        html_content += '</div>\n'
    
    html_content += '</div>\n'
    return html_content

def generate_html_report(results: Dict[str, Any], show_loading=False) -> str:
    """Generate an HTML report with embedded CSS"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Read the CSS file and embed it
    css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.css")
    with open(css_path, 'r') as css_file:
        css_content = css_file.read()
    
    # Create HTML content with embedded CSS
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>De Bono Thinking: Lateral Innovation Tool</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Text&family=Lexend:wght@300;400&display=swap" rel="stylesheet">
        <style>
        {css_content}
        </style>
    </head>
    <body>
        <div class="top-bar"></div>
        <header class="header">
            <div class="header-content">
                <a href="#" class="logo">Social Investor Idea Generator</a>
                <div class="timestamp">Generated on: {timestamp}</div>
            </div>
        </header>

        <div class="hero">
            <div class="hero-content">
                <h1>What's the (social and systemic) problem?</h1>
                <form id="problemForm" action="" method="post">
                    <div class="textarea-container">
                        <textarea 
                            id="problemInput" 
                            name="problem" 
                            required 
                            minlength="75" 
                            maxlength="300" 
                            placeholder="Describe the problem...">{html.escape(results['problem'])}</textarea>
                        <div class="character-count">
                            <span id="charCount">0</span>/300 characters (75 minimum)
                        </div>
                    </div>
                    <div class="analysis-level">
                        <label class="analysis-level-label">Analysis Level:</label>
                        <div class="level-options">
                            <label class="level-option">
                                <input type="radio" name="analysis_level" value="fastest" checked>
                                <div class="option-content">
                                    <span class="option-name">Fastest</span>
                                    <span class="option-desc">Quick analysis with fewer ideas (1-2 min)</span>
                                </div>
                            </label>
                            <label class="level-option">
                                <input type="radio" name="analysis_level" value="balanced">
                                <div class="option-content">
                                    <span class="option-name">Balanced</span>
                                    <span class="option-desc">Standard depth and variety (2-5 min)</span>
                                </div>
                            </label>
                            <label class="level-option">
                                <input type="radio" name="analysis_level" value="deepest">
                                <div class="option-content">
                                    <span class="option-name">Deepest</span>
                                    <span class="option-desc">Thorough analysis with more ideas (15+ min)</span>
                                </div>
                            </label>
                        </div>
                    </div>
                    <div class="form-footer">
                        <button type="button" onclick="resetForm()" class="refresh-btn">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                            </svg>
                            Clear Page
                        </button>
                        <button type="submit" class="generate-btn">Generate Solutions</button>
                    </div>
                </form>
            </div>
        </div>

        <div class="main-container">
    """
    
    # 1. Root Causes Section - display with loading state if needed
    if not results['cause_trees'] and show_loading:
        html_content += """
            <section>
                <h2>Systemic Root Causes</h2>
                <p class="section-intro">By repeatedly asking "why," we identify deeper systemic causes behind the problem. Each branch explores a different causal pathway.</p>
                <div class="loading-spinner"></div>
            </section>
        """
    else:
        html_content += """
            <section>
                <h2>Systemic Root Causes</h2>
                <p class="section-intro">By repeatedly asking "why," we identify deeper systemic causes behind the problem. Each branch explores a different causal pathway.</p>
        """
        
        # Add root cause trees
        for i, tree in enumerate(results['cause_trees'], 1):
            html_content += f'<div class="cause-tree">\n<h3>Root Cause {i}: {html.escape(tree["cause"])}</h3>\n'
            html_content += tree_to_html(tree)
            html_content += '</div>\n'
        
        html_content += """
            </section>
        """
    
    # 2. Knowledge Domains Section - display with loading state if needed
    if not results['domains'] and show_loading:
        html_content += """
            <section>
                <h2>Knowledge Domains</h2>
                <p class="section-intro">These domains provide cross-disciplinary inspiration for innovative solutions, encouraging lateral thinking that breaks conventional problem-solving patterns.</p>
                <div class="loading-spinner"></div>
            </section>
        """
    else:
        html_content += """
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
        """
    
    # 3. Solutions Section - display with loading state if needed
    if not results['solutions'] and show_loading:
        html_content += """
            <section>
                <h2>Ideas</h2>
                <p class="section-intro">These solutions draw inspiration from diverse knowledge domains to tackle the problem. Each solution addresses specific root causes identified in our analysis.</p>
                <div class="loading-spinner"></div>
            </section>
        """
    else:
        html_content += """
            <section>
                <h2>Ideas</h2>
                <p class="section-intro">These solutions draw inspiration from diverse knowledge domains to tackle the problem. Each solution addresses specific root causes identified in our analysis.</p>
                <div class="solutions-grid">
        """
        
        # Add solutions
        for i, solution in enumerate(results['solutions'], 1):
            overall_score = solution['scores'].get('overall', 0)
            
            # Parse solution content into sections
            sections = parse_solution_content(solution['content'])
            
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
            
            html_content += f'''
                    </div>
                    
                    <div class="score-grid">
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
        """
    
    html_content += """
        </div>
    """

    # Add JavaScript for character counting, validation, and processing overlay
    html_content += """
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const textarea = document.getElementById('problemInput');
                const charCount = document.getElementById('charCount');
                const form = document.getElementById('problemForm');
                
                // Update character count on load
                charCount.textContent = textarea.value.length;
                
                // Update character count as user types
                textarea.addEventListener('input', function() {
                    charCount.textContent = this.value.length;
                    
                    // Visual feedback based on character count
                    if (this.value.length < 75) {
                        charCount.classList.add('invalid');
                        charCount.classList.remove('valid');
                    } else {
                        charCount.classList.add('valid');
                        charCount.classList.remove('invalid');
                    }
                });
                
                // Form validation
                form.addEventListener('submit', function(e) {
                    if (textarea.value.length < 75) {
                        e.preventDefault();
                        alert('Please enter at least 75 characters for the problem statement.');
                    } else {
                        // Show processing overlay when form is submitted
                        const hideOverlay = showProcessingOverlay();
                        
                        // Store the hideOverlay function so it can be called when response is received
                        window.hideProcessingOverlay = hideOverlay;
                    }
                });
                
                // Set initial focus to the textarea but place cursor at the end
                textarea.focus();
                textarea.setSelectionRange(textarea.value.length, textarea.value.length);
            });

            function resetForm() {
                // Fetch a clean form from the server
                fetch('/reset')
                    .then(response => response.text())
                    .then(html => {
                        document.open();
                        document.write(html);
                        document.close();
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        // Fallback to page reload if fetch fails
                        window.location.reload();
                    });
            }

            function showProcessingOverlay() {
                // Create overlay
                const overlay = document.createElement('div');
                overlay.className = 'processing-overlay';
                
                // Create spinner
                const spinner = document.createElement('div');
                spinner.className = 'processing-spinner';
                overlay.appendChild(spinner);
                
                // Create status message
                const status = document.createElement('div');
                status.className = 'processing-status';
                status.textContent = 'Analysing your problem...';
                overlay.appendChild(status);
                
                // Create steps list
                const steps = document.createElement('div');
                steps.className = 'processing-steps';
                
                // Add processing steps
                const stepsList = [
                    'Generating knowledge domains for lateral thinking',
                    'Identifying initial root causes',
                    'Building root cause trees',
                    'Having ideas',
                    'Writing and ranking ideas (this will take some time)'
                ];
                
                stepsList.forEach((step, index) => {
                    const stepEl = document.createElement('div');
                    stepEl.className = 'processing-step' + (index === 0 ? ' active' : '');
                    stepEl.id = `process-step-${index}`;
                    
                    const indicator = document.createElement('span');
                    indicator.className = 'step-indicator';
                    stepEl.appendChild(indicator);
                    
                    const text = document.createElement('span');
                    text.textContent = step;
                    stepEl.appendChild(text);
                    
                    steps.appendChild(stepEl);
                });
                
                overlay.appendChild(steps);
                document.body.appendChild(overlay);
                
                // Use variable timing for each step to better match the actual process
                let currentStep = 0;
                const stepTimes = [3000, 7000, 10000, 15000, 15000]; 
                
                function advanceStep() {
                    if (currentStep < stepsList.length - 1) {
                        currentStep++;
                        document.querySelectorAll('.processing-step').forEach(el => el.classList.remove('active'));
                        document.getElementById(`process-step-${currentStep}`).classList.add('active');
                        
                        // If we've reached the generation step, update the status text
                        if (currentStep === 3) {
                            status.textContent = 'Creating innovative solutions...';
                        }
                        
                        // Schedule next step with appropriate timing
                        if (currentStep < stepsList.length - 1) {
                            setTimeout(advanceStep, stepTimes[currentStep]);
                        }
                    }
                }
                
                // Start the progression
                setTimeout(advanceStep, stepTimes[0]);
                
                return () => {
                    // Clear any pending timeouts by using a more comprehensive approach
                    let id = window.setTimeout(function() {}, 0);
                    while (id--) {
                        window.clearTimeout(id);
                    }
                    
                    if (document.body.contains(overlay)) {
                        document.body.removeChild(overlay);
                    }
                };
            }
        </script>
    </body>
    </html>
    """
    
    # Save the HTML content to a file
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "de_bono_report.html")
    with open(report_path, 'w') as f:
        f.write(html_content)
    
    return report_path