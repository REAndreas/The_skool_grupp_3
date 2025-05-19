import taipy.gui.builder as tgb
import pandas as pd
import duckdb as ddb

from taipy.gui import Gui
from pathlib import Path

data_path =  Path(__file__).parent / "data"

navbar_lov = [("/page0", "Start"),("/page1", "Kurser"), ("/page2", "Studerande över tid"), ("/page3", "Kommun karta"), ("/page4", "Utbildningsanordnare") ]


with tgb.Page() as page_root:
    with tgb.part():
        tgb.navbar(lov="{navbar_lov}")

with tgb.Page() as page_start:
    with tgb.part():
        tgb.text("# TITLE!!", mode="md")
        tgb.text("## brödtext", mode="md")

with tgb.Page() as page_kurser:
    with tgb.part():
        tgb.text("Hej1")

with tgb.Page() as page_studerande:
    with tgb.part():
        tgb.text("HEj2")

with tgb.Page() as page_karta:
    with tgb.part():
        tgb.text("HEj3")

with tgb.Page() as page_anordnare:
    with tgb.part():
        tgb.text("HEj4")

pages = {
    "/": page_root,
    "page0": page_start, 
    "page1": page_kurser, 
    "page2": page_studerande, 
    "page3": page_karta, 
    "page4": page_anordnare
}

if __name__ == "__main__":
    Gui(pages=pages).run(dark_mode=True, use_reloader=True, port=8080)