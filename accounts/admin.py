from django.contrib import admin

from accounts.models import User

# admin.site.register(User)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'is_staff', 'is_active', 'display_groups')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('id',)

    @admin.display(description="Groups")
    def display_groups(self, obj):
        return ", ".join(group.name for group in obj.groups.all())
