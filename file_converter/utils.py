# utils.py
import os
import uuid
import tempfile
import subprocess


SOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe" #LOCAL
# SOFFICE_PATH = "libreoffice" #PRODUCTION

def run_libreoffice_convert(uploaded_file, target_ext: str):
    
    target_ext = target_ext.lower().lstrip('.')

    tmp_dir = tempfile.gettempdir()

  
    unique_id = uuid.uuid4().hex
    safe_name = uploaded_file.name.replace(' ', '_')
    input_filename = f"{unique_id}_{safe_name}"
    input_path = os.path.join(tmp_dir, input_filename)

  
    with open(input_path, 'wb+') as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)

   
    result = subprocess.run(
        [
            SOFFICE_PATH,
            '--headless',
            '--convert-to', target_ext,
            '--outdir', tmp_dir,
            input_path
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"LibreOffice failed: {result.stderr or result.stdout}")

   
    converted_path = None
    uuid_base = os.path.splitext(input_filename)[0]  # with uuid
    for fname in os.listdir(tmp_dir):
        if fname.lower().endswith(f".{target_ext}"):
            if uuid_base in fname:     # ideal match
                converted_path = os.path.join(tmp_dir, fname)
                break

   
    if converted_path is None:
        candidates = [
            os.path.join(tmp_dir, f) for f in os.listdir(tmp_dir)
            if f.lower().endswith(f".{target_ext}")
        ]
        if candidates:
            converted_path = max(candidates, key=os.path.getmtime)

    if not converted_path or not os.path.exists(converted_path):
        raise RuntimeError("Converted file not found.")

    return converted_path