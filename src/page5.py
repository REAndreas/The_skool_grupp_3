import taipy.gui.builder as tgb
from utils import IMAGE_PATH

img1 = IMAGE_PATH / "students.png"
img2 = IMAGE_PATH / "godkant_beslut.png"


with tgb.Page() as page_storytelling:
    with tgb.part():
        tgb.image(img1, width="900px")
        
    with tgb.part():    
        tgb.image(img2, width="900px")
        
        