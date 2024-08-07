import re
import html
from typing import Dict

def parse_headers(md_text: str) -> str:
    """Convert Markdown headers to HTML strong tags."""
    return re.sub(r'^(#{1,6})\s+(.*)$', r'<strong>\2</strong>', md_text, flags=re.MULTILINE)

def parse_emphasis(md_text: str) -> str:
    """Convert Markdown bold and italics to HTML."""
    md_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', md_text)
    md_text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', md_text)
    return md_text

def parse_code_blocks(md_text: str) -> str:
    """Convert Markdown code blocks to HTML pre/code blocks with language classes."""
    def replace_code(match):
        language = match.group(1).strip() or 'plaintext'
        code = html.escape(match.group(2).strip())
        return f'<pre><code class="language-{language}">{code}</code></pre>'
    
    return re.sub(r'```(\w*)\n([\s\S]+?)\n```', replace_code, md_text)

def parse_inline_code(md_text: str) -> str:
    """Convert inline code to HTML code tags."""
    return re.sub(r'`([^`\n]+)`', lambda m: f'<code>{html.escape(m.group(1))}</code>', md_text)

def parse_links(md_text: str) -> str:
    """Convert Markdown links to HTML anchor tags."""
    return re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', md_text)

def parse_list_items(md_text: str) -> str:
    """Convert Markdown list items to bullet points and add newlines."""
    lines = md_text.split('\n')
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(('•', '*', '-')):
            lines[i] = f'• {stripped[1:].strip()}'
        elif stripped and i > 0 and lines[i-1].startswith('•'):
            lines[i] = f'• {stripped}'
    return '\n'.join(lines)

def parse_paragraphs(md_text: str) -> str:
    """Add double newlines between paragraphs."""
    paragraphs = [para.strip() for para in md_text.split('\n\n') if para.strip()]
    return '\n\n'.join(paragraphs)

def unescape_html_chars(text: str) -> str:
    """Unescape HTML character entities."""
    return html.unescape(text)

def format_message(md_text: str) -> str:
    """Convert full Markdown text to HTML."""
    # Preserve code blocks
    code_blocks: Dict[str, str] = {}
    md_text = re.sub(r'(```[\s\S]+?```)', lambda m: code_blocks.setdefault(f'CODE_BLOCK_{len(code_blocks)}', m.group(1)), md_text)
    
    # Escape HTML characters, but unescape specific characters
    md_text = html.escape(md_text)
    md_text = md_text.replace('&lt;', '<').replace('&gt;', '>')
    
    # Parse Markdown elements
    md_text = parse_headers(md_text)
    md_text = parse_emphasis(md_text)
    md_text = parse_inline_code(md_text)
    md_text = parse_links(md_text)
    md_text = parse_list_items(md_text)
    md_text = parse_paragraphs(md_text)
    
    # Restore and parse code blocks
    for placeholder, block in code_blocks.items():
        md_text = md_text.replace(placeholder, parse_code_blocks(block))
    
    # Unescape HTML character entities
    md_text = unescape_html_chars(md_text)
    
    return md_text.strip()
