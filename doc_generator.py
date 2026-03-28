import random
import time
import hashlib
from io import BytesIO
from typing import Tuple, Optional

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    import qrcode
    from barcode import Code128
    from barcode.writer import ImageWriter
except ImportError:
    print("❌ Error: Missing required libraries. Please install: Pillow, qrcode, python-barcode")
    raise

# ============ COLOR PALETTES ============
COLOR_SCHEMES = {
    "blue": {"primary": (0, 51, 102), "secondary": (51, 102, 153), "accent": (255, 255, 255), "text": (51, 51, 51)},
    "navy": {"primary": (0, 0, 80), "secondary": (30, 30, 110), "accent": (255, 255, 255), "text": (45, 45, 45)},
    "maroon": {"primary": (128, 0, 32), "secondary": (160, 40, 72), "accent": (255, 255, 255), "text": (50, 50, 50)},
    "green": {"primary": (34, 85, 51), "secondary": (51, 119, 68), "accent": (255, 255, 255), "text": (48, 48, 48)},
    "purple": {"primary": (75, 0, 130), "secondary": (100, 30, 160), "accent": (255, 255, 255), "text": (55, 55, 55)},
}

def get_random_color_scheme() -> dict:
    return random.choice(list(COLOR_SCHEMES.values()))

def add_simple_noise(img: Image.Image, intensity: int = 3) -> Image.Image:
    pixels = img.load()
    width, height = img.size
    for _ in range(width * height // 10):
        x, y = random.randint(0, width - 1), random.randint(0, height - 1)
        try:
            r, g, b = pixels[x, y][:3]
            r = max(0, min(255, r + random.randint(-intensity, intensity)))
            g = max(0, min(255, g + random.randint(-intensity, intensity)))
            b = max(0, min(255, b + random.randint(-intensity, intensity)))
            pixels[x, y] = (r, g, b, pixels[x, y][3]) if len(pixels[x, y]) == 4 else (r, g, b)
        except:
            pass
    return img

def randomize_position(base_x: int, base_y: int, variance: int = 3) -> Tuple[int, int]:
    return (base_x + random.randint(-variance, variance), base_y + random.randint(-variance, variance))

def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    font_paths = ["arial.ttf", "Arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/System/Library/Fonts/Helvetica.ttc"]
    if bold:
        font_paths = ["arialbd.ttf", "Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] + font_paths
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except:
            continue
    return ImageFont.load_default()

def draw_real_barcode(img: Image.Image, data: str, x: int, y: int, width: int = 140, height: int = 40):
    try:
        # 生成真实条形码
        rv = BytesIO()
        Code128(data, writer=ImageWriter()).write(rv, options={"write_text": False, "module_width": 0.2, "module_height": 5})
        barcode_img = Image.open(rv).convert("RGBA")
        barcode_img = barcode_img.resize((width, height))
        img.paste(barcode_img, (x, y), barcode_img)
    except Exception as e:
        print(f"Barcode error: {e}")

def draw_real_qrcode(img: Image.Image, data: str, x: int, y: int, size: int = 60):
    try:
        qr = qrcode.QRCode(version=1, box_size=2, border=1)
        qr.add_data(data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
        qr_img = qr_img.resize((size, size))
        img.paste(qr_img, (x, y), qr_img)
    except Exception as e:
        print(f"QR code error: {e}")

def process_photo(photo_bytes: bytes, target_w: int, target_h: int) -> Optional[Image.Image]:
    if not photo_bytes: return None
    try:
        user_photo = Image.open(BytesIO(photo_bytes)).convert("RGB")
        # 简单裁剪缩放适应比例
        return user_photo.resize((target_w, target_h))
    except:
        return None

def generate_student_id(first: str, last: str, school: str, major: str = "Computer Science", theme: str = "blue", photo_bytes: bytes = None, export_pdf: bool = False) -> bytes:
    w, h = random.randint(640, 660), random.randint(390, 410)
    bg_color = (255 - random.randint(0, 8), 255 - random.randint(0, 8), 255 - random.randint(0, 8))
    img = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(img)
    
    colors = COLOR_SCHEMES.get(theme, COLOR_SCHEMES["blue"])
    font_lg, font_md, font_sm = get_font(24, True), get_font(18), get_font(14)
    
    # Header
    header_height = 60
    draw.rectangle([(0, 0), (w, header_height)], fill=colors["primary"])
    draw.text((w // 2, header_height // 2), "STUDENT IDENTIFICATION CARD", fill=colors["accent"], font=font_lg, anchor="mm")
    
    # School
    draw.text((w // 2, header_height + 30), school[:50], fill=colors["primary"], font=font_md, anchor="mm")
    
    # Photo Area
    photo_x, photo_y, photo_w, photo_h = 30, 120, 120, 160
    user_img = process_photo(photo_bytes, photo_w, photo_h)
    if user_img:
        img.paste(user_img, (photo_x, photo_y))
        draw.rectangle([(photo_x, photo_y), (photo_x + photo_w, photo_y + photo_h)], outline=colors["primary"], width=3)
    else:
        draw.rectangle([(photo_x, photo_y), (photo_x + photo_w, photo_y + photo_h)], outline=(180, 180, 180), width=2)
        draw.text((photo_x + photo_w // 2, photo_y + photo_h // 2), "PHOTO", fill=(180, 180, 180), font=font_md, anchor="mm")
    
    # Student Info
    student_id = f"STU{random.randint(100000, 999999)}"
    info_x, info_y = photo_x + photo_w + 30, 130
    current_year = int(time.strftime('%Y'))
    
    info_lines = [
        f"Name: {first} {last}",
        f"ID: {student_id}",
        f"Major: {major or 'Computer Science'}",
        f"Valid: {current_year}-{current_year + 1}"
    ]
    
    for line in info_lines:
        draw.text((info_x, info_y), line, fill=colors["text"], font=font_md)
        info_y += 30
    
    # Footer
    footer_y = h - 40
    draw.rectangle([(0, footer_y), (w, h)], fill=colors["primary"])
    draw.text((w // 2, footer_y + 20), "Property of University", fill=colors["accent"], font=font_sm, anchor="mm")
    
    # Real Barcode
    barcode_x = w - 180
    barcode_y = photo_y + photo_h - 40
    draw_real_barcode(img, student_id, barcode_x, barcode_y)
    
    # Real QR Code
    draw_real_qrcode(img, f"Name:{first} {last}|ID:{student_id}", w - 100, 120, size=70)
    
    img = add_simple_noise(img, intensity=random.randint(2, 4))
    
    buf = BytesIO()
    if export_pdf:
        img.save(buf, format="PDF", resolution=100.0)
    else:
        img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()

def generate_teacher_badge(first: str, last: str, school: str, department: str = "Science", theme: str = "green", photo_bytes: bytes = None, export_pdf: bool = False) -> bytes:
    w, h = 500, 350
    img = Image.new("RGB", (w, h), (250, 250, 250))
    draw = ImageDraw.Draw(img)
    
    colors = COLOR_SCHEMES.get(theme, COLOR_SCHEMES["green"])
    font_title, font_text, font_small = get_font(22, True), get_font(16), get_font(12)
    
    # Header
    draw.rectangle([(0, 0), (w, 50)], fill=colors["primary"])
    draw.text((w // 2, 25), "FACULTY ID CARD", fill=colors["accent"], font=font_title, anchor="mm")
    
    draw.text((w // 2, 75), school[:45], fill=colors["primary"], font=font_text, anchor="mm")
    
    # Photo
    photo_x, photo_y, photo_w, photo_h = 25, 100, 100, 120
    user_img = process_photo(photo_bytes, photo_w, photo_h)
    if user_img:
        img.paste(user_img, (photo_x, photo_y))
    else:
        draw.rectangle([(photo_x, photo_y), (photo_x + photo_w, photo_y + photo_h)], outline=(200, 200, 200), width=2)
    
    # Info
    teacher_id = f"T{random.randint(10000, 99999)}"
    info_x, info_y = photo_x + photo_w + 20, 100
    
    info_lines = [
        f"Name: {first} {last}",
        f"ID: {teacher_id}",
        f"Dept: {department or 'Education'}",
        f"Status: Active Faculty"
    ]
    for line in info_lines:
        draw.text((info_x, info_y), line, fill=colors["text"], font=font_text)
        info_y += 25
        
    # QR Code
    draw_real_qrcode(img, f"FACULTY|{teacher_id}|{last}", w - 85, h - 130, size=65)
    
    # Footer
    draw.rectangle([(0, h - 35), (w, h)], fill=colors["primary"])
    draw.text((w // 2, h - 17), "Property of School District", fill=colors["accent"], font=font_small, anchor="mm")
    
    img = add_simple_noise(img, intensity=3)
    buf = BytesIO()
    img.save(buf, format="PDF" if export_pdf else "PNG", resolution=100.0)
    return buf.getvalue()

def generate_transcript(first: str, last: str, dob: str, school: str, major: str = "Business", theme: str = "maroon", export_pdf: bool = False) -> bytes:
    w, h = 800, 1100
    img = Image.new("RGB", (w, h), (252, 252, 252))
    draw = ImageDraw.Draw(img)
    colors = COLOR_SCHEMES.get(theme, COLOR_SCHEMES["maroon"])
    font_title, font_header, font_text = get_font(26, True), get_font(20, True), get_font(14)
    
    # Basics
    draw.text((w // 2, 50), school.upper(), fill=colors["primary"], font=font_title, anchor="mm")
    draw.text((w // 2, 90), "OFFICIAL ACADEMIC TRANSCRIPT", fill=colors["text"], font=font_header, anchor="mm")
    draw.line([(50, 120), (w - 50, 120)], fill=colors["primary"], width=2)
    
    # Info
    y = 150
    info = [("Name:", f"{first} {last}"), ("DOB:", dob), ("Major:", major)]
    for label, val in info:
        draw.text((60, y), label, fill=colors["text"], font=font_text)
        draw.text((200, y), val, fill=colors["text"], font=font_text)
        y += 25
    
    # Table Header
    y += 20
    draw.rectangle([(50, y), (w - 50, y + 30)], fill=colors["primary"])
    draw.text((60, y + 8), "COURSE", fill=colors["accent"], font=font_text)
    draw.text((500, y + 8), "GRADE", fill=colors["accent"], font=font_text)
    
    # Fake Courses
    y += 40
    for i in range(8):
        draw.text((60, y), f"Course Code {random.randint(101, 499)}", fill=colors["text"], font=font_text)
        draw.text((500, y), random.choice(["A", "A-", "B+", "B"]), fill=colors["text"], font=font_text)
        y += 25
        
    # QR at bottom
    draw_real_qrcode(img, f"VERIFY-TRANSCRIPT-{first}-{last}", 60, h - 150, size=80)
    
    img = add_simple_noise(img, intensity=2)
    buf = BytesIO()
    img.save(buf, format="PDF" if export_pdf else "PNG", resolution=150.0)
    return buf.getvalue()
