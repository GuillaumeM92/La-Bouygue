from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm
from .forms import AdminLoginForm
from .models import MyUser
from .models import Profile

# The admin login shares the site's lock after repeated failures.
admin.site.login_form = AdminLoginForm


class MyUserCreationForm(AdminUserCreationForm):
    class Meta:
        model = MyUser
        fields = ("email",)


class MyUserChangeForm(UserChangeForm):
    """The password shows as a summary with a link to reset it, never as a field."""

    class Meta:
        model = MyUser
        fields = ("email",)


@admin.register(MyUser)
class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = ("email", "surname", "name", "is_active", "is_staff", "date_joined")
    list_filter = ("is_active", "is_staff", "is_superuser")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Identité", {"fields": ("surname", "name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "surname", "name", "usable_password", "password1", "password2",
                           "is_active", "is_staff"),
            },
        ),
    )
    readonly_fields = ("last_login", "date_joined")
    search_fields = ("email", "surname", "name")
    ordering = ("email",)


admin.site.register(Profile)
