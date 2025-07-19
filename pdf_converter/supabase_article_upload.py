import os
from supabase import create_client
from django.conf import settings
import mimetypes
import os
import uuid

def get_supabase_client():
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def _safe_name(name: str) -> str:
    """Sanitize filename for storage."""
    base, ext = os.path.splitext(name)
    base = base.strip().replace(' ', '_').replace('/', '_').replace('\\', '_')
    ext = ext.lower()
    return base, ext

def upload_article_image(local_path, original_name):
    """
    Upload article image to Supabase bucket under articles/.
    Returns public URL.
    """
    supabase = get_supabase_client()

    base, ext = _safe_name(original_name)
    if not ext:
        # try guess from path
        guessed = mimetypes.guess_extension(mimetypes.guess_type(local_path)[0] or '') or '.bin'
        ext = guessed

    unique_id = uuid.uuid4().hex
    storage_name = f"articles/{base}_{unique_id}{ext}"

    # Infer content type
    ctype, _ = mimetypes.guess_type(original_name)
    if not ctype:
        ctype = "application/octet-stream"

    with open(local_path, "rb") as f:
        result = supabase.storage.from_(settings.SUPABASE_BUCKET_NAME).upload(
            path=storage_name,
            file=f,
            file_options={
                "upsert": "true",          # MUST be string
                "content-type": ctype,     # helps correct serving
                "cache-control": "3600",   # optional
            }
        )

    # Defensive error checks (supabase-py versions differ)
    if hasattr(result, "error") and result.error:
        raise Exception(f"Upload failed: {result.error['message']}")
    if isinstance(result, dict) and result.get("error"):
        raise Exception(f"Upload failed: {result['error']}")

    public_url = supabase.storage.from_(settings.SUPABASE_BUCKET_NAME).get_public_url(storage_name)
    return public_url