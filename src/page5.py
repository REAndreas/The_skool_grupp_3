import taipy.gui.builder as tgb

with tgb.Page() as page_storytelling:
    with tgb.part():
        tgb.text("Lägg in bilder för storytelling!")
        tgb.image("images/student_storytelling.jpg", width="300px")
        tgb.image("images/storytelling_arbetsmarknaden.jpg", width="300px")