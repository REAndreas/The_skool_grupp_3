import taipy.gui.builder as tgb

from taipy.gui import Gui
from page0 import page_start
from page1 import page_kurser
from page2 import page_studerande
from page3 import page_karta
from page4 import page_anordnare
from page5 import page_storytelling

navbar_lov = [
    ("/page0", "Start"),
    ("/page1", "Kurser"), 
    ("/page2", "Studerande över tid"), 
    ("/page3", "Kommun karta"), 
    ("/page4", "Utbildningsanordnare"),
    ("/page5", "Storytelling") 
    ]


with tgb.Page() as page_root:
    with tgb.part():
        tgb.navbar(lov="{navbar_lov}")

pages = {
    "/": page_root,
    "page0": page_start, 
    "page1": page_kurser, 
    "page2": page_studerande, 
    "page3": page_karta, 
    "page4": page_anordnare,
    "page5": page_storytelling
}

if __name__ == "__main__":
    Gui(pages=pages).run(dark_mode=True, use_reloader=True, port=8080)