"""
生成农历闹钟 App 的 PNG 图标（纯标准库，无需 Pillow）
使用 BMP 格式写入，再转为 PNG
"""
import struct, zlib, math, os

OUT_DIR = r"C:\Users\lin\WorkBuddy\Claw\icons"
os.makedirs(OUT_DIR, exist_ok=True)

def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))

def draw_icon(size):
    s = size
    # RGBA 像素数组，初始化为透明
    pixels = [[0, 0, 0, 0] for _ in range(s * s)]

    def set_pixel(x, y, r, g, b, a=255):
        if 0 <= x < s and 0 <= y < s:
            idx = y * s + x
            # 简单 alpha 混合
            sa = a / 255.0
            da = pixels[idx][3] / 255.0
            out_a = sa + da * (1 - sa)
            if out_a > 0:
                pixels[idx][0] = clamp((r * sa + pixels[idx][0] * da * (1 - sa)) / out_a)
                pixels[idx][1] = clamp((g * sa + pixels[idx][1] * da * (1 - sa)) / out_a)
                pixels[idx][2] = clamp((b * sa + pixels[idx][2] * da * (1 - sa)) / out_a)
                pixels[idx][3] = clamp(out_a * 255)

    def fill_rect(x0, y0, w, h, r, g, b, a=255):
        for yy in range(y0, y0 + h):
            for xx in range(x0, x0 + w):
                set_pixel(xx, yy, r, g, b, a)

    def fill_circle(cx, cy, radius, r, g, b, a=255):
        for yy in range(cy - radius, cy + radius + 1):
            for xx in range(cx - radius, cx + radius + 1):
                dist = math.sqrt((xx - cx)**2 + (yy - cy)**2)
                if dist <= radius:
                    aa = min(255, int(255 * max(0, radius - dist + 1)))
                    set_pixel(xx, yy, r, g, b, min(a, aa))

    def fill_ellipse(cx, cy, rx, ry, r, g, b, a=255):
        for yy in range(cy - ry, cy + ry + 1):
            for xx in range(cx - rx, cx + rx + 1):
                dist = ((xx - cx) / max(rx, 1))**2 + ((yy - cy) / max(ry, 1))**2
                if dist <= 1.0:
                    edge = max(rx, ry) * (1.0 - math.sqrt(dist))
                    aa = min(255, int(255 * min(1.0, edge)))
                    set_pixel(xx, yy, r, g, b, min(a, aa))

    def draw_ellipse_border(cx, cy, rx, ry, thick, r, g, b, a=255):
        for yy in range(cy - ry - thick, cy + ry + thick + 1):
            for xx in range(cx - rx - thick, cx + rx + thick + 1):
                dist = ((xx - cx) / max(rx, 1))**2 + ((yy - cy) / max(ry, 1))**2
                inner = ((xx - cx) / max(rx - thick, 1))**2 + ((yy - cy) / max(ry - thick, 1))**2
                if dist <= 1.0 and inner >= 1.0:
                    set_pixel(xx, yy, r, g, b, a)

    def draw_line(x0, y0, x1, y1, thick, r, g, b, a=200):
        dx, dy = x1 - x0, y1 - y0
        length = max(1, math.sqrt(dx*dx + dy*dy))
        steps = int(length * 2)
        for i in range(steps + 1):
            t = i / max(steps, 1)
            px = x0 + dx * t
            py = y0 + dy * t
            for tx in range(-thick, thick + 1):
                for ty in range(-thick, thick + 1):
                    if tx*tx + ty*ty <= thick*thick:
                        set_pixel(int(px+tx), int(py+ty), r, g, b, a)

    def rounded_rect_bg(x0, y0, w, h, corner, r, g, b, a=255):
        # 填充矩形
        fill_rect(x0 + corner, y0, w - 2*corner, h, r, g, b, a)
        fill_rect(x0, y0 + corner, w, h - 2*corner, r, g, b, a)
        # 四角圆
        for cx2, cy2 in [
            (x0 + corner, y0 + corner),
            (x0 + w - corner - 1, y0 + corner),
            (x0 + corner, y0 + h - corner - 1),
            (x0 + w - corner - 1, y0 + h - corner - 1)
        ]:
            fill_circle(cx2, cy2, corner, r, g, b, a)

    # ─── 绘制 ───
    corner = int(s * 0.2)
    rounded_rect_bg(0, 0, s, s, corner, 15, 6, 0, 255)

    cx = s // 2
    cy = s // 2
    lrx = int(s * 0.23)   # 灯笼横半径
    lry = int(s * 0.27)   # 灯笼纵半径

    # 灯笼体
    fill_ellipse(cx, cy, lrx, lry, 192, 57, 43, 255)
    # 高光
    fill_ellipse(cx - lrx//3, cy - lry//4, lrx//4, lry//5, 230, 90, 70, 120)
    # 金边
    thick = max(1, s // 48)
    draw_ellipse_border(cx, cy, lrx, lry, thick, 212, 160, 23, 255)

    # 顶底盖
    capw = int(lrx * 1.1)
    caph = max(2, int(s * 0.065))
    fill_rect(cx - capw//2, cy - lry - caph, capw, caph, 212, 160, 23)
    fill_rect(cx - capw//2, cy + lry, capw, caph, 212, 160, 23)

    # 绳子
    if s >= 96:
        rope_h = int(s * 0.06)
        draw_line(cx, cy - lry - caph - rope_h, cx, cy - lry - caph, 1, 212, 160, 23)

    # 竖纹
    if s >= 96:
        for i in range(-2, 3):
            px = cx + i * (lrx // 2)
            ratio = abs((px - cx) / max(lrx, 1))
            if ratio < 0.95:
                hh = int(math.sqrt(max(0, 1 - ratio**2)) * lry)
                draw_line(px, cy - hh, px, cy + hh, max(1, s//120), 212, 160, 23, 80)

    # 流苏
    if s >= 96:
        tassel_y = cy + lry + caph
        tassel_len = int(s * 0.09)
        for off in [-0.22, -0.11, 0, 0.11, 0.22]:
            tx = int(cx + lrx * off)
            draw_line(tx, tassel_y, tx, tassel_y + tassel_len, 1, 212, 160, 23, 180)

    # 文字"农"（使用几何线条拼）
    # 简化：在中心画几条线模拟汉字笔画
    fs = int(s * 0.22)
    fc = cy + int(s * 0.02)
    # 横
    draw_line(cx - fs//2, fc - fs//3, cx + fs//2, fc - fs//3, max(1, s//80), 255, 224, 102)
    # 撇 - 从中上到左下
    draw_line(cx, fc - fs//3, cx - fs//2, fc + fs//2, max(1, s//80), 255, 224, 102)
    # 捺 - 从中上到右下
    draw_line(cx, fc - fs//3, cx + fs//2, fc + fs//2, max(1, s//80), 255, 224, 102)
    # 中竖
    draw_line(cx, fc - fs//3, cx, fc + fs//2, max(1, s//80), 255, 224, 102)
    # 冖横
    draw_line(cx - fs//3, fc - fs//8, cx + fs//3, fc - fs//8, max(1, s//90), 255, 224, 102)

    return pixels

def encode_png(pixels, size):
    s = size
    def chunk(name, data):
        c = zlib.crc32(name + data) & 0xffffffff
        return struct.pack('>I', len(data)) + name + data + struct.pack('>I', c)

    ihdr_data = struct.pack('>IIBBBBB', s, s, 8, 2, 0, 0, 0)  # 8-bit RGB
    # 转为 RGB（去掉 alpha，用背景色合成）
    raw = b''
    for y in range(s):
        raw += b'\x00'  # filter type None
        for x in range(s):
            p = pixels[y * s + x]
            # alpha blend onto dark background
            a = p[3] / 255.0
            r = clamp(p[0] * a + 15 * (1 - a))
            g2 = clamp(p[1] * a + 6 * (1 - a))
            b = clamp(p[2] * a + 0 * (1 - a))
            raw += bytes([r, g2, b])
    
    compressed = zlib.compress(raw, 9)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr_data)
    png += chunk(b'IDAT', compressed)
    png += chunk(b'IEND', b'')
    return png

sizes = [72, 96, 128, 144, 152, 192, 384, 512]
for s in sizes:
    print(f"Generating icon-{s}.png ...", flush=True)
    px = draw_icon(s)
    png_data = encode_png(px, s)
    out_path = os.path.join(OUT_DIR, f"icon-{s}.png")
    with open(out_path, 'wb') as f:
        f.write(png_data)
    print(f"  Saved {len(png_data)} bytes -> {out_path}")

print("All icons generated!")
