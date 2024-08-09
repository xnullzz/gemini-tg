import re
import bleach
import mistune

def parse_lists(text: str) -> str:
    """Parses Markdown lists into plain text with bullet points."""
    list_blocks = re.findall(r'(?:(?:-|\*|\+)\s.*\n)+', text, flags=re.MULTILINE)
    for block in list_blocks:
        items = re.findall(r'(?:-|\*|\+)\s(.*)', block)
        bullet_list = "\n".join(f"• {item}" for item in items)
        text = text.replace(block, bullet_list)
    return text

def parse_markdown(text: str) -> str:
    """Parses MarkdownV2 to HTML, with list items as plain text bullet points and headers in <strong> tags."""
    text = mistune.html(text)
    text = parse_lists(text)

    # Sanitize the output
    allowed_tags = ['b', 'strong', 'i', 'em', 'u', 'ins', 's', 'strike', 'del', 'a', 'code', 'pre', 'br']
    allowed_attributes = {'a': ['href', 'title'], 'code': ['class']}
    text = bleach.clean(text, tags=allowed_tags, attributes=allowed_attributes, strip=True)

    return text
