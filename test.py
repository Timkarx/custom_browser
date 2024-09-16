from telnet.index import URL, lex

if __name__ == "__main__":
    import sys
    content = URL(sys.argv[1]).request()
    document = lex(content)
    print(document)
