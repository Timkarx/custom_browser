from layout_engine.core import DocumentLayout, paint_tree
from parser.html.core import HTMLParser, Text, Element, print_tree
from parser.css.core import CSSParser, style, cascade_priority

import tkinter
import tkinter.font

HSTEP, VSTEP = 13, 18
WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100

DEFAULT_STYLE_SHEET = CSSParser(open("browser.css").read()).parse()

class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT, bg="white")
        self.canvas.pack()
        self.scroll = 0
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)

    def load(self, url):
        # Request
        body = url.request()
        # Parsing
        self.entryNode = HTMLParser(body).parse()
        rules = DEFAULT_STYLE_SHEET.copy()
        links = [node.attributes["href"]
                for node in tree_to_list(self.entryNode, [])
                if isinstance(node, Element)
                and node.tag == "link"
                and node.attributes.get("rel") == "stylesheet"
                and "href" in node.attributes]
        for link in links:
            style_url = url.resolve(link)
            body = style_url.request()
            rules.extend(CSSParser(body).parse())
        style(self.entryNode, sorted(rules, key=cascade_priority))
        # Layout and rendering
        self.document = DocumentLayout(self.entryNode)
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for cmd in self.display_list:
            if cmd.top > self.scroll + HEIGHT:
                continue
            if cmd.bottom < self.scroll:
                continue
            cmd.execute(self.scroll, self.canvas)

    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

    def scrollup(self, e):
        self.scroll -= SCROLL_STEP
        self.draw()

def tree_to_list(tree, list):
        list.append(tree)
        for child in tree.children:
            tree_to_list(child, list)
        return list
