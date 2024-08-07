import re


def escape_html(text: str) -> str:
    """Escapes HTML special characters in a string.

    Replaces &, <, > with HTML entities to prevent them
    from being interpreted as HTML tags when output.

    Args:
        text (str): The text to escape.

    Returns:
        str: The text with HTML characters escaped.
    """
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


def apply_hand_points(text: str) -> str:
    """Replaces markdown bullet points (*) with right hand point emoji.

    Arguments:
    text (str): The text to modify.

    Returns:
    str: The text with markdown bullet points replaced with emoji.
    """
    pattern = r"(?<=\n)\*\s(?!\*)|^\*\s(?!\*)"

    replaced_text = re.sub(pattern, "👉 ", text)

    return replaced_text


def apply_bold(text: str) -> str:
    """Replaces markdown bold formatting with HTML bold tags."""
    pattern = r"\*\*(.*?)\*\*"  # No changes here
    replaced_text = re.sub(pattern, r"<b>\1</b>", text)
    return replaced_text

def apply_italic(text: str) -> str:
    """Replaces markdown italic formatting with HTML italic tags."""
    pattern = r"(?<!\*)\*(?!\*\*)(.*?)(?<!\*)\*(?!\*)"  # Updated pattern
    replaced_text = re.sub(pattern, r"<i>\1</i>", text)
    return replaced_text

def apply_code(text: str) -> str:
    """Replace markdown code blocks with HTML <pre> tags.

    Arguments:
    text (str): The text to modify.

    Returns:
    str: The text with markdown code blocks replaced by HTML tags.
    """
    pattern = r"```([\w]*)\n([\s\S]*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    
    for match in matches:
        lang, code = match
        if lang:
            pre_tag = f"<pre lang='{lang}'>"
        else:
            pre_tag = "<pre>"
        
        # Ensure code content is properly escaped
        code = escape_html(code)
        
        text = text.replace(f"```{lang}\n{code}```", f"{pre_tag}{code}</pre>")
    
    return text

def apply_monospace(text: str) -> str:
    """Replaces markdown monospace backticks with HTML <code> tags.

    Arguments:
    text (str): The input text containing markdown monospace formatting.

    Returns:
    str: The text with monospace sections replaced with HTML tags.
    """
    pattern = r"(?<!`)`(?!`)(.*?)(?<!`)`(?!`)"
    replaced_text = re.sub(pattern, r"<code>\1</code>", text)
    return replaced_text


def apply_link(text: str) -> str:
    """Replace markdown links with HTML anchor tags.

    Arguments:
    text (str): The input text containing markdown links.

    Returns:
    str: The text with markdown links replaced by HTML anchor tags.
    """
    pattern = r"\[(.*?)\]\((.*?)\)"
    replaced_text = re.sub(pattern, r'<a href="\2">\1</a>', text)
    return replaced_text


def apply_underline(text: str) -> str:
    """Replace markdown underline with HTML underline tags.

    Arguments:
    text (str): The input text to modify.

    Returns:
    str: The text with markdown underlines replaced with HTML tags."""
    pattern = r"__(.*?)__"
    replaced_text = re.sub(pattern, r"<u>\1</u>", text)
    return replaced_text


def apply_strikethrough(text: str) -> str:
    """Replace markdown strikethrough with HTML strikethrough tags.

    Arguments:
    text (str): The input text to modify.

    Returns:
    str: The text with markdown strikethroughs replaced with HTML tags.
    """
    pattern = r"~~(.*?)~~"
    replaced_text = re.sub(pattern, r"<s>\1</s>", text)
    return replaced_text


def apply_header(text: str) -> str:
    """Replace markdown header # with HTML header tags.

    Arguments:
    text (str): The input text to modify.

    Returns:
    str: The text with markdown headers replaced with HTML tags.
    """
    pattern = r"^(#{1,6})\s+(.*)"
    replaced_text = re.sub(pattern, r"<b><u>\2</u></b>", text, flags=re.DOTALL)
    return replaced_text

def apply_exclude_code(text: str) -> str:
    """Apply text formatting to non-code lines."""
    lines = text.split("\n")
    in_code_block = False

    for i, line in enumerate(lines):
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue

        if not in_code_block:
            formatted_line = apply_header(line)
            formatted_line = apply_link(formatted_line)
            formatted_line = apply_bold(formatted_line)
            formatted_line = apply_italic(formatted_line)
            formatted_line = apply_underline(formatted_line)
            formatted_line = apply_strikethrough(formatted_line)
            formatted_line = apply_monospace(formatted_line)
            formatted_line = apply_hand_points(formatted_line)
            lines[i] = formatted_line

    return "\n".join(lines)

def format_message(text: str) -> str:
    """Format the given message text from markdown to HTML."""
    formatted_text = escape_html(text)
    formatted_text = apply_exclude_code(formatted_text)
    formatted_text = apply_code(formatted_text)

    # Validate the formatted HTML
    if not validate_html(formatted_text):
        raise ValueError("Invalid HTML generated from markdown")

    return formatted_text

def validate_html(html: str) -> bool:
    """Validate the formatted HTML string."""
    # Simple validation to check for unmatched tags
    stack = []
    tags = re.findall(r"</?[^>]+>", html)
    for tag in tags:
        if not tag.startswith("</"):
            stack.append(tag)
        elif stack and stack[-1][1:] == tag[2:]:
            stack.pop()
        else:
            print(f"Unmatched tag found: {tag}")
            print(f"Current stack: {stack}")
            return False
    if len(stack) != 0:
        print(f"Unmatched opening tags: {stack}")
    return len(stack) == 0
