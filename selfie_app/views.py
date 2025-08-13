from django.shortcuts import render
import base64
from io import BytesIO
from PIL import Image
from rembg import remove
from django.conf import settings
from django.core.files.base import ContentFile
import os
from django.contrib import messages

def index(request):
    # List of available backgrounds
    backgrounds = [
        {'name': 'Background 1', 'file': 'Background_1.jpg'},
        {'name': 'Background 2', 'file': 'Background_2.jpg'},
        {'name': 'Background 3', 'file': 'Background_3.jpg'},
        {'name': 'Background 4', 'file': 'Background_4.jpg'},
    ]

    if request.method == "POST":
        try:
            img_data = request.POST.get("image")
            bg_choice = request.POST.get("background", "Background_1.jpg")  # Default to first bg
            
            if not img_data:
                messages.error(request, "No image was uploaded. Please take a photo first.")
                return render(request, "selfie_app/index.html", {'backgrounds': backgrounds})

            # Decode the base64 image
            format, imgstr = img_data.split(';base64,')
            image_data = ContentFile(base64.b64decode(imgstr), name='selfie.png')

            # Process selfie
            selfie = Image.open(image_data).convert("RGBA")
            selfie = selfie.resize((1280, 720))
            selfie_no_bg = remove(selfie)

            # Load selected background
            bg_path = os.path.join(
                settings.BASE_DIR, 
                "selfie_app", 
                "static", 
                "selfie_app", 
                "background", 
                bg_choice
            )
            
            if not os.path.exists(bg_path):
                messages.error(request, "Background image not found. Using default.")
                bg_path = os.path.join(
                    settings.BASE_DIR, 
                    "selfie_app", 
                    "static", 
                    "selfie_app", 
                    "background", 
                    "Background_1.jpg"
                )

            bg = Image.open(bg_path).convert("RGBA")
            bg = bg.resize((1280, 720))

            # Composite images
            final_img = Image.alpha_composite(bg, selfie_no_bg)
            
            # Prepare response
            buffer = BytesIO()
            final_img.save(buffer, format="PNG")
            final_data = base64.b64encode(buffer.getvalue()).decode()

            return render(request, "selfie_app/result.html", {
                "image_data": final_data
            })

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, "selfie_app/index.html", {'backgrounds': backgrounds})

    return render(request, "selfie_app/index.html", {'backgrounds': backgrounds})