from telnet.index import URL
from chrome.core import Chrome
from layout_engine.draw_cmds import Rect, DrawText, DrawOutline, DrawLine, DrawRect
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
        self.tabs = []
        self.active_tab = None
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window, width=WIDTH, height=HEIGHT, bg="white"
        )
        self.canvas.pack()
        self.window.bind("<Down>", self.handle_scrolldown)
        self.window.bind("<Up>", self.handle_scrollup)
        self.window.bind("<Button-1>", self.handle_click)
        self.window.bind("<Key>", self.handle_key)
        self.window.bind("<Return>", self.handle_enter)
        self.chrome = Chrome(self)

    def new_tab(self, url):
        new_tab = Tab(HEIGHT - self.chrome.bottom)
        new_tab.load(url)
        self.active_tab = new_tab
        self.tabs.append(new_tab)
        self.draw()

    def handle_scrolldown(self, e):
        self.active_tab.scrolldown()
        self.draw()

    def handle_scrollup(self, e):
        self.active_tab.scrollup()
        self.draw()

    def handle_click(self, e):
        if e.y < self.chrome.bottom:
            self.chrome.click(e.x, e.y)
        else:
            tab_y = e.y - self.chrome.bottom
            self.active_tab.click(e.x, tab_y)
        self.draw()

    def handle_key(self, e):
        if len(e.char) == 0: return
        if not (0x20 <= ord(e.char) <= 0x7f): return
        self.chrome.keypress(e.char)
        self.draw()

    def handle_enter(self, e):
        self.chrome.enter()
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        self.active_tab.draw(self.canvas, self.chrome.bottom)
        for cmd in self.chrome.paint():
            cmd.execute(0, self.canvas)


class Tab:
    def __init__(self, tab_height):
        self.url = None
        self.scroll = 0
        self.tab_height = tab_height
        self.history = []

    def load(self, url):
        self.url = url
        self.history.append(url)
        # Request
        body = url.request()
        # Parsing
        self.entryNode = HTMLParser(body).parse()
        rules = DEFAULT_STYLE_SHEET.copy()
        links = [
            node.attributes["href"]
            for node in tree_to_list(self.entryNode, [])
            if isinstance(node, Element)
            and node.tag == "link"
            and node.attributes.get("rel") == "stylesheet"
            and "href" in node.attributes
        ]
        for link in links:
            style_url = url.resolve(link)
            body = style_url.request()
            rules.extend(CSSParser(body).parse())
        style(self.entryNode, sorted(rules, key=cascade_priority))
        # Layout and rendering
        self.document = DocumentLayout(self.entryNode)
        self.document.layout()
        # Mutate the Tabs display_list then draw
        self.display_list = []
        paint_tree(self.document, self.display_list)

    def go_back(self):
        if len(self.history) > 1:
            self.history.pop()
            back = self.history.pop()
            self.load(back)

    def draw(self, canvas, offset):
        for cmd in self.display_list:
            if cmd.top > self.scroll + self.tab_height:
                continue
            if cmd.bottom < self.scroll:
                continue
            cmd.execute(self.scroll - offset, canvas)

    def scrolldown(self):
        max_scroll = max(self.document.height + 2 * VSTEP - self.tab_height, 0)
        self.scroll = min(self.scroll + SCROLL_STEP, max_scroll)

    def scrollup(self):
        self.scroll = 0 if self.scroll - SCROLL_STEP <= 0 else self.scroll - SCROLL_STEP

    def click(self, cor_x, cor_y):
        x, y = cor_x, cor_y
        y += self.scroll

        objs = [
            obj
            for obj in tree_to_list(self.document, [])
            if obj.x <= x <= obj.x + obj.width
            if obj.y <= y <= obj.y + obj.height
        ]

        if not objs:
            return
        elt = objs[-1].node

        while elt:
            if isinstance(elt, Text):
                pass
            elif elt.tag == "a" and "href" in elt.attributes:
                url = self.url.resolve(elt.attributes["href"])
                self.load(url)
            elt = elt.parent


def tree_to_list(tree, list):
    list.append(tree)
    for child in tree.children:
        tree_to_list(child, list)
    return list
