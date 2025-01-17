import re
import html

def parse_headers(md_text):
    """Convert Markdown headers to HTML."""
    # Pattern for headers (up to 6 levels)
    header_patterns = [
        (re.compile(r'###### (.*)'), r'<h6>\1</h6>'),
        (re.compile(r'##### (.*)'), r'<h5>\1</h5>'),
        (re.compile(r'#### (.*)'), r'<h4>\1</h4>'),
        (re.compile(r'### (.*)'), r'<h3>\1</h3>'),
        (re.compile(r'## (.*)'), r'<h2>\1</h2>'),
        (re.compile(r'# (.*)'), r'<h1>\1</h1>')
    ]
    for pattern, replacement in header_patterns:
        md_text = pattern.sub(replacement, md_text)
    return md_text

def parse_bold(md_text):
    """Convert Markdown bold text to HTML."""
    return re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', md_text)

def parse_italics(md_text):
    """Convert Markdown italics to HTML."""
    return re.sub(r'\*(.*?)\*', r'<em>\1</em>', md_text)

def parse_code(md_text):
    """Converts markdown code blocks to HTML pre/code blocks with appropriate language classes."""
    def replace_code(match):
        language = match.group(1)
        code = match.group(2)
        return f'<pre><code class="language-{language}">{code}</code></pre>'
    
    return re.sub(r'```(\w+)\n(.*?)\n```', replace_code, md_text, flags=re.DOTALL)

def parse_inline_code(md_text):
    """Convert inline code to HTML."""
    return re.sub(r'`([^`\n]+)`', r'<code>\1</code>', md_text)

def parse_links(md_text):
    """Convert Markdown links to HTML."""
    return re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', md_text)

def parse_list_items(md_text):
    """Convert Markdown list items to bullet points and add newlines."""
    lines = md_text.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('*'):
            lines[i] = '• ' + line.strip()[1:].strip()  # Replace * with •
        elif line.strip() and i > 0 and lines[i-1].startswith('•'):
            lines[i] = '• ' + line.strip()
    return '\n'.join(lines)

def parse_paragraphs(md_text):
    """Add double newline between paragraphs."""
    paragraphs = md_text.split('\n\n')
    paragraphs = [para.strip() for para in paragraphs if para.strip()]
    return '\n\n'.join(paragraphs)

def format_message(md_text):
    """Convert full Markdown text to HTML."""
    # First, escape all HTML characters in the entire text
    md_text = html.escape(md_text)
    
    # Parse Markdown elements
    md_text = parse_headers(md_text)
    md_text = parse_bold(md_text)
    md_text = parse_italics(md_text)
    md_text = parse_code(md_text)
    md_text = parse_inline_code(md_text)
    md_text = parse_links(md_text)
    md_text = parse_list_items(md_text)
    md_text = parse_paragraphs(md_text)
    
    return md_text
