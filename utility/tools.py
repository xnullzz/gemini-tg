import re

# Function to convert headers
def convert_headers(text):
    # MarkdownV2 headers are indicated by one to six hash (#) symbols
    for i in range(6, 0, -1):
        header_pattern = re.compile(rf'{"#" * i} (.+)')
        text = header_pattern.sub(rf'<h{i}>\1</h{i}>', text)
    return text

# Function to convert bold text
def convert_bold(text):
    bold_pattern = re.compile(r'\*\*(.+?)\*\*')
    text = bold_pattern.sub(r'<b>\1</b>', text)
    return text

# Function to convert italic text
def convert_italic(text):
    italic_pattern = re.compile(r'\*(.+?)\*')
    text = italic_pattern.sub(r'<i>\1</i>', text)
    return text

# Function to convert links
def convert_links(text):
    link_pattern = re.compile(r'\[(.+?)\]\((.+?)\)')
    text = link_pattern.sub(r'<a href="\2">\1</a>', text)
    return text

# Function to convert images
def convert_images(text):
    image_pattern = re.compile(r'!\[(.*?)\]\((.+?)\)')
    text = image_pattern.sub(r'<img src="\2" alt="\1">', text)
    return text

# Function to convert inline code and code blocks
def convert_code(text):
    # Inline code
    inline_code_pattern = re.compile(r'`(.+?)`')
    text = inline_code_pattern.sub(r'<code>\1</code>', text)
    # Code blocks
    code_block_pattern = re.compile(r'```(.*?)```', re.DOTALL)
    text = code_block_pattern.sub(r'<pre><code>\1</code></pre>', text)
    return text

# Function to convert lists (both ordered and unordered)
def convert_lists(text):
    # Ordered lists
    ordered_list_pattern = re.compile(r'^\d+\. (.+)', re.MULTILINE)
    text = ordered_list_pattern.sub(r'<li>\1</li>', text)
    # Unordered lists
    unordered_list_pattern = re.compile(r'^\* (.+)', re.MULTILINE)
    text = unordered_list_pattern.sub(r'<li>\1</li>', text)
    # Wrap list items in <ul> or <ol>
    text = re.sub(r'(<li>.+</li>)', r'<ul>\1</ul>', text)
    return text

# Final function to convert MarkdownV2 to HTML
def format_message(text):
    text = convert_headers(text)
    text = convert_bold(text)
    text = convert_italic(text)
    text = convert_links(text)
    text = convert_images(text)
    text = convert_code(text)
    text = convert_lists(text)
    return text

