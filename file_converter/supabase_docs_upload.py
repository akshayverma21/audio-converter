# supabase_docs_upload.py
import os
import uuid
from supabase import create_client
from django.conf import settings

BUCKET_NAME = getattr(settings, "SUPABASE_BUCKET_NAME", "converter")  # reuse existing bucket

def get_supabase_client():
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def build_docs_storage_name(original_name: str, target_ext: str) -> str:

    base, _old_ext = os.path.splitext(original_name)
    base = base.strip().replace(" ", "_").replace("/", "_").replace("\\", "_")
    unique_id = uuid.uuid4().hex
    target_ext = target_ext.lstrip(".").lower()
    return f"docs_converter/{base}_{unique_id}.{target_ext}"

def upload_doc_to_supabase(local_path: str, original_name: str, target_ext: str, upsert: bool = False) -> str:
    
    supabase = get_supabase_client()
    storage_path = build_docs_storage_name(original_name, target_ext)

    with open(local_path, "rb") as f:
        result = supabase.storage.from_(BUCKET_NAME).upload(
            path=storage_path,
            file=f,
            file_options={"upsert": upsert}
        )

    # Defensive error check (supabase-py can differ by version)
    if hasattr(result, "error") and result.error:
        raise Exception(f"Upload failed: {result.error['message']}")
    if isinstance(result, dict) and result.get("error"):
        raise Exception(f"Upload failed: {result['error']}")

    public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(storage_path)
    return public_url
