#!/usr/bin/env python3
"""Generate realistic sample images for all artifacts and exhibitions"""
from PIL import Image, ImageDraw, ImageFont
import os
import random

def create_realistic_artifact_image(filename, artifact_name, category, year):
    """Create a more realistic artifact image based on category"""
    os.makedirs('static/uploads', exist_ok=True)
    filepath = os.path.join('static/uploads', filename)
    
    # Define color schemes based on category
    schemes = {
        'archaeological': {
            'bg': (139, 90, 43),      # Brown
            'accent': (184, 134, 11),  # Goldenrod
            'text': (255, 240, 245),   # Floral white
            'pattern': '▋▌▍▎'
        },
        'historical': {
            'bg': (70, 78, 84),        # Bluish gray
            'accent': (255, 193, 7),   # Amber
            'text': (255, 255, 255),   # White
            'pattern': '◆◇◈'
        },
        'art': {
            'bg': (156, 39, 176),      # Deep purple
            'accent': (233, 30, 99),   # Pink
            'text': (255, 255, 255),   # White
            'pattern': '★✦✧'
        },
        'cultural': {
            'bg': (63, 81, 181),       # Indigo
            'accent': (103, 58, 183),  # Deep purple
            'text': (255, 255, 255),   # White
            'pattern': '◉◎◕'
        }
    }
    
    scheme = schemes.get(category, schemes['archaeological'])
    
    # Create image
    width, height = 600, 400
    img = Image.new('RGB', (width, height), color=scheme['bg'])
    draw = ImageDraw.Draw(img)
    
    # Add decorative border
    border_color = scheme['accent']
    draw.rectangle([(10, 10), (width-10, height-10)], outline=border_color, width=3)
    draw.rectangle([(20, 20), (width-20, height-20)], outline=border_color, width=1)
    
    # Add pattern background
    pattern = scheme['pattern']
    for i in range(5):
        for j in range(5):
            x = 60 + i * 100
            y = 80 + j * 60
            draw.text((x, y), pattern[i % len(pattern)], fill=scheme['accent'], font=None)
    
    # Add main title
    try:
        font_large = ImageFont.truetype("arial.ttf", 28)
        font_small = ImageFont.truetype("arial.ttf", 16)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw artifact name
    name_text = artifact_name[:20]  # Limit text
    bbox = draw.textbbox((0, 0), name_text, font=font_large)
    name_width = bbox[2] - bbox[0]
    name_x = (width - name_width) // 2
    draw.text((name_x, 120), name_text, fill=scheme['text'], font=font_large)
    
    # Draw category
    category_text = f"Category: {category.upper()}"
    bbox = draw.textbbox((0, 0), category_text, font=font_small)
    cat_width = bbox[2] - bbox[0]
    cat_x = (width - cat_width) // 2
    draw.text((cat_x, 165), category_text, fill=scheme['accent'], font=font_small)
    
    # Draw year
    if year:
        year_text = f"Year: {year}"
        bbox = draw.textbbox((0, 0), year_text, font=font_small)
        year_width = bbox[2] - bbox[0]
        year_x = (width - year_width) // 2
        draw.text((year_x, 190), year_text, fill=scheme['text'], font=font_small)
    
    # Add decorative elements
    draw.ellipse([(30, 30), (50, 50)], outline=scheme['accent'], width=2)
    draw.ellipse([(width-50, 30), (width-30, 50)], outline=scheme['accent'], width=2)
    draw.ellipse([(30, height-50), (50, height-30)], outline=scheme['accent'], width=2)
    draw.ellipse([(width-50, height-50), (width-30, height-30)], outline=scheme['accent'], width=2)
    
    # Add museum watermark
    draw.text((20, height-35), "🏛️ Digital Museum", fill=scheme['accent'], font=font_small)
    
    img.save(filepath)
    print(f"  ✓ {filename}")
    return filename

def create_exhibition_image(filename, exhibition_title, status):
    """Create a more realistic exhibition image"""
    os.makedirs('static/uploads', exist_ok=True)
    filepath = os.path.join('static/uploads', filename)
    
    # Status-based colors
    status_colors = {
        'active': {'bg': (46, 125, 50), 'accent': (129, 199, 132)},       # Green
        'upcoming': {'bg': (25, 103, 210), 'accent': (100, 181, 246)},    # Blue
        'past': {'bg': (97, 97, 97), 'accent': (189, 189, 189)}           # Gray
    }
    
    colors = status_colors.get(status, status_colors['upcoming'])
    
    width, height = 600, 400
    img = Image.new('RGB', (width, height), color=colors['bg'])
    draw = ImageDraw.Draw(img)
    
    # Add gradient-like effect with rectangles
    for i in range(0, height, 20):
        alpha = int((i / height) * 30)
        color = tuple(max(0, min(255, c - alpha)) for c in colors['bg'])
        draw.rectangle([(0, i), (width, i+20)], fill=color)
    
    # Add border
    draw.rectangle([(15, 15), (width-15, height-15)], outline=colors['accent'], width=4)
    
    # Add decorative lines
    for i in range(3):
        y = 80 + i * 80
        draw.rectangle([(40, y), (width-40, y+2)], fill=colors['accent'])
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 32)
        font_small = ImageFont.truetype("arial.ttf", 18)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Title
    title_text = exhibition_title[:25]
    bbox = draw.textbbox((0, 0), title_text, font=font_large)
    title_width = bbox[2] - bbox[0]
    title_x = (width - title_width) // 2
    draw.text((title_x, 140), title_text, fill=(255, 255, 255), font=font_large)
    
    # Status badge
    status_map = {'active': '🔴 LIVE', 'upcoming': '🔵 COMING', 'past': '⚪ ARCHIVE'}
    status_text = status_map.get(status, 'EXHIBITION')
    bbox = draw.textbbox((0, 0), status_text, font=font_small)
    status_width = bbox[2] - bbox[0]
    status_x = (width - status_width) // 2
    draw.text((status_x, 210), status_text, fill=colors['accent'], font=font_small)
    
    # Museum branding
    draw.text((30, height-40), "🏛️ Թվայնացված Թանգարան 2026", fill=colors['accent'], font=font_small)
    
    img.save(filepath)
    print(f"  ✓ {filename}")
    return filename

def main():
    print("\n" + "="*70)
    print("🎨 GENERATING REALISTIC IMAGES FOR ALL ARTIFACTS & EXHIBITIONS")
    print("="*70)
    
    # Artifact images data
    artifacts_images = [
        ('urartian_shield.jpg', 'Ուրարտական Վահան', 'archaeological', -785),
        ('urartian_shield_1.jpg', 'Urartian Shield Detail', 'archaeological', -785),
        ('urartian_shield_2.jpg', 'Shield Engravings', 'archaeological', -785),
        ('urartian_shield_3.jpg', 'Shield Patterns', 'archaeological', -785),
        
        ('ani_silver_cup.jpg', 'Արծաղե Գավաթ Անիից', 'historical', 1215),
        ('ani_silver_cup_1.jpg', 'Silver Cup Details', 'historical', 1215),
        ('ani_silver_cup_2.jpg', 'Cup Decorations', 'historical', 1215),
        ('ani_silver_cup_3.jpg', 'Silver Work', 'historical', 1215),
        
        ('classical_painting.jpg', 'Հայ Դասական Ներկ', 'art', 1885),
        ('classical_painting_1.jpg', 'Landscape Detail', 'art', 1885),
        ('classical_painting_2.jpg', 'Nature Study', 'art', 1885),
        ('classical_painting_3.jpg', 'Artistic Elements', 'art', 1885),
        
        ('blue_mosque_tile.jpg', 'Կապույտ Մզկիթի Կաշին', 'cultural', 1765),
        ('blue_mosque_tile_1.jpg', 'Tile Pattern 1', 'cultural', 1765),
        ('blue_mosque_tile_2.jpg', 'Tile Pattern 2', 'cultural', 1765),
        ('blue_mosque_tile_3.jpg', 'Tile Details', 'cultural', 1765),
        
        ('ancient_bell.jpg', 'Հնագույն Պղնձե Զանգ', 'archaeological', 1134),
        ('ancient_bell_1.jpg', 'Bell Details', 'archaeological', 1134),
        ('ancient_bell_2.jpg', 'Bell Inscriptions', 'archaeological', 1134),
        ('ancient_bell_3.jpg', 'Bell Structure', 'archaeological', 1134),
    ]
    
    # Exhibition images data
    exhibitions_images = [
        ('urartian_shield.jpg', 'Ուրարտական Ժառանգություն', 'past'),
        ('ani_silver_cup.jpg', 'Հայկական Զարդեր և Դրամ', 'active'),
        ('classical_painting.jpg', 'Հայ Դասական Արվեստ', 'active'),
        ('blue_mosque_tile.jpg', 'Ծեսեր և Ձեռագործություն', 'upcoming'),
        ('ancient_bell.jpg', 'Հնագույն Ձայներ', 'past'),
    ]
    
    print("\n📦 CREATING ARTIFACT IMAGES...")
    print("-" * 70)
    for filename, name, category, year in artifacts_images:
        # Skip if already exists
        if not os.path.exists(os.path.join('static/uploads', filename)):
            create_realistic_artifact_image(filename, name, category, year)
    
    print("\n🎭 CREATING EXHIBITION IMAGES...")
    print("-" * 70)
    for filename, title, status in exhibitions_images:
        # These might already exist, but we'll update them
        create_exhibition_image(filename, title, status)
    
    # Verify
    print("\n" + "="*70)
    print("✅ IMAGE GENERATION COMPLETE")
    print("="*70)
    
    if os.path.exists('static/uploads'):
        file_count = len(os.listdir('static/uploads'))
        print(f"\n✓ Total images: {file_count}")
        print(f"✓ Location: static/uploads/")
    
    print("\n🎨 All artifacts and exhibitions now have unique, realistic images!")

if __name__ == '__main__':
    main()
