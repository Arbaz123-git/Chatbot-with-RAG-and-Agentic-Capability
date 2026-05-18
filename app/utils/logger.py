import logging
import sys
import os
from datetime import datetime

class StepLogger:
    """Centralized step-by-step logger for tracking chatbot operations."""
    
    def __init__(self):
        self.step_count = 0
        self.logger = logging.getLogger("chatbot_steps")
        self.logger.setLevel(logging.INFO)
        self.logger.handlers = []  # Clear existing handlers
        
        # Log file path
        log_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.log_file = os.path.join(log_dir, "chatbot_steps.log")
        
        # Clear log file on initialization (fresh logs each run)
        with open(self.log_file, 'w') as f:
            f.write(f"=== Chatbot Session Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_format)
        
        # File handler
        file_handler = logging.FileHandler(self.log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S')
        file_handler.setFormatter(file_format)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def reset_steps(self):
        """Reset step counter for a new request."""
        self.step_count = 0
        self.logger.info("\n" + "="*60)
        self.logger.info("NEW REQUEST")
        self.logger.info("="*60)
    
    def step(self, message: str, component: str = "SYSTEM"):
        """Log a step with auto-incrementing step number."""
        self.step_count += 1
        log_message = f"[STEP {self.step_count}] [{component}] {message}"
        self.logger.info(log_message)
    
    def info(self, message: str, component: str = "SYSTEM"):
        """Log info without step number."""
        log_message = f"         [{component}] {message}"
        self.logger.info(log_message)
    
    def result(self, message: str):
        """Log final result."""
        self.logger.info(f"\n{'─'*40}")
        self.logger.info(f"RESULT: {message[:200]}{'...' if len(message) > 200 else ''}")
        self.logger.info(f"{'─'*40}\n")
    
    def error(self, message: str, component: str = "SYSTEM"):
        """Log an error."""
        log_message = f"[ERROR] [{component}] {message}"
        self.logger.error(log_message)

# Global instance
step_logger = StepLogger()
