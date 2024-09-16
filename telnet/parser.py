import re

class Text:
    def __init__(self, text):
        self.text = text

class Tag:
    def __init__(self, tag):
        self.tag = tag

class NewLine:
    def __init__(self):
        pass

def lex(body):
        out = []
        buffer = ""
        in_tag = False
        for c in body:
            if c == "<":
                in_tag = True
                if buffer: out.append(Text(buffer))
                buffer = ""
            elif c == ">":
                in_tag = False
                out.append(Tag(buffer))
                buffer = ""
            # elif c == "\n":
            #     if buffer and not in_tag: out.append(Text(buffer))
            #     out.append(NewLine())
            #     buffer = ""
            else:
                buffer += c
        # text = parse_entities(text)
        if not in_tag and buffer:
            out.append(Text(buffer))
        return out

def parse_entities(text):
        text = re.sub("&lt;", "<", text)
        text = re.sub("&gt;", ">", text)
        return text
