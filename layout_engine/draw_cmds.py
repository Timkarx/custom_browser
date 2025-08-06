class Rect:
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def containsPoint(self, x, y):
        return x >= self.left and x < self.right \
                and y < self.bottom and y >= self.top

class DrawText:
    def __init__(self, rect: Rect, text, font, color):
        self.top, self.bottom = rect.top, rect.bottom
        self.left, self.right = rect.left, rect.right
        self.text = text
        self.font = font
        self.color = color

        self.bottom = self.top  + font.metrics("linespace")

    def execute(self, scroll, canvas):
        canvas.create_text(
            self.left,
            self.top - scroll,
            text=self.text,
            font=self.font,
            anchor="nw",
            fill=self.color,
        )


class DrawRect:
    def __init__(self, rect: Rect, color):
        self.top, self.bottom = rect.top, rect.bottom
        self.left, self.right = rect.left, rect.right
        self.color = color

    def execute(self, scroll, canvas):
        canvas.create_rectangle(
            self.left,
            self.top - scroll,
            self.right,
            self.bottom - scroll,
            width=0,
            fill=self.color,
        )

class DrawOutline:
    def __init__(self, rect: Rect, color, thickness):
        self.top, self.bottom = rect.top, rect.bottom
        self.left, self.right = rect.left, rect.right
        self.rect = rect
        self.color = color
        self.thickness = thickness

    def execute(self, scroll, canvas):
        canvas.create_rectangle(
                self.left, self.top - scroll,
                self.right, self.bottom - scroll,
                width=self.thickness,
                outline=self.color
                )

class DrawLine:
    def __init__(self, rect: Rect, color, thickness):
        self.top, self.bottom = rect.top, rect.bottom
        self.left, self.right = rect.left, rect.right
        self.rect = rect
        self.color = color
        self.thickness = thickness

    def execute(self, scroll, canvas):
        canvas.create_line(
                self.left, self.top - scroll,
                self.right, self.bottom - scroll,
                fill=self.color, width=self.thickness
                )
