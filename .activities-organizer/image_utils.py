from html2image import Html2Image
from PIL import Image

def html2png(html, img_file):
    hti = Html2Image()
    hti.screenshot(html_str=html, save_as=img_file)
    im = Image.open(img_file)
    im = im.crop(im.getbbox())
    im.save(img_file)