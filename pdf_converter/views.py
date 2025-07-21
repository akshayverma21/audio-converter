from django.shortcuts import render

# Create your views here.
import os
import uuid
import subprocess
from django.http import HttpResponse,JsonResponse,FileResponse
from PIL import Image
import io
from .models import FileConversion,Article
from django.views.decorators.csrf import csrf_exempt
from .forms import ImageConverter
from audio_youtube.supabase_upload import upload_to_supabase
import io, os, zipfile, tempfile
from django.shortcuts import get_object_or_404
import mimetypes


def image_converter(request):
    image_form = ImageConverter()

    if request.method == 'POST':
        image_form = ImageConverter(request.POST, request.FILES)
        if image_form.is_valid():
            images = request.FILES.getlist('files')
            selected_format = image_form.cleaned_data['format'].lower()

            pillow_format = {
                'jpg': 'JPEG',
                'jpeg': 'JPEG',
                'png': 'PNG',
                'gif': 'GIF',
                'bmp': 'BMP',
                'tiff': 'TIFF',
                'webp': 'WEBP',
                'pdf': 'PDF',
            }.get(selected_format, selected_format.upper())

            if not images:
                return JsonResponse({'error': 'No images uploaded'}, status=400)

            try:
                with tempfile.TemporaryDirectory() as tmpdirname:
                    unique_id = uuid.uuid4().hex
                    output_filename = f"converted_{unique_id}.{selected_format}"
                    output_path = os.path.join(tmpdirname, output_filename)

                    if selected_format == 'pdf':
                        image_list = [Image.open(file).convert("RGB") for file in images]
                        image_list[0].save(
                            output_path,
                            format='PDF',
                            save_all=True,
                            append_images=image_list[1:]
                        )

                    elif selected_format == 'gif' and len(images) > 1:
                        gif_frames = [Image.open(file).convert("RGB") for file in images]
                        gif_frames[0].save(
                            output_path,
                            format='GIF',
                            save_all=True,
                            append_images=gif_frames[1:],
                            duration=300,
                            loop=0
                        )

                    elif len(images) == 1:
                        img = Image.open(images[0]).convert("RGB")
                        img.save(output_path, format=pillow_format)

                    else:
                        # Multiple images but not PDF/GIF → zip them
                        zip_filename = f"converted_{unique_id}.zip"
                        zip_path = os.path.join(tmpdirname, zip_filename)
                        with zipfile.ZipFile(zip_path, 'w') as zipf:
                            for idx, file in enumerate(images):
                                img = Image.open(file).convert("RGB")
                                img_io = io.BytesIO()
                                img.save(img_io, format=pillow_format)
                                img_io.seek(0)
                                zipf.writestr(f'image_{idx+1}.{selected_format}', img_io.read())
                        output_path = zip_path
                        output_filename = zip_filename

                    # Upload to Supabase
                    download_url = upload_to_supabase(output_path, f"image_converter/{output_filename}")

                    FileConversion.objects.create(
                        user=request.user if request.user.is_authenticated else None,
                        input_format='image',
                        output_format=selected_format,
                        status='completed',
                    )

                    return JsonResponse({
                        'success': True,
                        'download_url': download_url,
                        'filename': output_filename,
                        'content_type': mimetypes.guess_type(output_filename)[0] or 'application/octet-stream'
                        
                    })

            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)

        return JsonResponse({'error': image_form.errors.as_json()}, status=400)

    return render(request, 'pdf_converter/image_to_pdf.html', {'image_form': image_form})






def article_view(request,slug):
    article= get_object_or_404(Article,slug=slug)
    return render(request,'pdf_converter/article.html',{'article':article})



































