from django import forms
from django.core.exceptions import ValidationError

SUPPORTED_FORMATS = [
    ('mp3', 'MP3'),
    ('wav', 'WAV'),
    ('flac', 'FLAC'),
    ('ogg', 'OGG'),
    ('aac', 'AAC'),
    ('m4a', 'M4A'),
    ('opus', 'Opus'),
    ('amr', 'AMR'),
    ('wma', 'WMA'),
]
class AudioConverterForm(forms.Form):
    audio_file=forms.FileField(label="upload your audio")
    format=forms.ChoiceField(choices=SUPPORTED_FORMATS, label="Convert to")


    def clean_audio_file(self):
        file = self.cleaned_data.get('audio_file')

        max_size = 268 * 1024 * 1024  # 100 MB
        if file.size > max_size:
            raise ValidationError("File too large. Max size is 100 MB.")

        return file