import re
import html

def parse_headers(md_text):
    """Convert Markdown headers to HTML."""
    # Pattern for headers (up to 6 levels)
    header_patterns = [
        (re.compile(r'###### (.*)'), r'<strong>\1</strong>'),
        (re.compile(r'##### (.*)'), r'<strong>\1</strong>'),
        (re.compile(r'#### (.*)'), r'<strong>\1</strong>'),
        (re.compile(r'### (.*)'), r'<strong>\1</strong>'),
        (re.compile(r'## (.*)'), r'<strong>\1</strong>'),
        (re.compile(r'# (.*)'), r'<strong>\1</strong>')
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

def parse_code_blocks(md_text):
    """Converts markdown code blocks to HTML pre/code blocks with appropriate language classes."""
    def replace_code(match):
        language = match.group(1).strip()
        code = match.group(2).strip()
        # Unescape any HTML entities within the code block
        code = html.unescape(code)
        # Re-escape < and > characters
        code = code.replace('<', '&lt;').replace('>', '&gt;')
        return f'<pre><code class="language-{language}">{code}</code></pre>'
    
    # Use a more flexible pattern that allows for newlines around the code block
    pattern = r'```\s*(\w+)\s*\n((?:(?!```).|\n)+?)\n\s*```'
    return re.sub(pattern, replace_code, md_text, flags=re.DOTALL)

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
        if line.strip().startswith('•'):
            lines[i] = line.strip()  # Keep existing bullet points
        elif line.strip().startswith('*'):
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
    # First, temporarily replace code blocks with placeholders
    code_blocks = []
    def code_block_replacer(match):
        code_blocks.append(match.group(0))
        return f'CODE_BLOCK_{len(code_blocks) - 1}'
    
    pattern = r'```\s*(\w+)\s*\n((?:(?!```).|\n)+?)\n\s*```'
    md_text = re.sub(pattern, code_block_replacer, md_text, flags=re.DOTALL)
    
    # Escape HTML characters in the remaining text
    md_text = html.escape(md_text)
    
    # Parse Markdown elements
    md_text = parse_headers(md_text)
    md_text = parse_bold(md_text)
    md_text = parse_italics(md_text)
    md_text = parse_inline_code(md_text)
    md_text = parse_links(md_text)
    md_text = parse_list_items(md_text)
    md_text = parse_paragraphs(md_text)
    
    # Restore and parse code blocks
    def restore_code_blocks(match):
        index = int(match.group(1))
        return parse_code_blocks(code_blocks[index])
    
    md_text = re.sub(r'CODE_BLOCK_(\d+)', restore_code_blocks, md_text)
    
    return md_text
