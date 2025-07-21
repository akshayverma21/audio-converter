from supabase import create_client
from django.conf import settings
import mimetypes
import logging


logger = logging.getLogger(__name__)


def get_supabase_client():
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def upload_to_supabase(local_path, file_name):
    supabase = get_supabase_client()
    mime_type, _ = mimetypes.guess_type(file_name)
    if not mime_type:
        mime_type = {
            '.pdf': 'application/pdf',
            '.gif': 'image/gif',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff',
            '.webp': 'image/webp',
            '.zip': 'application/zip'
        }.get(os.path.splitext(file_name)[1].lower(), 'application/octet-stream')

    logger.info(f"Uploading {file_name} with MIME type: {mime_type}")
    with open(local_path, 'rb') as f:
        result = supabase.storage.from_(settings.SUPABASE_BUCKET_NAME).upload(
            path=file_name,
            file=f,
            file_options={"content-type": mime_type}
        )

    if hasattr(result, "error") and result.error:
        raise Exception(f"Upload failed: {result.error['message']}")
    public_url = supabase.storage.from_(settings.SUPABASE_BUCKET_NAME).get_public_url(file_name)
    return public_url
















# from supabase import create_client
# from django.conf import settings

# def get_supabase_client():
#     return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


# def upload_to_supabase(local_path, file_name):
#     supabase = get_supabase_client()

#     with open(local_path, 'rb') as f:
#         result = supabase.storage.from_(settings.SUPABASE_BUCKET_NAME).upload(
#             path=file_name,
#             file=f,
#         )

#     if hasattr(result, "error") and result.error:
#         raise Exception(f"Upload failed: {result.error['message']}")
#     public_url = supabase.storage.from_(settings.SUPABASE_BUCKET_NAME).get_public_url(file_name)
#     return public_url
