import requests
from html.parser import HTMLParser

class HTMLBeautifier(HTMLParser):
    def __init__(self, indent_size=2):
        super().__init__()
        self.result = []
        self.indent_level = 0
        self.indent_str = " " * indent_size
        self.inline_elements = {
            'a', 'abbr', 'acronym', 'b', 'bdo', 'big', 'br', 'button', 'cite', 'code', 
            'dfn', 'em', 'i', 'img', 'input', 'kbd', 'label', 'map', 'object', 'q', 
            'samp', 'script', 'select', 'small', 'span', 'strong', 'sub', 'sup', 
            'textarea', 'time', 'tt', 'var'
        }
        self.void_elements = {
            'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 
            'meta', 'param', 'source', 'track', 'wbr'
        }
        # Special tags where we want specific formatting - added span and all inline elements
        self.compact_tags = {
            'title', 'div', 'td', 'th', 'li', 'option', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'p', 'caption', 'dd', 'dt', 'figcaption', 'label', 'span', 'a', 'abbr', 'acronym',
            'b', 'bdo', 'big', 'button', 'cite', 'code', 'dfn', 'em', 'i', 'kbd',
            'q', 'samp', 'small', 'strong', 'sub', 'sup', 'time', 'tt', 'var'
        }
        self.add_blank_after_open = {'html'}
        self.add_blank_after_close = {'head'}
        
        self.preserve_whitespace = False
        self.tag_stack = []
        self.data_buffer = {}  # Stores data for each tag level

    def handle_starttag(self, tag, attrs):
        # Format attributes
        formatted_attrs = ''
        for attr, value in attrs:
            if value is None:
                formatted_attrs += f' {attr}'
            else:
                value = value.replace('"', '&quot;')
                formatted_attrs += f' {attr}="{value}"'
        
        # Add indented tag
        indent = self.indent_str * self.indent_level
        self.result.append(f"{indent}<{tag}{formatted_attrs}>")
        
        # Add blank line after specific opening tags
        if tag in self.add_blank_after_open:
            self.result.append("")
        
        # Increase indent level for non-void elements
        if tag not in self.void_elements:
            self.indent_level += 1
            # Add tag to stack and prepare data buffer
            self.tag_stack.append(tag)
            self.data_buffer[len(self.tag_stack)] = []
        
        if tag == 'pre' or tag == 'code':
            self.preserve_whitespace = True

    def handle_endtag(self, tag):
        # Don't process end tags for void elements
        if tag in self.void_elements:
            return
        
        # Check if we have any content in the buffer for this tag level
        if self.tag_stack and self.tag_stack[-1] == tag and len(self.tag_stack) in self.data_buffer:
            content = ''.join(self.data_buffer[len(self.tag_stack)])
            # If content is present and tag is in compact list, format it differently
            if content and tag in self.compact_tags:
                # Remove last line (which is the opening tag)
                last_line = self.result.pop()
                # Replace it with compact format
                self.result.append(f"{last_line}{content}</{tag}>")
                # We've already added closing tag, so just cleanup
                del self.data_buffer[len(self.tag_stack)]
                self.tag_stack.pop()
                self.indent_level -= 1
                return
        
        # Normal closing tag process
        self.indent_level -= 1
        indent = self.indent_str * self.indent_level
        self.result.append(f"{indent}</{tag}>")
        
        # Add blank line after specific closing tags
        if tag in self.add_blank_after_close:
            self.result.append("")
        
        if self.tag_stack and self.tag_stack[-1] == tag:
            del self.data_buffer[len(self.tag_stack)]
            self.tag_stack.pop()
        
        if tag == 'pre' or tag == 'code':
            self.preserve_whitespace = False

    def handle_data(self, data):
        if self.preserve_whitespace:
            # For pre/code, preserve whitespace and append directly
            if self.result:
                self.result[-1] += data
            else:
                self.result.append(data)
            return
            
        # For normal content, normalize whitespace
        data = ' '.join(data.split()).strip()
        if not data:
            return
        
        # Store data in buffer for the current tag level
        if self.tag_stack:
            self.data_buffer[len(self.tag_stack)].append(data)
        else:
            # Top level text, just add with current indent
            indent = self.indent_str * self.indent_level
            self.result.append(f"{indent}{data}")

    def handle_comment(self, data):
        indent = self.indent_str * self.indent_level
        self.result.append(f"{indent}<!--{data}-->")

    def handle_decl(self, decl):
        self.result.append(f"<!{decl}>")
        
    def handle_pi(self, data):
        indent = self.indent_str * self.indent_level
        self.result.append(f"{indent}<?{data}?>")

def format_html(html_code, indent_size=4):
    """Format HTML code to match the specified style."""
    parser = HTMLBeautifier(indent_size=indent_size)
    parser.feed(html_code)
    return '\n'.join(parser.result)

if __name__ == "__main__":
    # Example usage
    html_code = open("old stuff/data/AnswerKey.aspx.html", "r", encoding="utf-8").read()
    formatted_html = format_html(html_code)

    with open("output.html", "w", encoding="utf-8") as file:
        file.write(formatted_html)
