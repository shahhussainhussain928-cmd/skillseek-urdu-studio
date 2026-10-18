
import json
import os
import subprocess
import urllib.request
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

WIDTH, HEIGHT = 1280, 720
FPS = 30
BG = "#0f172a"
YELLOW = "#facc15"
WHITE = "#ffffff"

os.makedirs("output/scenes", exist_ok=True)

FONT_URL = (
    "https://raw.githubusercontent.com/google/fonts/main/"
    "ofl/notonastaliqurdu/NotoNastaliqUrdu%5Bwght%5D.ttf"
)
FONT_PATH = "NotoNastaliqUrdu.ttf"

def get_font(size):
    return ImageFont.truetype(FONT_PATH, size)

def urdu(text):
    return get_display(arabic_reshaper.reshape(str(text)))

def draw_centered(draw, text, y, font, color):
    draw.text(
        (WIDTH // 2, y),
        urdu(text),
        font=font,
        fill=color,
        anchor="mm",
        direction="rtl"
    )

def create_scene(scene, index, total):
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    # Decorative border and accent bars
    draw.rounded_rectangle(
        (35, 35, WIDTH - 35, HEIGHT - 35),
        radius=28,
        outline=YELLOW,
        width=3
    )
    draw.rounded_rectangle(
        (70, 75, 85, HEIGHT - 75),
        radius=7,
        fill=YELLOW
    )
    draw.rounded_rectangle(
        (WIDTH - 85, 75, WIDTH - 70, HEIGHT - 75),
        radius=7,
        fill=YELLOW
    )

    # Brand header
    draw.text(
        (WIDTH // 2, 105),
        "SKILLSEEK URDU",
        font=get_font(27),
        fill=YELLOW,
        anchor="mm"
    )

    # Scene heading
    draw_centered(
        draw,
        scene["heading"],
        205,
        get_font(43),
        YELLOW
    )

    # Scene content
    lines = scene["lines"]
    start_y = 315 if len(lines) <= 4 else 300
    gap = 62 if len(lines) <= 4 else 54

    for line_number, line in enumerate(lines):
        y = start_y + line_number * gap
        draw_centered(
            draw,
            line,
            y,
            get_font(29 if len(line) > 38 else 34),
            WHITE
        )

    # Progress indicator
    bar_x, bar_y = 120, 625
    bar_width = WIDTH - 240
    draw.rounded_rectangle(
        (bar_x, bar_y, bar_x + bar_width, bar_y + 10),
        radius=5,
        fill="#334155"
    )
    progress = int(bar_width * (index + 1) / total)
    draw.rounded_rectangle(
        (bar_x, bar_y, bar_x + progress, bar_y + 10),
        radius=5,
        fill=YELLOW
    )

    draw.text(
        (WIDTH // 2, 665),
        f"{index + 1:02d} / {total:02d}",
        font=get_font(20),
        fill=WHITE,
        anchor="mm"
    )

    path = f"output/scenes/scene_{index + 1:02d}.png"
    image.save(path)
    print(f"Created {path}")

def main():
    print("Downloading Urdu font...")
    urllib.request.urlretrieve(FONT_URL, FONT_PATH)

    with open("video_content.json", encoding="utf-8") as file:
        data = json.load(file)

    scenes = data["scenes"]
    if len(scenes) != 10:
        raise ValueError("Expected exactly 10 scenes")

    for index, scene in enumerate(scenes):
        create_scene(scene, index, len(scenes))

    # Each scene is a 30-second clip with subtle zoom animation.
    inputs = []
    filters = []

    for index, scene in enumerate(scenes):
        inputs += [
            "-loop", "1",
            "-framerate", str(FPS),
            "-t", str(scene["duration"]),
            "-i", f"output/scenes/scene_{index + 1:02d}.png"
        ]

        filters.append(
            f"[{index}:v]"
            f"scale={WIDTH}:{HEIGHT},"
            f"zoompan=z='min(zoom+0.00015,1.04)':"
            f"x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d=1:s={WIDTH}x{HEIGHT}:fps={FPS},"
            f"trim=duration={scene['duration']},"
            f"setpts=PTS-STARTPTS,"
            f"setsar=1[v{index}]"
        )

    joined = "".join(f"[v{i}]" for i in range(len(scenes)))
    filters.append(
        f"{joined}concat=n={len(scenes)}:v=1:a=0[outv]"
    )

    command = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", ";".join(filters),
        "-map", "[outv]",
        "-an",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-t", "300",
        "output/skillseek_urdu_ai_tools.mp4"
    ]

    print("Rendering the five-minute video...")
    subprocess.run(command, check=True)

    print("SUCCESS: output/skillseek_urdu_ai_tools.mp4")

if __name__ == "__main__":
    main()

