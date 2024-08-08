import re

def parse_list_items(md_text: str) -> str:
    """Convert Markdown list items to HTML list items."""
    md_text = re.sub(r'^\s*([-*•])\s+', '<li>', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'\n<li>', '</li>\n<li>', md_text)
    return md_text

def parse_paragraphs(md_text: str) -> str:
    """Add double newlines between paragraphs."""
    paragraphs = [para.strip() for para in md_text.split('\n\n') if para.strip()]
    return '\n\n'.join(paragraphs)

def parse_ul(html_text: str) -> str:
    """Removes <ul> tags from the HTML text."""
    html_text = re.sub(r'<ul>', '', html_text)
    html_text = re.sub(r'</ul>', '', html_text)
    return html_text

def format_message(html):
    html = re.sub(r"<p>", "", html)
    html = re.sub(r"</p>", "", html)
    html = parse_list_items(html)
    html = parse_paragraphs(html)
    html = parse_ul(html)

    return html
