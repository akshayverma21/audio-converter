from django import forms
from django.core.exceptions import ValidationError
import os
from django import forms
from .models import Article






IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp','pdf']
OUTPUT_FORMATS = [
    ('jpg', 'JPEG'),
    ('jpeg', 'JPEG'),
    ('png', 'PNG'),
    ('gif', 'GIF'),
    ('bmp', 'BMP'),
    ('tiff', 'TIFF'),
    ('webp', 'WEBP'),
    ('pdf', 'PDF'),
]

# def validate_image_file(value):
#     files = value if isinstance(value, (list, tuple)) else [value]
#     for file in files:
#         # Use file.name if available (for InMemoryUploadedFile), or skip if already cleaned
#         if hasattr(file, 'name'):
#             ext = os.path.splitext(file.name)[1].lower()
#             if ext not in IMAGE_EXTENSIONS:
#                 raise ValidationError(f'Unsupported image file type: {ext}')


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result

class ImageConverter(forms.Form):
    files = MultipleFileField(
        label='Upload your Images',
        required=False,
        # validators=[validate_image_file],
    )
    format = forms.ChoiceField(
        choices=OUTPUT_FORMATS,
        label="Image Format",
        required=True,
        # help_text="Select the format of the images you are uploading"
    )
    def clean_files(self):
        files = self.cleaned_data.get('files')
        max_size = 100 * 1024 * 1024  # 100 MB
        files = files if isinstance(files, (list, tuple)) else [files]
        for file in files:
            if file.size > max_size:
                raise ValidationError("File too large. Max size is 100 MB.")
            if hasattr(file, 'name'):
                ext = os.path.splitext(file.name)[1].lower()
                if ext not in IMAGE_EXTENSIONS:
                    raise ValidationError(f'Unsupported input image type: {ext}')
        return files
    



class ArticleAdminForm(forms.ModelForm):
    upload_image = forms.ImageField(required=False, help_text="Upload an image for the article")

    class Meta:
        model = Article
        fields = ['title', 'content', 'upload_image']