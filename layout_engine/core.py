from layout_engine.draw_cmds import DrawText, DrawRect, Rect
from parser.html.core import Text, Element
import tkinter.font

HSTEP, VSTEP = 13, 18
WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100

FONTS = {}

BLOCK_ELEMENTS = [
    "html",
    "body",
    "article",
    "section",
    "nav",
    "aside",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hgroup",
    "header",
    "footer",
    "address",
    "p",
    "hr",
    "pre",
    "blockquote",
    "ol",
    "ul",
    "menu",
    "li",
    "dl",
    "dt",
    "dd",
    "figure",
    "figcaption",
    "main",
    "div",
    "table",
    "form",
    "fieldset",
    "legend",
    "details",
    "summary",
]


class DocumentLayout:
    def __init__(self, node: Element):
        self.node = node
        self.parent = None
        self.children = []

        self.x = None
        self.y = None
        self.width = None
        self.height = None

    def layout(self):
        child = BlockLayout(self.node, self, None)
        self.children.append(child)

        self.x = HSTEP
        self.y = VSTEP
        self.width = WIDTH - 2 * HSTEP
        child.layout()
        self.height = child.height

    def paint(self):
        return []


class BlockLayout:
    # Every BlockLayout has a corresponding html node (Element or Text)
    def __init__(self, node, parent, previous):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []

        self.x = None
        self.y = None
        self.width = None
        self.height = None

    def paint(self):
        cmds = []
        bgcolor = self.node.style.get("background-color", "transparent")
        if bgcolor != "transparent":
            x2 = self.x + self.width
            y2 = self.y + self.height
            rect = DrawRect(self.rect(), bgcolor)
            cmds.append(rect)
        return cmds

    def layout(self):
        self.x = self.parent.x
        self.width = self.parent.width
        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y

        mode = self.layout_mode()
        if mode == "block":
            self.layout_intermediate()
        else:
            self.new_line()
            self.recurse(self.node)

        for child in self.children:
            child.layout()

        self.height = sum([child.height for child in self.children])

    def layout_intermediate(self):
        previous = None
        for child in self.node.children:
            next = BlockLayout(child, self, previous)
            self.children.append(next)
            previous = next

    def layout_mode(self):
        if isinstance(self.node, Text):
            return "inline"
        # Block if any child is block
        elif any(
            [
                isinstance(child, Element) and child.tag in BLOCK_ELEMENTS
                for child in self.node.children
            ]
        ):
            return "block"
        # Inline if all children are inline
        elif self.node.children:
            return "inline"
        else:
            return "block"

    def rect(self):
        return Rect(self.x, self.y, self.x + self.width, self.y + self.height)

    def recurse(self, node):
        if isinstance(node, Text):
            for word in node.text.split():
                self.word(node, word)
        else:
            if node.tag == "br":
                self.new_line()
            for child in node.children:
                self.recurse(child)

    def word(self, node, word):
        color = node.style["color"]
        weight = node.style["font-weight"]
        style = node.style["font-style"]
        if style == "normal": style = "roman"
        size = int(float(node.style["font-size"][:-2]) * 0.75)
        font = get_font(size, weight, style) 

        w = font.measure(word)

        if self.cursor_x + w >= self.width:
            self.new_line()
        line = self.children[-1]
        previous_word = line.children[-1] if line.children else None
        next_word = TextLayout(node, word, line, previous_word)
        line.children.append(next_word)

    def new_line(self):
        self.cursor_x = 0
        last_line = self.children[-1] if self.children else None
        new_line = LineLayout(self.node, self, last_line)
        self.children.append(new_line)

#    def flush(self):
#        if not self.line:
#            return
#        metrics = [font.metrics() for x, word, font, color in self.line]
#        max_ascent = max(metric["ascent"] for metric in metrics)
#        baseline = self.cursor_y + 1.25 * max_ascent
#
#        for rel_x, word, font, color in self.line:
#            x = self.x + rel_x
#            y = self.y + baseline - font.metrics("ascent")
#            self.display_list.append((x, y, word, font, color))
#
#        max_descent = max([metric["descent"] for metric in metrics])
#        self.cursor_y = baseline + 1.25 * max_descent
#
#        self.cursor_x = 0
#        self.line = []


class LineLayout:
    def __init__(self, node, parent, previous):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []

    def layout(self):
        self.width = self.parent.width
        self.x = self.parent.x

        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y

        for word in self.children:
            word.layout()

        max_ascent = max([word.font.metrics("ascent") for word in self.children])
        baseline = self.y + 1.25 * max_ascent
        for word in self.children:
            word.y = baseline - word.font.metrics("ascent")
        max_descent = max([word.font.metrics("descent") for word in self.children])

        self.height = 1.25 * (max_ascent + max_descent)

    def paint(self):
        return []

class TextLayout:
    def __init__(self, node, word, parent, previous):
        self.node = node
        self.word = word
        self.children = []
        self.parent = parent
        self.previous = previous

    def layout(self):
        color = self.node.style["color"]
        weight = self.node.style["font-weight"]
        style = self.node.style["font-style"]
        if style == "normal":
            style = "roman"
        size = int(float(self.node.style["font-size"][:-2]) * 0.75)
        self.font = get_font(size, weight, style)

        self.width = self.font.measure(self.word)

        if self.previous:
            space = self.font.measure(" ")
            self.x = self.previous.x + self.previous.width + space
        else:
            self.x = self.parent.x

        self.height = self.font.metrics("linespace")

    def rect(self):
        return Rect(self.x, self.y, self.x + self.width, self.y + self.height)

    def paint(self):
        color = self.node.style["color"]
        return [DrawText(self.rect(), self.word, self.font, color)]

def paint_tree(layout_object, display_list):
    display_list.extend(layout_object.paint())

    for child in layout_object.children:
        paint_tree(child, display_list)


def get_font(size, weight, style):
    key = (size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(size=size, weight=weight, slant=style)
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    return FONTS[key][0]
