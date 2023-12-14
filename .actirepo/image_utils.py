import os
from html2image import Html2Image
from PIL import Image

def html2png(html, destination_dir, img_file):
    hti = Html2Image()
    hti.output_path = destination_dir
    hti.screenshot(html_str=html, save_as=img_file)
    img_file = os.path.join(destination_dir, img_file)
    im = Image.open(img_file)
    im = im.crop(im.getbbox())
    im.save(img_file)