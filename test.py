from telnet.index import URL
from telnet.parser import HTMLParser, print_tree
from gui.index import Browser
import tkinter

if __name__ == "__main__":
    import sys
    body = URL(sys.argv[1]).request()
    nodes = HTMLParser(body).parse()
    print_tree(nodes)
