import taipy.gui.builder as tgb

with tgb.Page() as page_start:
    with tgb.part():
        tgb.text("# The Skools YH-kollen", mode="md")
        tgb.text("En enkel dashboard för att utforska **Myndigheten för Yrkeshögskolans** statistik.", mode="md")