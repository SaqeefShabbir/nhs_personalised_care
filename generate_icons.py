"""
Generate NHS Personalised Care Icons
Run: python generate_icons.py
"""

import os
import base64
from PIL import Image, ImageDraw, ImageFont

def create_icon(size, color="#005EB8", text="NHS"):
    """Create a simple icon with NHS branding"""
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    margin = size // 8
    draw.ellipse([margin, margin, size - margin, size - margin], fill=color)
    
    cross_width = size // 6
    cross_height = size // 2.5
    bar_width = size // 2.5
    bar_height = size // 6
    
    x1 = (size - cross_width) // 2
    y1 = (size - cross_height) // 2
    x2 = x1 + cross_width
    y2 = y1 + cross_height
    draw.rectangle([x1, y1, x2, y2], fill='white')
    
    x1 = (size - bar_width) // 2
    y1 = (size - bar_height) // 2
    x2 = x1 + bar_width
    y2 = y1 + bar_height
    draw.rectangle([x1, y1, x2, y2], fill='white')
    
    try:
        font_size = size // 4
        font = ImageFont.truetype("arial.ttf", font_size)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size - text_width) // 2
        y = (size - text_height) // 2 + size // 3
        draw.text((x, y), text, fill='white', font=font)
    except:
        pass
    
    return img

def create_simple_icon(size, color="#005EB8"):
    """Create a simple colored icon with border"""
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    radius = size // 8
    draw.rounded_rectangle([0, 0, size, size], radius=radius, fill=color)
    
    cross_size = size // 3
    bar_size = size // 8
    
    x1 = (size - bar_size) // 2
    y1 = (size - cross_size) // 2
    x2 = x1 + bar_size
    y2 = y1 + cross_size
    draw.rectangle([x1, y1, x2, y2], fill='white')
    
    x1 = (size - cross_size) // 2
    y1 = (size - bar_size) // 2
    x2 = x1 + cross_size
    y2 = y1 + bar_size
    draw.rectangle([x1, y1, x2, y2], fill='white')
    
    return img

def generate_all_icons():
    """Generate all icon sizes"""
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    os.makedirs('static/icons', exist_ok=True)
    
    for size in sizes:
        img = create_simple_icon(size)
        filename = f'static/icons/icon-{size}.png'
        img.save(filename, 'PNG')
        print(f'✅ Generated {filename}')
    
    favicon = create_simple_icon(64, "#005EB8")
    favicon.save('static/icons/favicon.ico', 'ICO')
    print('✅ Generated favicon.ico')
    
    os.makedirs('static/screenshots', exist_ok=True)
    screenshot = Image.new('RGB', (1080, 1920), color='#F5F7FA')
    draw = ImageDraw.Draw(screenshot)
    
    draw.rectangle([0, 0, 1080, 200], fill='#005EB8')
    draw.text((50, 70), 'NHS Personalised Care', fill='white', size=40)
    
    draw.rounded_rectangle([50, 250, 1030, 400], radius=20, fill='white', outline='#E8ECF0', width=2)
    draw.rounded_rectangle([50, 430, 1030, 580], radius=20, fill='white', outline='#E8ECF0', width=2)
    draw.rounded_rectangle([50, 610, 1030, 760], radius=20, fill='white', outline='#E8ECF0', width=2)
    
    screenshot.save('static/screenshots/dashboard.png')
    print('✅ Generated screenshot')
    
    print('\n✅ All icons generated successfully!')

if __name__ == '__main__':
    try:
        generate_all_icons()
    except ImportError:
        print("❌ Pillow library required. Install: pip install Pillow")
        print("⚠️  Using fallback method...")
        create_fallback_icons()

def create_fallback_icons():
    """Create minimal PNG icons using base64 encoding"""
    png_data = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==')
    
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    os.makedirs('static/icons', exist_ok=True)
    
    for size in sizes:
        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (size, size), color='#005EB8')
            draw = ImageDraw.Draw(img)
            
            cross = size // 4
            bar = size // 8
            draw.rectangle([(size-cross)//2, (size-bar)//2, (size+cross)//2, (size+bar)//2], fill='white')
            draw.rectangle([(size-bar)//2, (size-cross)//2, (size+bar)//2, (size+cross)//2], fill='white')
            
            img.save(f'static/icons/icon-{size}.png')
            print(f'✅ Generated icon-{size}.png')
        except:
            with open(f'static/icons/icon-{size}.png', 'wb') as f:
                f.write(png_data)
            print(f'⚠️  Created placeholder icon-{size}.png')
    
    print('\n✅ Icons created!')