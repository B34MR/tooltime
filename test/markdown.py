from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table
from rich import box
from rich.panel import Panel
from rich.theme import Theme

MARKDOWN = """
# This is an h1

Rich can do a pretty *decent* job of rendering markdown.

1. This is a list item
2. This is another list item
"""
from rich.console import Console
from rich.markdown import Markdown

console = Console()
md = Markdown(MARKDOWN)
console.print(md)