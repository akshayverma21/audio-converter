from django.shortcuts import render
from .forms import AudioConverterForm
from django.http import JsonResponse
from django.conf import settings
from .models import AudioConversion
from uuid import uuid4
import os
import threading
import time
import subprocess
import logging
from .supabase_upload import upload_to_supabase

logger = logging.getLogger(__name__)

MAX_UPLOAD_SIZE_MB = 268
allowed = settings.ALLOWED_EXTENSIONS

def home(request):
    return render(request, 'home.html')



def converter(request):
    if request.method == 'POST':
        form = AudioConverterForm(request.POST, request.FILES)
        if form.is_valid():
            audio = request.FILES['audio_file']

            if audio.size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
                return JsonResponse({
                    'success': False,
                    'error': f'File too large. Max allowed size is {settings.MAX_UPLOAD_SIZE_MB} MB.'
                }, status=400)

            target_format = form.cleaned_data['format']
            _, input_ext = os.path.splitext(audio.name)
            input_ext = input_ext.lower()

            if input_ext not in settings.ALLOWED_EXTENSIONS:
                return JsonResponse({
                    'success': False,
                    'error': f'Unsupported file extension: {input_ext}'
                }, status=400)

            input_name = f"{uuid4()}{input_ext}"
            input_path = os.path.join(settings.MEDIA_ROOT, 'uploads', input_name)
            os.makedirs(os.path.dirname(input_path), exist_ok=True)

            with open(input_path, 'wb+') as f:
                for chunk in audio.chunks():
                    f.write(chunk)

            # Save DB record
            conversion = AudioConversion.objects.create(
                user=request.user if request.user.is_authenticated else None,
                original_file=f'uploads/{input_name}',
                input_format=input_ext.strip('.'),
                output_format=target_format,
                status='processing'
            )

            input_full_path = conversion.original_file.path
            output_name = f"{uuid4()}.{target_format}"
            output_path = os.path.join(settings.STATIC_MEDIA_ROOT, 'converted', output_name)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Cleanup task
            threading.Thread(target=delete_files, args=([input_full_path, output_path], 30)).start()

            try:
                success, error = convert_audio_ffmpeg(input_path, output_path, target_format)
                if not success:
                    conversion.error_message = error
                    conversion.save()
                    logger.error(f"FFmpeg failed: {error}{audio.name}{input_ext}")
                    raise Exception("Conversion failed: File may be corrupted or unsupported.")

                # Upload to Supabase
                download_url = upload_to_supabase(output_path, f"converted/{output_name}")

                conversion.converted_file = f'converted/{output_name}'
                conversion.status = 'completed'
                conversion.save()

                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('json') == 'true':
                    return JsonResponse({
                        "success": True,
                        "download_url": download_url,
                        "conversion_id": conversion.id,
                        "format": target_format
                    })

                return render(request, 'convert.html', {
                    'form': AudioConverterForm(),
                    'download_url': download_url,
                })

            except Exception as e:
                conversion.status = 'failed'
                conversion.error_message = str(e)
                conversion.save()
                logger.error(f"DEBUG: Entered converter view{str(e)}.{request.method}-files-{request.FILES}-post-{request.POST}-content_type-{request.content_type}")

                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('json') == 'true':
                    return JsonResponse({
                        "success": False,
                        "error": str(e),
                        "conversion_id": conversion.id,
                    }, status=400)

                return render(request, 'convert.html', {
                    'form': form,
                    'error': f"Conversion failed: {str(e)}"
                })

    else:
        form = AudioConverterForm()

    return render(request, 'convert.html', {'form': form})


def convert_audio_ffmpeg(input_path, output_path, target_format):
    format_args = {
        "mp3": ["-map", "0:a", "-vn", "-c:a", "libmp3lame"],
        "wav": ["-map", "0:a", "-vn", "-c:a", "pcm_s16le"],
        "flac": ["-map", "0:a", "-vn", "-c:a", "flac"],
        "ogg": ["-map", "0:a", "-vn", "-c:a", "libvorbis"],
        "opus": ["-map", "0:a", "-vn", "-c:a", "libopus"],
        "m4a": ["-map", "0:a", "-vn", "-c:a", "aac", "-f", "ipod"],
        "wma": ["-map", "0:a", "-vn", "-c:a", "wmav2"],
        "amr": ["-map", "0:a", "-vn", "-ar", "8000", "-ac", "1", "-c:a", "libopencore_amrnb"],
        "aac": ["-map", "0:a", "-vn", "-c:a", "aac", "-f", "adts"]
    }

    args = format_args.get(target_format, ["-map", "0:a", "-vn", "-c:a", "copy"])

    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", input_path, *args, output_path],
            check=True,
            capture_output=True,
            text=True
        )
        return True, None
    except subprocess.CalledProcessError as e:
        return False, e.stderr


def delete_files(file_paths, delay_minutes=30):
    try:
        time.sleep(delay_minutes * 60)
        for path in file_paths:
            if os.path.exists(path):
                os.remove(path)
    except Exception:
        pass


def custom_404_view(request, exception):
    return render(request, '404.html', status=404)


