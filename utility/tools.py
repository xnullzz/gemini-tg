import re
import bleach
import mistune
from typing import List, Tuple

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
    try:
        text = mistune.html(text)
        text = parse_lists(text)

        allowed_tags: List[str] = ['b', 'strong', 'i', 'em', 'u', 'ins', 's', 'strike', 'del', 'a', 'code', 'pre', 'br']
        allowed_attributes: Dict[str, List[str]] = {'a': ['href', 'title'], 'code': ['class']}
        text = bleach.clean(text, tags=allowed_tags, attributes=allowed_attributes, strip=True)

        return text
    except Exception as e:
        logger.error(f"Error parsing markdown: {e}")
        return text  # Return original text if parsing fails

def split_long_message(message: str, max_length: int = 4096) -> List[str]:
    """Splits a long message into multiple parts that fit within Telegram's message size limit."""
    if len(message) <= max_length:
        return [message]
    
    parts = []
    while len(message) > max_length:
        part = message[:max_length]
        last_newline = part.rfind('\n')
        if last_newline != -1:
            parts.append(part[:last_newline])
            message = message[last_newline+1:]
        else:
            parts.append(part)
            message = message[max_length:]
    parts.append(message)
    return parts
