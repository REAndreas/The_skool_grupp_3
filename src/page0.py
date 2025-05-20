import taipy.gui.builder as tgb

with tgb.Page() as page_start:
    with tgb.part():
        tgb.text("# TITLE!!", mode="md")
        tgb.text("brödtext", mode="md")