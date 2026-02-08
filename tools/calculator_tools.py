from crewai.tools import BaseTool

class CalculatorTools(BaseTool):
    name: str = "calculate"
    description: str = """Useful to perform any mathematical calculations,
        like sum, minus, multiplication, division, etc.
        The input to this tool should be a mathematical
        expression, a couple examples are `200*7` or `5000/2*10`
        """
    def _run(self, operation: str) -> str:
        try:
            return eval(operation)
        except SyntaxError:
            return "Error: Invalid syntax in mathematical expression"
