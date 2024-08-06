import re

def escape_markdown(text):
    
    markdown_chars = r'[\*_\[\]()~`>#\+\-=|{}\.!]'
    escaped_text = re.sub(markdown_chars, lambda m: '\\' + m.group(0), text)

    escaped_text = escaped_text.replace('\\n', '\n')

    return escaped_text
