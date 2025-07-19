from supabase import create_client
from django.conf import settings

def get_supabase_client():
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def upload_to_supabase(local_path, file_name):
    supabase = get_supabase_client()

    with open(local_path, 'rb') as f:
        result = supabase.storage.from_(settings.SUPABASE_BUCKET_NAME).upload(
            path=file_name,
            file=f,
        )

    if hasattr(result, "error") and result.error:
        raise Exception(f"Upload failed: {result.error['message']}")
    public_url = supabase.storage.from_(settings.SUPABASE_BUCKET_NAME).get_public_url(file_name)
    return public_url