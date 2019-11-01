from PIL import Image, ImageDraw

def export_image():
    img = Image.new(mode="RGB", size=(1000, 1000), color=(220, 220, 220))
    img.show()
