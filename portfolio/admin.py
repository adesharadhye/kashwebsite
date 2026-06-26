from django.contrib import admin

from .models import PortfolioDocument, PortfolioExperience, PortfolioProfile, PortfolioSkill


@admin.register(PortfolioDocument)
class PortfolioDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'uploaded_at')
    list_filter = ('document_type',)
    search_fields = ('title',)


@admin.register(PortfolioProfile)
class PortfolioProfileAdmin(admin.ModelAdmin):
    list_display = ('email', 'updated_at')


@admin.register(PortfolioSkill)
class PortfolioSkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_order', 'is_visible', 'created_at')
    list_editable = ('display_order', 'is_visible')
    search_fields = ('name',)


@admin.register(PortfolioExperience)
class PortfolioExperienceAdmin(admin.ModelAdmin):
    list_display = ('title', 'meta', 'display_order', 'is_visible', 'created_at')
    list_editable = ('display_order', 'is_visible')
    search_fields = ('title', 'meta', 'points')
