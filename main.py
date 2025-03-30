import os
import time
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
    
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 8000))
    
    # Check if running in production (Render sets this environment variable)
    is_production = os.environ.get('RENDER', False)
    
    if is_production:
        # Production mode: bind to all interfaces
        host = '0.0.0.0'
        server = HTTPServer((host, port), handler_factory)
        print(f'Starting server at http://{host}:{port} (production mode)')
        server.serve_forever()
    else:
        # Development mode: run in thread and open browser
        host = 'localhost'
        
        def run_server():
            server = HTTPServer((host, port), handler_factory)
            print(f'Starting server at http://{host}:{port} (development mode)')
            server.serve_forever()
        
        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Open the initial report in the browser (dev only)
        import webbrowser
        webbrowser.open(f'http://{host}:{port}')
        
        # Keep main thread running in development
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")

if __name__ == "__main__":
    main()