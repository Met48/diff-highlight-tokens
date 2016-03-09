import re

ESCAPE_RE = re.compile(r'\033\[[^m]*m')

FORMAT_INVERT = '\033[7m'
FORMAT_RESET_INVERT = '\033[27m'
FORMAT_REMOVE = '\033[31m'  # Red
FORMAT_ADD = '\033[32m'  # Green
FORMAT_RESET = '\033[0m'
