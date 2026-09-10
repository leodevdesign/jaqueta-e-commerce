import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1200, 630
base = Image.new('RGBA', (W, H), (7, 7, 9, 255))
draw = ImageDraw.Draw(base)

# 1. Grid
grid_color = (255, 255, 255, 10)
for x in range(0, W, 60):
    draw.line([(x, 0), (x, H)], fill=grid_color, width=1)
for y in range(0, H, 60):
    draw.line([(0, y), (W, y)], fill=grid_color, width=1)

# 2. Glow
glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
glow_draw = ImageDraw.Draw(glow)
jacket_cx, jacket_cy = 870, 315
for r in range(320, 0, -12):
    alpha = int(48 * (1 - r / 320))
    glow_draw.ellipse([jacket_cx - r, jacket_cy - r, jacket_cx + r, jacket_cy + r], fill=(14, 165, 233, alpha))
for r in range(180, 0, -12):
    alpha = int(28 * (1 - r / 180))
    glow_draw.ellipse([jacket_cx + 80 - r, jacket_cy + 100 - r, jacket_cx + 80 + r, jacket_cy + 100 + r], fill=(234, 88, 12, alpha))

glow = glow.filter(ImageFilter.GaussianBlur(35))
base = Image.alpha_composite(base, glow)
draw = ImageDraw.Draw(base)

# 3. Fonts
def get_font(name, size):
    for p in [f'C:/Windows/Fonts/{name}', 'C:/Windows/Fonts/segoeuib.ttf', 'C:/Windows/Fonts/arialbd.ttf']:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

font_brand = get_font('segoeuib.ttf', 62)
font_sub = get_font('segoeuib.ttf', 24)
font_mono = get_font('consola.ttf', 15)
font_mono_bold = get_font('consolab.ttf', 15)
font_micro = get_font('consola.ttf', 12)
font_badge = get_font('segoeuib.ttf', 13)

# 4. Jacket
jacket_path = 'assets/images/jacket-cutout.png'
jacket = Image.open(jacket_path).convert('RGBA')
target_h = 510
ratio = target_h / jacket.height
target_w = int(jacket.width * ratio)
jacket_resized = jacket.resize((target_w, target_h), Image.Resampling.LANCZOS)

# Shadow
shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
shadow_draw = ImageDraw.Draw(shadow)
jx = jacket_cx - target_w // 2
jy = jacket_cy - target_h // 2 + 10
shadow_draw.ellipse([jx + 40, jy + target_h - 50, jx + target_w - 40, jy + target_h + 30], fill=(0, 0, 0, 180))
shadow = shadow.filter(ImageFilter.GaussianBlur(28))
base = Image.alpha_composite(base, shadow)
base.paste(jacket_resized, (jx, jy), jacket_resized)
draw = ImageDraw.Draw(base)

# 5. Frame & Corners
m = 40
draw.rectangle([m, m, W - m, H - m], outline=(255, 255, 255, 24), width=1)
for cx, cy in [(m, m), (W - m, m), (m, H - m), (W - m, H - m)]:
    draw.line([(cx - 12, cy), (cx + 12, cy)], fill=(56, 189, 248, 200), width=1)
    draw.line([(cx, cy - 12), (cx, cy + 12)], fill=(56, 189, 248, 200), width=1)

# Left Content
lx = m + 40
ly = m + 40

# Monogram Icon
draw.rounded_rectangle([lx, ly, lx + 44, ly + 44], radius=10, fill=(18, 22, 30, 240), outline=(255, 255, 255, 45), width=1)
draw.text((lx + 11, ly + 8), 'Æ', font=get_font('segoeuib.ttf', 22), fill=(248, 250, 252, 255))
draw.ellipse([lx + 32, ly + 10, lx + 37, ly + 15], fill=(234, 88, 12, 255))

draw.text((lx + 58, ly + 6), 'AETHER ARCHITECTURAL APPAREL', font=font_mono_bold, fill=(248, 250, 252, 220))
draw.text((lx + 58, ly + 25), 'COLLECTION 2026 // HAUTE PERFORMANCE CAPSULE', font=font_micro, fill=(56, 189, 248, 220))

# Title
ty = ly + 80
draw.text((lx, ty), 'A E T H E R', font=font_brand, fill=(255, 255, 255, 255))

ty += 78
draw.text((lx, ty), 'HAUTE PERFORMANCE JACKET', font=font_sub, fill=(226, 232, 240, 255))

ty += 44
p1 = 'Architectural outerwear engineered with 4-tier micro-strata,'
p2 = 'aerogel insulation, and bio-responsive titanium telemetry.'
draw.text((lx, ty), p1, font=font_mono, fill=(148, 163, 184, 230))
draw.text((lx, ty + 24), p2, font=font_mono, fill=(148, 163, 184, 230))

ty += 72
chips = [
    ('4-TIER STRATA', (56, 189, 248)),
    ('TITANIUM MEMBRANE', (234, 88, 12)),
    ('ISO 811 CERTIFIED', (148, 163, 184)),
    ('EDITION 100/100', (255, 255, 255))
]
cx_pill = lx
for text, col in chips:
    bbox = draw.textbbox((0, 0), text, font=font_badge)
    pw = bbox[2] - bbox[0] + 24
    ph = 30
    draw.rounded_rectangle([cx_pill, ty, cx_pill + pw, ty + ph], radius=6, fill=(15, 18, 25, 220), outline=(col[0], col[1], col[2], 90), width=1)
    draw.ellipse([cx_pill + 10, ty + 11, cx_pill + 17, ty + 18], fill=col)
    draw.text((cx_pill + 24, ty + 7), text, font=font_badge, fill=(241, 245, 249, 255))
    cx_pill += pw + 12

by = H - m - 32
draw.text((lx, by), 'SYSTEM: READY // VIEWPORT: 1200x630 // PROTOCOL: OPEN_GRAPH_V2', font=font_micro, fill=(100, 116, 139, 200))
draw.text((W - m - 320, by), 'LAT 45.4642 N - ELEV 2400M - 30K/30K', font=font_micro, fill=(100, 116, 139, 200))

out_path = 'assets/images/og-share-aether.png'
base.convert('RGB').save(out_path, 'PNG', quality=95)
print('Generated', out_path)