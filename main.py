from telnet.index import URL
from core import Browser

import tkinter

if __name__ == "__main__":
    import sys
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()
