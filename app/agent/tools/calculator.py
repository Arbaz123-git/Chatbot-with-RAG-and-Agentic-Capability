import re
import logging
from typing import Union

logger = logging.getLogger(__name__)

class CalculatorTool:
    def __init__(self):
        self.allowed_operators = {'+', '-', '*', '/', '(', ')', '.', ' '}
        self.allowed_functions = ['abs', 'round', 'pow', 'sqrt', 'sin', 'cos', 'tan', 'log', 'exp']
    
    def calculate(self, expression: str) -> str:
        logger.info(f"Calculating expression: {expression}")
        
        try:
            sanitized = self._sanitize_expression(expression)
            logger.debug(f"Sanitized expression: {sanitized}")
            
            result = eval(sanitized, {"__builtins__": {}}, self._get_safe_functions())
            
            logger.info(f"Calculation result: {result}")
            return str(result)
            
        except ZeroDivisionError:
            error_msg = "Error: Division by zero"
            logger.error(error_msg)
            return error_msg
        except SyntaxError:
            error_msg = f"Error: Invalid mathematical expression: {expression}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error calculating expression: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _sanitize_expression(self, expression: str) -> str:
        expression = expression.strip()
        
        expression = re.sub(r'[^0-9+\-*/().\s]', '', expression)
        
        if not expression:
            raise ValueError("Empty expression after sanitization")
        
        return expression
    
    def _get_safe_functions(self) -> dict:
        import math
        return {
            'abs': abs,
            'round': round,
            'pow': pow,
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'exp': math.exp,
            'pi': math.pi,
            'e': math.e
        }

calculator_tool = CalculatorTool()
