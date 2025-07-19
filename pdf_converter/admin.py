import os
import tempfile
from django.contrib import admin
from .models import Article
from .forms import ArticleAdminForm
from .supabase_article_upload import upload_article_image
from pdf_converter.models import FileConversion  # if needed where you registered earlier

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    list_display = ('title', 'created_at', 'slug')
    search_fields = ('title',)

    def save_model(self, request, obj, form, change):
        image_file = request.FILES.get('upload_image')
        if image_file:
            tmp_dir = tempfile.gettempdir()
            temp_path = os.path.join(tmp_dir, image_file.name)

            # Save uploaded image to temp
            with open(temp_path, 'wb+') as f:
                for chunk in image_file.chunks():
                    f.write(chunk)

            try:
                # Upload to Supabase
                image_url = upload_article_image(temp_path, image_file.name)
                obj.article_image = image_url
            finally:
                # Always attempt cleanup
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        super().save_model(request, obj, form, change)

# If you still want to admin-register FileConversion:
admin.site.register(FileConversion)