from django.contrib import admin
from .models import ContextManager, ContextLookup, ContextPosition, Roles, Group, JobTitle

# Register your models here.
admin.site.register(ContextManager)

class ContextLookupAdmin(admin.ModelAdmin):
    model=ContextLookup
    readonly_fields=['symbol', 'cvalue']
admin.site.register(ContextLookup, ContextLookupAdmin)

admin.site.register(ContextPosition)

class RolesAdmin(admin.ModelAdmin):
    model=Roles
    fields=['role_name', 'time_created', 'time_updated']
    readonly_fields=['time_created', 'time_updated']
admin.site.register(Roles, RolesAdmin)

class GroupAdmin(admin.ModelAdmin):
    model=Group
    readonly_fields=['time_created', 'time_updated']
admin.site.register(Group, GroupAdmin)

class JobTitleAdmin(admin.ModelAdmin):
    model=JobTitle
    readonly_fields=['time_created', 'time_updated']
admin.site.register(JobTitle, JobTitleAdmin)
