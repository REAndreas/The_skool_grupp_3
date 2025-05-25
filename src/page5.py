import taipy.gui.builder as tgb

img1 = "images/students.png"
img2 = "images/godkant_beslut.png"


with tgb.Page() as page_storytelling:
    with tgb.part():
        tgb.text("GRAF 1")
        tgb.image(img1, width="900px")
        
    with tgb.part():
        tgb.text("GRAF 2")    
        tgb.image(img2, width="900px")
        
        