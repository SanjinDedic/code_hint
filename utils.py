import re
import keyword
import ast

def is_this_python(s):
    try:
        ast.parse(s)
        return True
    except SyntaxError:
        pass

    # Remove single-line comments
    s = re.sub(r"#.*", "", s)
    # Remove single and double-quoted strings
    s = re.sub(r'".*?"', '', s)
    s = re.sub(r"'.*?'", '', s)
    # Remove multi-line strings
    s = re.sub(r"'''(.*?)'''", '', s, flags=re.DOTALL)
    s = re.sub(r'"""(.*?)"""', '', s, flags=re.DOTALL)

    # List of Python keywords
    python_keywords = set(keyword.kwlist)
    # List of Python operators
    python_operators = {"+", "-", "*", "/", "//", "%", "**", "=", "==", "!=", ">", "<", ">=", "<=", "[", "]", "{", "}", ":",
                        "and", "or", "not", "is", "is not", "in", "not in", "&", "|", "^", "~", ")", "("}
    # Special case for single print statement
    if s.strip().startswith('print(') and s.strip().endswith(')'):
        return True
    # Tokenize the input string, including special characters
    words = re.findall(r"\b\w+\b|[+\-*/%=<>!&|^~()\[\]{}]", s)
    # Count the number of keywords and operators
    count = sum(word in python_keywords or word in python_operators for word in words)
    # Adjusting the threshold
    ratio = count / len(words) if words else 0
    print(ratio)
    return ratio > 0.35