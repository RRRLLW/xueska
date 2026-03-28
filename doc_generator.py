import random
import time
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
    "blue": {"primary": (10, 50, 100), "secondary": (51, 102, 153), "accent": (255, 255, 255), "text": (40, 40, 40)},
    "navy": {"primary": (0, 20, 60), "secondary": (30, 30, 110), "accent": (255, 255, 255), "text": (45, 45, 45)},
    "maroon": {"primary": (115, 0, 10), "secondary": (160, 40, 72), "accent": (255, 255, 255), "text": (50, 50, 50)},
    "green": {"primary": (20, 70, 40), "secondary": (51, 119, 68), "accent": (255, 255, 255), "text": (48, 48, 48)},
    "purple": {"primary": (70, 20, 110), "secondary": (100, 30, 160), "accent": (255, 255, 255), "text": (55, 55, 55)},
}

def add_simple_noise(img: Image.Image, intensity: int = 2) -> Image.Image:
    # 模拟真实纸张或卡片打印的微小噪点
    pixels = img.load()
    width, height = img.size
    for _ in range(width * height // 15):
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

def draw_real_barcode(img: Image.Image, data: str, x: int, y: int, width: int = 200, height: int = 50):
    try:
        rv = BytesIO()
        Code128(data, writer=ImageWriter()).write(rv, options={"write_text": False, "module_width": 0.2, "module_height": 5})
        barcode_img = Image.open(rv).convert("RGBA").resize((width, height))
        img.paste(barcode_img, (x, y), barcode_img)
    except Exception as e:
        pass

def draw_real_qrcode(img: Image.Image, data: str, x: int, y: int, size: int = 60):
    try:
        qr = qrcode.QRCode(version=1, box_size=2, border=1)
        qr.add_data(data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA").resize((size, size))
        img.paste(qr_img, (x, y), qr_img)
    except Exception as e:
        pass

def process_photo(photo_bytes: bytes, target_w: int, target_h: int) -> Optional[Image.Image]:
    if not photo_bytes: return None
    try:
        user_photo = Image.open(BytesIO(photo_bytes)).convert("RGB")
        # 居中裁剪适应比例
        img_ratio = user_photo.width / user_photo.height
        target_ratio = target_w / target_h
        if img_ratio > target_ratio:
            new_w = int(user_photo.height * target_ratio)
            left = (user_photo.width - new_w) // 2
            user_photo = user_photo.crop((left, 0, left + new_w, user_photo.height))
        else:
            new_h = int(user_photo.width / target_ratio)
            top = (user_photo.height - new_h) // 2
            user_photo = user_photo.crop((0, top, user_photo.width, top + new_h))
        return user_photo.resize((target_w, target_h))
    except:
        return None

def generate_student_id(first: str, last: str, school: str, major: str = "Computer Science", theme: str = "blue", photo_bytes: bytes = None, export_pdf: bool = False, custom_id: str = "", valid_date: str = "") -> bytes:
    # 采用现代化的竖版设计 (Vertical Layout)
    w, h = 600, 940 
    bg_color = (248, 248, 250)
    img = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(img)
    
    colors = COLOR_SCHEMES.get(theme, COLOR_SCHEMES["blue"])
    font_xl = get_font(36, True)
    font_lg = get_font(28, True)
    font_md = get_font(22)
    font_sm = get_font(16)
    
    # 1. 绘制背景暗纹水印 (伪造防伪涂层)
    draw.ellipse([(w//2 - 200, h//2 - 200), (w//2 + 200, h//2 + 200)], outline=(230, 230, 235), width=10)
    draw.ellipse([(w//2 - 180, h//2 - 180), (w//2 + 180, h//2 + 180)], outline=(235, 235, 240), width=2)
    
    # 2. 顶部 Header
    header_height = 140
    draw.rectangle([(0, 0), (w, header_height)], fill=colors["primary"])
    draw.text((w // 2, 50), school.upper(), fill=colors["accent"], font=font_lg, anchor="mm")
    draw.text((w // 2, 95), "STUDENT IDENTIFICATION", fill=colors["accent"], font=font_sm, anchor="mm")
    
    # 3. 居中大头照
    photo_w, photo_h = 240, 320
    photo_x = (w - photo_w) // 2
    photo_y = 180
    user_img = process_photo(photo_bytes, photo_w, photo_h)
    
    # 照片外框防伪线
    draw.rectangle([(photo_x-4, photo_y-4), (photo_x + photo_w + 4, photo_y + photo_h + 4)], fill=colors["primary"])
    
    if user_img:
        img.paste(user_img, (photo_x, photo_y))
    else:
        draw.rectangle([(photo_x, photo_y), (photo_x + photo_w, photo_y + photo_h)], fill=(220, 220, 220))
        draw.text((photo_x + photo_w // 2, photo_y + photo_h // 2), "PHOTO", fill=(150, 150, 150), font=font_md, anchor="mm")
    
    # 4. 学生信息区
    student_id = custom_id if custom_id else f"900{random.randint(100000, 999999)}"
    current_year = int(time.strftime('%Y'))
    valid_str = valid_date if valid_date else f"EXP: 08/{current_year + 4}"
    
    name_y = photo_y + photo_h + 40
    draw.text((w // 2, name_y), f"{first.upper()} {last.upper()}", fill=colors["text"], font=font_xl, anchor="mm")
    draw.text((w // 2, name_y + 40), major.upper(), fill=colors["primary"], font=font_md, anchor="mm")
    
    # ID & EXP 左右排版
    draw.text((w // 2 - 120, name_y + 90), f"ID: {student_id}", fill=colors["text"], font=font_lg, anchor="lm")
    draw.text((w // 2 + 120, name_y + 90), valid_str, fill=(180, 50, 50), font=font_md, anchor="rm")
    
    # 5. 底部条形码区
    draw_real_barcode(img, student_id, (w - 300) // 2, h - 180, width=300, height=60)
    
    footer_y = h - 60
    draw.rectangle([(0, footer_y), (w, h)], fill=colors["primary"])
    draw.text((w // 2, footer_y + 30), f"Library: 2{student_id}55", fill=colors["accent"], font=font_sm, anchor="mm")
    
    img = add_simple_noise(img, intensity=2)
    buf = BytesIO()
    img.save(buf, format="PDF" if export_pdf else "PNG", resolution=300.0)
    return buf.getvalue()

def generate_transcript(first: str, last: str, dob: str, school: str, major: str = "Business", theme: str = "maroon", export_pdf: bool = False, custom_id: str = "", valid_date: str = "") -> bytes:
    # 采用高分辨率 A4 比例，模拟打印扫描件
    w, h = 1240, 1754 
    img = Image.new("RGB", (w, h), (250, 252, 250)) # 略带米白色的纸张质感
    draw = ImageDraw.Draw(img)
    colors = COLOR_SCHEMES.get(theme, COLOR_SCHEMES["maroon"])
    
    font_xl = get_font(38, True)
    font_lg = get_font(24, True)
    font_md = get_font(18, True)
    font_sm = get_font(16)
    
    # 背景大水印
    draw.ellipse([(w//2 - 400, h//2 - 400), (w//2 + 400, h//2 + 400)], outline=(240, 240, 245), width=2)
    draw.text((w // 2, h // 2), "OFFICIAL WATERMARK", fill=(240, 240, 245), font=font_xl, anchor="mm")
    
    # 1. 顶部 Header
    draw.text((w // 2, 120), school.upper(), fill=colors["primary"], font=font_xl, anchor="mm")
    draw.text((w // 2, 180), "OFFICIAL ACADEMIC TRANSCRIPT", fill=colors["text"], font=font_lg, anchor="mm")
    draw.line([(100, 220), (w - 100, 220)], fill=colors["primary"], width=4)
    
    # 2. 学生基础信息 (左右两列排版)
    stu_id = custom_id if custom_id else f"S{random.randint(1000000, 9999999)}"
    issued = valid_date if valid_date else time.strftime('%Y-%m-%d')
    
    draw.text((120, 260), "STUDENT INFORMATION", fill=colors["primary"], font=font_md)
    draw.text((120, 290), f"Name: {first.upper()} {last.upper()}", fill=colors["text"], font=font_sm)
    draw.text((120, 320), f"Student ID: {stu_id}", fill=colors["text"], font=font_sm)
    draw.text((120, 350), f"Date of Birth: {dob}", fill=colors["text"], font=font_sm)
    
    draw.text((800, 260), "ACADEMIC PROGRAM", fill=colors["primary"], font=font_md)
    draw.text((800, 290), f"Degree: Bachelor of Science", fill=colors["text"], font=font_sm)
    draw.text((800, 320), f"Major: {major}", fill=colors["text"], font=font_sm)
    draw.text((800, 350), f"Issued Date: {issued}", fill=colors["text"], font=font_sm)
    
    # 3. 课程成绩区 (按学期切分)
    y_offset = 420
    
    def draw_semester_block(term_name, courses, y):
        draw.rectangle([(100, y), (w - 100, y + 30)], fill=colors["primary"])
        draw.text((120, y + 6), f"TERM: {term_name}", fill=colors["accent"], font=font_md)
        y += 40
        
        # 表头
        draw.text((120, y), "COURSE CODE", fill=colors["text"], font=font_md)
        draw.text((350, y), "COURSE TITLE", fill=colors["text"], font=font_md)
        draw.text((850, y), "CREDITS", fill=colors["text"], font=font_md)
        draw.text((950, y), "GRADE", fill=colors["text"], font=font_md)
        draw.text((1050, y), "POINTS", fill=colors["text"], font=font_md)
        draw.line([(100, y+25), (w - 100, y+25)], fill=(200, 200, 200), width=1)
        y += 40
        
        term_credits, term_points = 0, 0
        for code, title, cred, grade, pt_val in courses:
            pts = cred * pt_val
            term_credits += cred
            term_points += pts
            
            draw.text((120, y), code, fill=colors["text"], font=font_sm)
            draw.text((350, y), title, fill=colors["text"], font=font_sm)
            draw.text((850, y), f"{cred}.00", fill=colors["text"], font=font_sm)
            draw.text((950, y), grade, fill=colors["text"], font=font_sm)
            draw.text((1050, y), f"{pts:.2f}", fill=colors["text"], font=font_sm)
            y += 30
            
        term_gpa = term_points / term_credits if term_credits > 0 else 0
        draw.line([(100, y+5), (w - 100, y+5)], fill=(200, 200, 200), width=1)
        draw.text((120, y + 15), f"Term GPA: {term_gpa:.2f}   |   Term Credits: {term_credits}.00", fill=colors["primary"], font=font_md)
        return y + 60

    # 伪造两个学期的课程数据
    courses_f24 = [
        ("ENG 101", "College Composition", 3, "A", 4.0),
        ("MAT 201", "Calculus I", 4, "B+", 3.3),
        ("HIS 105", "World History", 3, "A-", 3.7),
        ("CSC 110", "Intro to Programming", 4, "A", 4.0)
    ]
    courses_s25 = [
        ("CSC 120", "Data Structures", 4, "A", 4.0),
        ("PHY 101", "General Physics I", 4, "B", 3.0),
        ("MAT 202", "Calculus II", 4, "B+", 3.3),
        ("ART 100", "Art Appreciation", 3, "A", 4.0)
    ]
    
    y_offset = draw_semester_block("Fall 2024", courses_f24, y_offset)
    y_offset = draw_semester_block("Spring 2025", courses_s25, y_offset)
    
    # 4. 汇总 GPA 与 底部教务长签名
    draw.rectangle([(100, y_offset), (w - 100, y_offset + 40)], fill=(230, 230, 230))
    draw.text((120, y_offset + 10), f"CUMULATIVE GPA: 3.68", fill=colors["primary"], font=font_lg)
    draw.text((600, y_offset + 12), f"TOTAL CREDITS EARNED: 29.00", fill=colors["text"], font=font_md)
    
    footer_y = h - 200
    draw.line([(w - 400, footer_y), (w - 100, footer_y)], fill=colors["text"], width=2)
    draw.text((w - 250, footer_y + 10), "Signature of Registrar", fill=colors["text"], font=font_sm, anchor="mm")
    
    draw_real_qrcode(img, f"VERIFY:{stu_id}", 100, h - 220, size=120)
    
    img = add_simple_noise(img, intensity=2)
    buf = BytesIO()
    img.save(buf, format="PDF" if export_pdf else "PNG", resolution=150.0)
    return buf.getvalue()

# (注：generate_teacher_badge 篇幅原因暂未放出，您可以先保留上一次代码中的该函数，主要关注学生证和成绩单的变化)
def generate_teacher_badge(first: str, last: str, school: str, department: str = "Science", theme: str = "green", photo_bytes: bytes = None, export_pdf: bool = False, custom_id: str = "", valid_date: str = "") -> bytes:
    # 教师证通常采用横版设计
    w, h = 500, 350
    img = Image.new("RGB", (w, h), (250, 250, 250))
    draw = ImageDraw.Draw(img)
    
    colors = COLOR_SCHEMES.get(theme, COLOR_SCHEMES["green"])
    font_title = get_font(22, True)
    font_text = get_font(16)
    font_small = get_font(12)
    
    # 顶部 Header
    draw.rectangle([(0, 0), (w, 50)], fill=colors["primary"])
    draw.text((w // 2, 25), "FACULTY ID CARD", fill=colors["accent"], font=font_title, anchor="mm")
    draw.text((w // 2, 75), school[:45], fill=colors["primary"], font=font_text, anchor="mm")
    
    # 照片区域
    photo_x, photo_y, photo_w, photo_h = 25, 100, 100, 120
    user_img = process_photo(photo_bytes, photo_w, photo_h)
    if user_img:
        img.paste(user_img, (photo_x, photo_y))
    else:
        draw.rectangle([(photo_x, photo_y), (photo_x + photo_w, photo_y + photo_h)], outline=(200, 200, 200), width=2)
        draw.text((photo_x + photo_w // 2, photo_y + photo_h // 2), "PHOTO", fill=(150, 150, 150), font=font_text, anchor="mm")
    
    # 教师信息区
    teacher_id = custom_id if custom_id else f"T{random.randint(10000, 99999)}"
    valid_str = valid_date if valid_date else f"Active"
    
    info_x, info_y = photo_x + photo_w + 20, 100
    info_lines = [
        f"Name: {first} {last}", 
        f"ID: {teacher_id}", 
        f"Dept: {department or 'Education'}", 
        f"Status: {valid_str}"
    ]
    for line in info_lines:
        draw.text((info_x, info_y), line, fill=colors["text"], font=font_text)
        info_y += 25
        
    # 右下角二维码
    draw_real_qrcode(img, f"FACULTY|{teacher_id}|{last}", w - 85, h - 130, size=65)
    
    # 底部 Footer
    draw.rectangle([(0, h - 35), (w, h)], fill=colors["primary"])
    draw.text((w // 2, h - 17), "Property of School District", fill=colors["accent"], font=font_small, anchor="mm")
    
    img = add_simple_noise(img, intensity=3)
    buf = BytesIO()
    img.save(buf, format="PDF" if export_pdf else "PNG", resolution=100.0)
    return buf.getvalue()
