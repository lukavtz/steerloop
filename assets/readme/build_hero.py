"""Compose the README hero and social card from the generated loop artwork.

Source art: assets/readme/loops.png (generated, 1536x1024).
Run:  python assets/readme/build_hero.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
ART = HERE / "loops.png"
BG = (27, 27, 27)
FG = (244, 244, 242)
MUTED = (138, 143, 152)
DIM = (122, 126, 133)
ACCENT = (232, 176, 75)
FONTS = Path("C:/Windows/Fonts")


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


def art_panel(size: tuple[int, int], box: tuple[int, int, int, int]) -> Image.Image:
    """Crop the loops region, resize to `size`, feather the left edge into the background."""
    im = Image.open(ART).convert("RGB").crop(box).resize(size, Image.LANCZOS)
    w, h = size
    mask = Image.new("L", size, 255)
    draw = ImageDraw.Draw(mask)
    fade = int(w * 0.34)
    for x in range(fade):
        draw.line([(x, 0), (x, h)], fill=int(255 * (x / fade) ** 1.6))
    im = im.convert("RGBA")
    im.putalpha(mask)
    return im


def hero() -> None:
    w, h = 1200, 460
    canvas = Image.new("RGB", (w, h), BG)
    panel = art_panel((700, 430), (230, 150, 1480, 920))
    canvas.paste(panel, (500, 16), panel)

    d = ImageDraw.Draw(canvas)
    d.text((72, 104), "AGENT SKILLS  ·  THREE FILES", font=font("consola.ttf", 17), fill=MUTED)
    d.text((72, 146), "steerloop", font=font("segoeuib.ttf", 92), fill=FG)
    d.text((74, 262), "One slice at a time. The agent asks", font=font("segoeui.ttf", 25), fill=(201, 205, 210))
    d.text((74, 296), "before it writes code.", font=font("segoeui.ttf", 25), fill=(201, 205, 210))

    cmd = "npx skills add lukavtz/steerloop"
    cf = font("consola.ttf", 18)
    tw = d.textlength(cmd, font=cf)
    d.rounded_rectangle([72, 350, 72 + tw + 36, 392], radius=8, outline=(70, 70, 70), width=1)
    d.text((90, 362), cmd, font=cf, fill=ACCENT)

    d.line([(72, 420), (72 + tw + 36, 420)], fill=(58, 58, 58))
    d.text((72, 430), "skills/steerloop · skills/craftloop · skills/webperf · MIT", font=font("consola.ttf", 14), fill=DIM)
    canvas.save(HERE / "hero.png", optimize=True)


def social() -> None:
    w, h = 1200, 630
    canvas = Image.new("RGB", (w, h), BG)
    panel = art_panel((700, 590), (200, 120, 1480, 940))
    canvas.paste(panel, (500, 20), panel)
    d = ImageDraw.Draw(canvas)
    d.text((72, 96), "AGENT SKILLS · THREE", font=font("consola.ttf", 18), fill=MUTED)
    d.text((70, 140), "steerloop", font=font("segoeuib.ttf", 96), fill=FG)
    d.text((74, 262), "One slice at a time.", font=font("segoeui.ttf", 28), fill=(201, 205, 210))
    d.text((74, 300), "The agent asks before", font=font("segoeui.ttf", 28), fill=(201, 205, 210))
    d.text((74, 338), "it writes code.", font=font("segoeui.ttf", 28), fill=(201, 205, 210))
    d.text((74, 520), "npx skills add lukavtz/steerloop", font=font("consola.ttf", 20), fill=ACCENT)
    canvas.save(HERE / "social.png", optimize=True)


if __name__ == "__main__":
    hero()
    social()
    print("wrote hero.png and social.png")
