import ast
from loguru import logger

class CodeValidator:
    """Validates generated code for safety and security."""

    RESTRICTED_IMPORTS = {'os', 'sys', 'shutil', 'subprocess', 'builtins', 'socket', 'requests', 'urllib'}
    RESTRICTED_KEYWORDS = {'exec', 'eval', 'open', 'getattr', 'setattr', 'delattr', '__import__'}

    def validate(self, code: str):
        """Performs static analysis on the code to detect unsafe operations."""
        logger.info("Validating generated code for safety...")

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            logger.error("Syntax error in generated code: {}", e)
            return False, f"Syntax Error: {str(e)}"

        for node in ast.walk(tree):
            # Check for restricted imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split('.')[0] in self.RESTRICTED_IMPORTS:
                        return False, f"Restricted import: {alias.name}"
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split('.')[0] in self.RESTRICTED_IMPORTS:
                    return False, f"Restricted import from: {node.module}"

            # Check for restricted calls/keywords
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.RESTRICTED_KEYWORDS:
                        return False, f"Restricted keyword/function used: {node.func.id}"
                elif isinstance(node.func, ast.Attribute):
                    # Check for dunder attributes EXCEPT __init__ and common safe ones
                    safe_dunders = {'__init__', '__str__', '__repr__'}
                    if node.func.attr.startswith('__') and node.func.attr not in safe_dunders:
                        return False, f"Restricted attribute access: {node.func.attr}"
                    if node.func.attr in self.RESTRICTED_KEYWORDS:
                        return False, f"Restricted attribute access: {node.func.attr}"

        logger.success("Code validation passed.")
        return True, "Success"
