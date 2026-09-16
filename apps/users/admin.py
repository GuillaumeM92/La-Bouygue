from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import AdminLoginForm
from .models import MyUser
from .models import Profile

# The admin login shares the site's lock after repeated failures.
admin.site.login_form = AdminLoginForm


class MyUserAdmin(UserAdmin):
    model = MyUser
    list_display = (
        "email",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "email",
        "is_staff",
        "is_active",
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(Profile)
admin.site.register(MyUser)
