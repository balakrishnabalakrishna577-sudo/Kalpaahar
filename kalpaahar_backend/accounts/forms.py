from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class RegisterForm(forms.Form):
    name             = forms.CharField(max_length=200, label="Full Name")
    email            = forms.EmailField(label="Email Address")
    password         = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    phone            = forms.CharField(max_length=20, required=False, label="Phone (optional)")

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
            validate_password(password)
        return password

    def clean(self):
        cleaned = super().clean()
        pw  = cleaned.get("password")
        cpw = cleaned.get("confirm_password")
        if pw and cpw and pw != cpw:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            email    = data["email"],
            password = data["password"],
            name     = data["name"],
            phone    = data.get("phone", ""),
        )
        return user


class LoginForm(forms.Form):
    email    = forms.EmailField(label="Email Address")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        self._user = None

    def clean(self):
        cleaned = super().clean()
        email   = cleaned.get("email", "").lower().strip()
        password = cleaned.get("password", "")
        if email and password:
            user = authenticate(self.request, username=email, password=password)
            if user is None:
                raise forms.ValidationError("Invalid email or password. Please try again.")
            if not user.is_active:
                raise forms.ValidationError("This account has been disabled.")
            self._user = user
        return cleaned

    def get_user(self):
        return self._user
