import re
import bleach

def parse_lists(text: str) -> str:
    """Parses Markdown lists into plain text with bullet points."""
    list_blocks = re.findall(r'(?:(?:-|\*|\+)\s.*\n)+', text, flags=re.MULTILINE)
    for block in list_blocks:
        items = re.findall(r'(?:-|\*|\+)\s(.*)', block)
        # Replace list items with lines starting with a bullet point
        bullet_list = "\n".join(f"• {item}" for item in items)
        text = text.replace(block, bullet_list)
    return text

def format_message(text: str) -> str:
    """Parses MarkdownV2 to HTML, with list items as plain text bullet points and headers in <strong> tags."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)  # Bold
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)      # Italic
    # ... (Add similar rules for other basic tags: u, ins, s, strike, del, a)
    text = re.sub(r'```(\w+)\n(.*?)\n```', r'<pre><code class="language-\1">\2</code></pre>', text, flags=re.DOTALL)  # Code blocks
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)  # Inline code
    text = re.sub(r'^(#+)\s*(.+)', r'<strong>\2</strong>', text, flags=re.MULTILINE)  # Headers

    text = parse_lists(text)

    # Sanitize the output
    allowed_tags = ['b', 'strong', 'i', 'em', 'u', 'ins', 's', 'strike', 'del', 'a', 'code', 'pre', 'br']
    allowed_attributes = {'a': ['href', 'title'], 'code': ['class']}
    text = bleach.clean(text, tags=allowed_tags, attributes=allowed_attributes, strip=True)

    return text
