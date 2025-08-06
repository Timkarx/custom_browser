from telnet.index import URL
from layout_engine.draw_cmds import Rect, DrawText, DrawOutline, DrawLine, DrawRect
from layout_engine.core import get_font

HSTEP, VSTEP = 13, 18
WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100


class Chrome:
    def __init__(self, browser):
        self.browser = browser

        self.focus = None
        self.address_bar = ""

        self.font = get_font(20, "normal", "roman")
        self.font_height = self.font.metrics("linespace")
        self.padding = 5
        self.tabbar_top = 0
        self.tabbar_bottom = self.font_height + 2 * self.padding
        self.urlbar_top = self.tabbar_bottom
        self.urlbar_bottom = self.urlbar_top + self.font_height + 2 * self.padding
        self.bottom = self.urlbar_bottom

        plus_width = self.font.measure("+") + 2 * self.padding
        self.addtab_rect = Rect(
            self.padding,
            self.padding,
            self.padding + plus_width,
            self.padding + self.font_height,
        )

        back_width = self.font.measure("<") + 2 * self.padding
        self.back_rect = Rect(
            self.padding,
            self.padding + self.urlbar_top,
            self.padding + back_width,
            self.urlbar_bottom - self.padding,
        )

        self.address_rect = Rect(
            self.back_rect.right + self.padding,
            self.urlbar_top + self.padding,
            WIDTH - self.padding,
            self.urlbar_bottom - self.padding,
        )

    def tab_rect(self, i):
        tab_start = self.padding + self.addtab_rect.right
        tab_width = self.font.measure("Tab X") + 2 * self.padding
        return Rect(
            tab_start + tab_width * i,
            self.tabbar_top,
            tab_start + tab_width * (i + 1),
            self.tabbar_bottom,
        )

    def paint(self):
        cmds = []
        # Draw white background for browser chrome
        cmds.append(DrawRect(Rect(0, 0, WIDTH, self.bottom), "white"))
        # cmds.append(DrawLine(Rect(0, self.bottom, WIDTH, self.bottom), "black", 1))
        # Paint the add tab "plus" button
        cmds.append(DrawOutline(self.addtab_rect, "black", 1))
        cmds.append(
            DrawText(
                Rect(
                    self.addtab_rect.left + self.padding,
                    self.addtab_rect.top,
                    None,
                    None,
                ),
                "+",
                self.font,
                "black",
            )
        )
        # Paint the back button
        cmds.append(DrawOutline(self.back_rect, "black", 1))
        cmds.append(
            DrawText(
                Rect(
                    self.back_rect.left + self.padding, self.back_rect.top, None, None
                ),
                "<",
                self.font,
                "black",
            )
        )
        # Paint the address bar
        cmds.append(DrawOutline(self.address_rect, "black", 1))
        adress_bar_content = ""
        if self.focus == "address bar":
            address_bar_content = self.address_bar
            w = self.font.measure(self.address_bar)
            cmds.append(
                DrawLine(
                    Rect(
                        self.address_rect.left + self.padding + w,
                        self.address_rect.top,
                        self.address_rect.left + self.padding + w,
                        self.address_rect.bottom,
                    ),
                    "red",
                    1,
                )
            )
        else:
            address_bar_content = str(self.browser.active_tab.url)

        cmds.append(
            DrawText(
                Rect(
                    self.address_rect.left + self.padding,
                    self.address_rect.top,
                    None,
                    None,
                ),
                address_bar_content,
                self.font,
                "black",
            )
        )

        for i, tab in enumerate(self.browser.tabs):
            bounds = self.tab_rect(i)
            # Draw tab separators
            cmds.append(
                DrawLine(Rect(bounds.left, 0, bounds.left, bounds.bottom), "black", 1)
            )
            cmds.append(
                DrawLine(Rect(bounds.right, 0, bounds.right, bounds.bottom), "black", 1)
            )
            # Draw tab number
            cmds.append(
                DrawText(
                    Rect(
                        bounds.left + self.padding,
                        bounds.top + self.padding,
                        None,
                        None,
                    ),
                    "Tab {}".format(i),
                    self.font,
                    "black",
                )
            )

            # Draw "active tab" lines
            if tab == self.browser.active_tab:
                cmds.append(
                    DrawLine(
                        Rect(0, bounds.bottom, bounds.left, bounds.bottom), "black", 1
                    )
                )
                cmds.append(
                    DrawLine(
                        Rect(bounds.right, bounds.bottom, WIDTH, bounds.bottom),
                        "black",
                        1,
                    )
                )

        return cmds

    def click(self, x, y):
        self.focus = None

        if self.addtab_rect.containsPoint(x, y):
            self.browser.new_tab(URL("https://example.org"))
        elif self.back_rect.containsPoint(x, y):
            self.browser.active_tab.go_back()
        elif self.address_rect.containsPoint(x, y):
            self.focus = "address_bar"
            self.address_bar = ""
        else:
            for i, tab in enumerate(self.browser.tabs):
                if self.tab_rect(i).containsPoint(x, y):
                    self.browser.active_tab = tab
                    break
    def keypress(self, char):
        if self.focus == "address bar":
            self.address_bar += char

    def enter(self):
        if self.focus == "address bar":
            self.browser.active_tab.load(URL(self.address_bar))
            self.focus = None
