from django.db import models


class PortfolioDocument(models.Model):
    RESUME = 'resume'
    DRAWING = 'drawing'
    DOCUMENT_TYPES = [
        (RESUME, 'Resume'),
        (DRAWING, 'PDF Drawing'),
    ]

    title = models.CharField(max_length=120)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.get_document_type_display()}: {self.title}'


class PortfolioProfile(models.Model):
    email = models.EmailField(blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Portfolio profile'


class PortfolioSkill(models.Model):
    name = models.CharField(max_length=100)
    display_order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class PortfolioExperience(models.Model):
    title = models.CharField(max_length=160)
    meta = models.CharField(max_length=180, blank=True)
    points = models.TextField(help_text='Enter one bullet point per line.')
    display_order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-created_at']

    def point_list(self):
        return [point.strip() for point in self.points.splitlines() if point.strip()]

    def __str__(self):
        return self.title
