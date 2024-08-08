import re

def format_message(html):
    html = re.sub(r"<p>", "", html)
    html = re.sub(r"</p>", "", html)
    html = re.sub(r"<li>(.*?)</li>", r"• \1", html, flags=re.DOTALL)

    return html
