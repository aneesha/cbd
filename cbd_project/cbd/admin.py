from django.contrib import admin

from cbd.models import UserProfile, ProcessedSocialMediaMessage, MLCache, IncorrectClassification
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

admin.site.register(UserProfile)
admin.site.register(ProcessedSocialMediaMessage)
admin.site.register(IncorrectClassification)
admin.site.register(MLCache)
