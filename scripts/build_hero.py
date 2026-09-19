"""Render the GitHub profile hero as a static PNG using Pillow.

Palette matches pedroventura.com.br dark theme:
  bg          #090A0B
  bg-elevated #0D0E10
  surface-01  #101113
  fg          #F0F0EE
  fg-secondary #B6B7B9
  fg-muted    #6E7077
  brand       #A2FF60
  brand-deep  #89F43D
  info        #7AADFF
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

# ---------- Palette ----------
BG_TOP    = (9, 10, 11)
BG_MID    = (13, 14, 16)
BG_BOT    = (21, 22, 24)
FG        = (240, 240, 238)
FG_2      = (182, 183, 185)
FG_MUTED  = (110, 112, 119)
BRAND     = (162, 255, 96)
BRAND_D   = (137, 244, 61)
INFO      = (122, 173, 255)

# ---------- Canvas ----------
W, H = 1200, 360
RADIUS = 24

# ---------- Fonts ----------
def load_font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except OSError:
            continue
    return ImageFont.load_default()

F_ROLE  = load_font(16, bold=True)
F_H1    = load_font(46, bold=True)
F_BODY  = load_font(17)
F_MONO  = load_font(13)
F_MONO_S= load_font(12)
F_LABEL = load_font(11, bold=True)

# ---------- Helpers ----------
def lerp(a, b, t):
    return a + (b - a) * t

def lerp_rgb(a, b, t):
    return tuple(int(round(lerp(a[i], b[i], t))) for i in range(3))

def rounded_rect_mask(size, radius):
    from PIL import Image as I
    m = I.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle((0, 0, size[0]-1, size[1]-1), radius=radius, fill=255)
    return m

def vertical_gradient(size, top, mid, bot):
    grad = Image.new("RGB", size, top)
    px = grad.load()
    for y in range(size[1]):
        t = y / (size[1] - 1)
        if t < 0.5:
            c = lerp_rgb(top, mid, t * 2)
        else:
            c = lerp_rgb(mid, bot, (t - 0.5) * 2)
        for x in range(size[0]):
            px[x, y] = c
    return grad

def soft_glow(size, center, radius, color, alpha_peak=120):
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(glow)
    for i in range(int(radius), 0, -2):
        t = 1 - i / radius
        a = int(alpha_peak * (t ** 2))
        d.ellipse(
            (center[0] - i, center[1] - i, center[0] + i, center[1] + i),
            fill=(*color, a)
        )
    return glow.filter(ImageFilter.GaussianBlur(radius / 4))

def wave_path(amplitude_a, amplitude_b, phase, samples=48):
    pts = []
    for i in range(samples + 1):
        x = i / samples * W
        y = (
            280
            + math.sin((x / W) * math.pi * 2 + phase) * amplitude_a
            + math.sin((x / W) * math.pi * 4 + phase * 1.3) * (amplitude_a * 0.3)
        )
        pts.append((x, y))
    return pts

# ---------- Render ----------
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Background gradient
bg = vertical_gradient((W, H), BG_TOP, BG_MID, BG_BOT)
img.paste(bg, (0, 0))

# Subtle grid overlay
grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(grid)
for x in range(0, W, 36):
    gd.line([(x, 0), (x, H)], fill=(240, 240, 238, 10), width=1)
for y in range(0, H, 36):
    gd.line([(0, y), (W, y)], fill=(240, 240, 238, 10), width=1)
img.alpha_composite(grid)

# Brand glow (top-right)
glow1 = soft_glow((W, H), (1020, 60), 420, BRAND, alpha_peak=85)
img.alpha_composite(glow1)
# Info glow (bottom-left)
glow2 = soft_glow((W, H), (120, 320), 360, INFO, alpha_peak=55)
img.alpha_composite(glow2)

# Constellation (top-right)
constellation = [(1032, 62, 3.4), (1098, 118, 2.4), (970, 142, 2.2),
                 (1086, 42, 1.8), (950, 62, 1.6), (1100, 96, 1.4)]
for (cx, cy, r) in constellation:
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=BRAND)

# Two waves
phase = 0.6 * math.pi
wave_a = wave_path(amplitude_a=22, amplitude_b=8, phase=phase)
wave_b = wave_path(amplitude_a=14, amplitude_b=6, phase=phase * 1.2 + math.pi)

line_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ld = ImageDraw.Draw(line_layer)
for i in range(len(wave_a) - 1):
    ld.line([wave_a[i], wave_a[i + 1]], fill=(240, 240, 238, 110), width=2)
for i in range(len(wave_b) - 1):
    ld.line([wave_b[i], wave_b[i + 1]], fill=(*INFO, 140), width=2)
img.alpha_composite(line_layer)

# Orbit
orbit_cx, orbit_cy = 960, 220
for r, alpha in [(92, 70), (64, 100), (36, 140)]:
    d_ = r * 2
    orbit_layer = Image.new("RGBA", (d_, d_), (0, 0, 0, 0))
    od = ImageDraw.Draw(orbit_layer)
    od.ellipse((0, 0, d_ - 1, d_ - 1), outline=(*BRAND, alpha), width=1)
    img.alpha_composite(orbit_layer, (orbit_cx - r, orbit_cy - r))

# Satellites at mid-orbit angles
sats = [
    ( 36, math.radians( 35), BRAND,   3.4),
    (-64, math.radians(220), INFO,    2.6),
    ( 92, math.radians(140), BRAND_D, 2.2),
]
for (orbit_r, ang, col, rad) in sats:
    x = orbit_cx + math.cos(ang) * orbit_r
    y = orbit_cy - math.sin(ang) * abs(orbit_r) * (1 if orbit_r > 0 else -1)
    # Use proper parametric: orbit position = center + r*(cos θ, sin θ)
    x = orbit_cx + math.cos(ang) * abs(orbit_r)
    y = orbit_cy + math.sin(ang) * abs(orbit_r)
    draw.ellipse((x - rad, y - rad, x + rad, y + rad), fill=col)

# Core
core_r = 7
draw.ellipse(
    (orbit_cx - core_r, orbit_cy - core_r, orbit_cx + core_r, orbit_cy + core_r),
    fill=FG
)
# Core halo
halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
hd = ImageDraw.Draw(halo)
hd.ellipse(
    (orbit_cx - 16, orbit_cy - 16, orbit_cx + 16, orbit_cy + 16),
    fill=(162, 255, 96, 180)
)
halo = halo.filter(ImageFilter.GaussianBlur(4))
img.alpha_composite(halo)

# Orbit label
label = "LLM  ·  AGENTS  ·  SYSTEMS"
bbox = draw.textbbox((0, 0), label, font=F_LABEL)
lw = (bbox[2] - bbox[0]) if bbox else 200
draw.text((orbit_cx - lw / 2, orbit_cy + 120), label, fill=(*FG_2, 220), font=F_LABEL)

# Accent bar
draw.rounded_rectangle((72, 66, 72 + 160, 72), radius=3, fill=BRAND)

# Title with lime glow
glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd2 = ImageDraw.Draw(glow_layer)
gd2.text((72, 130), "Pedro Henrique", font=F_H1, fill=BRAND)
gd2.text((72, 178), "Assis Ventura", font=F_H1, fill=BRAND)
glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(2.4))
img.alpha_composite(glow_layer)

draw.text((72, 130), "Pedro Henrique", font=F_H1, fill=FG)
draw.text((72, 178), "Assis Ventura", font=F_H1, fill=FG)

# Role
draw.text((74, 224), "SENIOR LLM ENGINEER  ·  AI SYSTEMS ARCHITECT", fill=FG_2, font=F_ROLE)
# Lede
draw.text((74, 274), "Building the layer between intelligence and execution.", fill=FG, font=F_BODY)
# Mono subtitle
draw.text((74, 300), "Agentes · Retrieval · SaaS · Operações reais", fill=FG_MUTED, font=F_MONO)

# Terminal block + bars
term_x, term_y = 74, 320
draw.rounded_rectangle(
    (term_x - 4, term_y - 4, term_x + 460, term_y + 22),
    radius=6,
    outline=(36, 39, 44),
    width=1,
)
for i in range(3):
    bx = term_x + i * 14
    draw.rounded_rectangle((bx, term_y, bx + 8, term_y + 14), radius=2, fill=BRAND)
draw.text((term_x + 56, term_y + 1), 'prompt.compile(model="phventura")', fill=FG_2, font=F_MONO_S)

# CTA pill
cta_x, cta_y, cta_w, cta_h = 720, 296, 220, 44
draw.rounded_rectangle(
    (cta_x, cta_y, cta_x + cta_w, cta_y + cta_h),
    radius=22,
    outline=BRAND,
    width=2,
)
draw.ellipse(
    (cta_x + 15, cta_y + 15, cta_x + 29, cta_y + 29),
    fill=BRAND,
)
draw.text((cta_x + 44, cta_y + 14), "pedroventura.com.br  >>", fill=FG, font=F_BODY)

# Apply rounded mask
mask = rounded_rect_mask((W, H), RADIUS)
out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
out.paste(img, (0, 0), mask)

# Save PNG (lossless) and a JPG preview
png_path = "/Users/pedrohenrique/phventuraogum/assets/hero.png"
out.save(png_path, "PNG", optimize=True)
import os
print(f"Wrote {png_path}: {os.path.getsize(png_path):,} bytes")
