import os
import time
import webbrowser
import threading
from http.server import HTTPServer
from lateral_thinking import LateralThinkingEnhanced
from form_handler import FormHandler
from config import PROBLEM_STATEMENT

def main():
    # Initialize the analyzer
    analyzer = LateralThinkingEnhanced()
    
    # Create a custom handler class that has access to the analyzer
    def handler_factory(*args, **kwargs):
        return FormHandler(*args, analyzer=analyzer, **kwargs)
    
    # Start HTTP server
    def run_server():
        server = HTTPServer(('localhost', 8000), handler_factory)
        print('Starting server at http://localhost:8000')
        server.serve_forever()
    
    # Start server in a separate thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Open the initial report in the browser
    webbrowser.open('http://localhost:8000')
    
    # Keep main thread running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")

if __name__ == "__main__":
    main()