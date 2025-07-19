import os
from django import forms
from django.core.exceptions import ValidationError


OUTPUT_FORMATS = {
    # Writer family
    'doc':  ['pdf', 'docx', 'txt', 'html'],
    'docx': ['pdf', 'doc',  'txt', 'html'],
    'txt':  ['pdf', 'doc',  'docx', 'html'],
    'html': ['pdf', 'doc',  'docx', 'txt'],

    # Calc family
    'xls':  ['pdf', 'xlsx'],
    'xlsx': ['pdf', 'xls'],

    # Impress family
    'ppt':  ['pdf', 'pptx'],
    'pptx': ['pdf', 'ppt'],

    # PDF import
    'pdf':  ['doc', 'docx', 'txt', 'html'],
}


ALL_FORMATS = sorted({fmt for fmts in OUTPUT_FORMATS.values() for fmt in fmts})

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower().lstrip('.')
    if ext not in OUTPUT_FORMATS:
        raise ValidationError(f'Unsupported file type: .{ext}')

class ConvertDocumentForm(forms.Form):
    file = forms.FileField(label="Choose a file", validators=[validate_file_extension])
  
    format = forms.ChoiceField(choices=[], label="Convert To", required=True)

    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        self.fields['format'].choices = [(fmt, fmt.upper()) for fmt in ALL_FORMATS]

    def set_format_choices(self, input_ext: str):
        allowed = OUTPUT_FORMATS.get(input_ext, ALL_FORMATS)
        self.fields['format'].choices = [(fmt, fmt.upper()) for fmt in allowed]