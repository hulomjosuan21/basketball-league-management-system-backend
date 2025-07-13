from docxtpl import RichText
import markdown2
from lxml import etree

def markdown_to_docx_friendly(md_text):
    html = markdown2.markdown(md_text)
    root = etree.HTML(html)
    rich_text = RichText()

    for element in root.xpath("//body/*"):
        if element.tag == "h1":
            rich_text.add(element.text, bold=True, size=36)
        elif element.tag == "h2":
            rich_text.add(element.text, bold=True, size=28)
        elif element.tag == "p":
            rich_text.add(element.text + "\n")
        elif element.tag == "ul":
            for li in element.xpath("./li"):
                if li.text:
                    rich_text.add(f"• {li.text}\n")
        elif element.tag == "ol":
            for idx, li in enumerate(element.xpath("./li"), start=1):
                if li.text:
                    rich_text.add(f"{idx}. {li.text}\n")
        rich_text.add("\n")  # Extra newline between blocks

    return rich_text
