import re

def escape_markdown(text):
    # First, replace literal '\n' with actual newline characters
    text = text.replace('\\n', '\n')

    # Escape Markdown special characters except for newline characters
    markdown_chars = r'[\*_\[\]()~`>#\+\-=|{}\.!]'
    escaped_text = re.sub(markdown_chars, lambda m: '\\' + m.group(0), text)

    return escaped_text
