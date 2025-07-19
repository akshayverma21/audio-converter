import os
import logging
from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import ConvertDocumentForm, OUTPUT_FORMATS, ALL_FORMATS
from pdf_converter.models import FileConversion
from .utils import run_libreoffice_convert
import json
from .supabase_docs_upload import upload_doc_to_supabase  # <-- make sure import path correct

logger = logging.getLogger(__name__)


@csrf_exempt
def get_allowed_formats(request):
    
   
    if request.method != "POST":
        return JsonResponse({'formats': ALL_FORMATS})

    
    try:
        data = json.loads(request.body.decode('utf-8') or "{}")
    except Exception:
        data = {}

    ext = str(data.get('ext', '')).lower().lstrip('.')
    allowed = OUTPUT_FORMATS.get(ext, ALL_FORMATS)
    return JsonResponse({'formats': allowed})


@csrf_exempt
def convert_document(request):
    form = ConvertDocumentForm()

    if request.method == "POST":
        form = ConvertDocumentForm(request.POST, request.FILES)
        uploaded_file = request.FILES.get('file')

        if uploaded_file:
            input_ext = os.path.splitext(uploaded_file.name)[1].lower().lstrip('.')
            form.set_format_choices(input_ext)  # limit choices server-side
        else:
            input_ext = None

        if form.is_valid():
            target_ext = form.cleaned_data['format'].lower().lstrip('.')

            # Validate allowed pair
            if input_ext and target_ext not in OUTPUT_FORMATS.get(input_ext, []):
                msg = f'Conversion {input_ext} → {target_ext} not supported.'
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'error': msg}, status=400)
                return render(request, 'file_converter/docx_to_pdf.html', {
                    'file_form': form,
                    'error': msg,
                })

            try:
                # Convert with LibreOffice
                output_path = run_libreoffice_convert(uploaded_file, target_ext)

                # Upload to Supabase (under docs_converter/)
                download_url = upload_doc_to_supabase(
                    local_path=output_path,
                    original_name=uploaded_file.name,
                    target_ext=target_ext,
                )

                # Log record
                FileConversion.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    original_file=uploaded_file,
                    converted_file=None,  # could store remote URL if you add a field
                    input_format=f'.{input_ext}' if input_ext else '',
                    output_format=f'.{target_ext}',
                    status='completed',
                )

                # JSON (AJAX request)
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    # Use user-friendly download filename (original basename + new ext)
                    user_filename = f"{os.path.splitext(uploaded_file.name)[0]}.{target_ext}"
                    return JsonResponse({
                        'success': True,
                        'filename': user_filename,
                        'download_url': download_url,
                    })

                # Non-AJAX fallback: show link
                return render(request, 'file_converter/docx_to_pdf.html', {
                    'file_form': form,
                    'download_url': download_url,
                })

            except Exception as e:
                logger.exception(f"Conversion failed.{e}")
                msg = str(e)
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'error': msg}, status=500)
                return render(request, 'file_converter/docx_to_pdf.html', {
                    'file_form': form,
                    'error': msg,
                })

        # invalid form
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': form.errors}, status=400)

    return render(request, 'file_converter/docx_to_pdf.html', {'file_form': form})