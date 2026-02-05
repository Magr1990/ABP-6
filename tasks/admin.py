from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Project, Task

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'start_date', 'end_date', 'status', 'created_at')
    list_filter = ('status', 'created_by', 'start_date')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'created_by')
        }),
        ('Fechas y Estado', {
            'fields': ('start_date', 'end_date', 'status')
        }),
        ('Registro', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assigned_to', 'priority', 'status', 'due_date', 'created_at')
    list_filter = ('status', 'priority', 'assigned_to', 'project')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'description', 'project', 'created_by')
        }),
        ('Asignación', {
            'fields': ('assigned_to', 'priority', 'status')
        }),
        ('Fechas', {
            'fields': ('due_date', 'completed_at')
        }),
        ('Registro', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'groups')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(id=request.user.id)
        return qs

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Task, TaskAdmin)

admin.site.site_header = "Administración de Gestor de Tareas"
admin.site.site_title = "Gestor de Tareas Admin"
admin.site.index_title = "Bienvenido al Panel de Administración"