
from PIL import Image, ImageDraw, ImageFont
import os
import urllib.request

os.makedirs("output", exist_ok=True)

font_url = (
    "https://raw.githubusercontent.com/google/fonts/"
    "main/ofl/notonastaliqurdu/"
    "NotoNastaliqUrdu%5Bwght%5D.ttf"
)
font_path = "NotoNastaliqUrdu.ttf"

print("Downloading Urdu font...")
urllib.request.urlretrieve(font_url, font_path)

font = ImageFont.truetype(font_path, 42)
image = Image.new("RGB", (1280, 720), "#0f172a")
draw = ImageDraw.Draw(image)

draw.text(
    (640, 180),
    "اردو فونٹ ٹیسٹ",
    font=font,
    fill="#facc15",
    anchor="mm",
    direction="rtl"
)

draw.text(
    (640, 300),
    "پانچ مفت AI ٹولز",
    font=font,
    fill="white",
    anchor="mm",
    direction="rtl"
)

draw.text(
    (640, 450),
    "SKILLSEEK URDU",
    font=ImageFont.truetype(font_path, 38),
    fill="#facc15",
    anchor="mm"
)

image.save("output/urdu_font_test.png")
print("SUCCESS: output/urdu_font_test.png created")
