from telnet.index import URL
from parser.html.core import HTMLParser, print_tree

if __name__ == "__main__":
    import sys
    body = URL(sys.argv[1]).request()
    nodes = HTMLParser(body).parse()
    print_tree(nodes)
