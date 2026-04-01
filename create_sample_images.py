from PIL import Image, ImageDraw, ImageFont
import os

def create_sample_images():
    # Ստեղծել uploads պանակը, եթե չկա
    uploads_dir = os.path.join('static', 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)

    # Նմուշ նկարների տվյալներ
    images_data = [
        {
            "filename": "urartian_shield.jpg",
            "text": "Ուրարտական Վահան",
            "bg_color": (139, 69, 19),  # շագանակագույն
            "size": (800, 600)
        },
        {
            "filename": "ani_silver_cup.jpg",
            "text": "Արծաթե Գավաթ",
            "bg_color": (192, 192, 192),  # արծաթագույն
            "size": (600, 800)
        },
        {
            "filename": "aivazovsky_ararat.jpg",
            "text": "Արարատ Լեռը",
            "bg_color": (135, 206, 235),  # երկնագույն
            "size": (800, 600)
        },
        {
            "filename": "blue_mosque_tile.jpg",
            "text": "Կապույտ Մզկիթի Կաշի",
            "bg_color": (0, 105, 148),  # խոր կապույտ
            "size": (600, 600)
        },
        {
            "filename": "ancient_bell.jpg",
            "text": "Հնագույն Զանգ",
            "bg_color": (176, 141, 87),  # պղնձագույն
            "size": (600, 800)
        }
    ]

    for data in images_data:
        filepath = os.path.join(uploads_dir, data["filename"])
        
        # Ստեղծել նոր նկար միայն եթե այն գոյություն չունի
        if not os.path.exists(filepath):
            # Ստեղծել նոր նկար
            img = Image.new('RGB', data["size"], data["bg_color"])
            draw = ImageDraw.Draw(img)

            # Ավելացնել տեքստ (հայերեն տառատեսակի բացակայության դեպքում կօգտագործի սիստեմային)
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()

            # Տեղադրել տեքստը նկարի կենտրոնում
            text = data["text"]
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (data["size"][0] - text_width) / 2
            y = (data["size"][1] - text_height) / 2
            
            # Ավելացնել ստվեր
            draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0))
            # Ավելացնել հիմնական տեքստը
            draw.text((x, y), text, font=font, fill=(255, 255, 255))

            # Պահպանել նկարը
            img.save(filepath, "JPEG", quality=95)
            print(f"Ստեղծվեց նկար՝ {data['filename']}")
        else:
            print(f"Նկարը արդեն գոյություն ունի՝ {data['filename']}")

if __name__ == '__main__':
    create_sample_images()