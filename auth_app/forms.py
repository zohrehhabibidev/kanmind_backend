from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm

from .models import CustomUser


class CustomUserCreationForm(AdminUserCreationForm):
    class Meta(AdminUserCreationForm.Meta):
        model = CustomUser
        fields = ("email", "fullname")


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = "__all__"
