from django.contrib import admin
from .models import *
from .middleware import UserVisitMiddleware
from account.models import CV
from django.utils.html import format_html

# Category Admin
admin.site.register(Category)

# Job Admin
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'company_name', 'location', 'job_type_display', 'is_published', 'is_closed', 'timestamp')
    list_filter = ('is_published', 'is_closed', 'job_type', 'category', 'location')
    search_fields = ('title', 'company_name', 'user__email')
    actions = ['publish_jobs', 'close_jobs']

    def job_type_display(self, obj):
        return dict(Job.JOB_TYPE)[obj.job_type]
    job_type_display.short_description = 'Job Type'

    def publish_jobs(self, request, queryset):
        queryset.update(is_published=True)
    publish_jobs.short_description = "Publish selected jobs"

    def close_jobs(self, request, queryset):
        queryset.update(is_closed=True)
    close_jobs.short_description = "Close selected jobs"

admin.site.register(Job, JobAdmin)

# Applicant Admin
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('job', 'user', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('job__title', 'user__email')

admin.site.register(Applicant, ApplicantAdmin)

# BookmarkJob Admin
class BookmarkJobAdmin(admin.ModelAdmin):
    list_display = ('job', 'user', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('job__title', 'user__email')

admin.site.register(BookmarkJob, BookmarkJobAdmin)

# CV Admin
admin.site.register(CV)

# UserVisit Admin
class UserVisitAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'path', 'method', 'timestamp')
    list_filter = ('method', 'timestamp', 'user')
    search_fields = ('user__email', 'path', 'ip_address')
    readonly_fields = ('user', 'ip_address', 'user_agent', 'path', 'method', 'timestamp')

admin.site.register(UserVisit, UserVisitAdmin)



# Contact Admin
class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'subject', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('first_name', 'last_name', 'email', 'subject')
    readonly_fields = ('first_name', 'last_name', 'email', 'subject', 'message', 'timestamp')

admin.site.register(Contact, ContactAdmin)
