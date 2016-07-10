import re
from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CommunityUser
from django.utils import timezone


class SignInForm(AuthenticationForm):
    error_messages = {
        'invalid_login': '用户名或密码错误',
        'inactive': '该账户已被冻结',
    }

    def __init__(self, *args, **kwargs):
        super(SignInForm, self).__init__(*args, **kwargs)
        self.request = kwargs.pop('request', 'None')

    def save(self, request, user):
        user.last_login = timezone.now()
        user.last_login_ip = request.META.get("REMOTE_ADDR", None)
        user.save(update_fields=['last_login', 'last_login_ip'])


class SignUpForm(UserCreationForm):
    error_messages = {
        'password_mismatch': "两次输入的密码不匹配",
    }

    class Meta:
        model = CommunityUser
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = '用户名长度6位到18位，只能包含字母数字和下划线'
        self.fields['password1'].help_text = '密码长度6位到32位'
        self.fields['password2'].help_text = '请再次输入密码'

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match('^\w+$', username):
            raise forms.ValidationError('用户名只能包含字母、数字或下划线')
        # 匹配数字字母下划线
        if len(username) < 6 or len(username) > 18:
            raise forms.ValidationError('用户名长度只能为6到18位')

        try:
            CommunityUser.objects.get(username=username)
            raise forms.ValidationError('该用户名已被注册')
        except CommunityUser.DoesNotExist:
            if username in settings.RESERVED:
                raise forms.ValidationError('用户名被保留不可用')
            return username

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            CommunityUser.objects.get(email=email)
            raise forms.ValidationError('所填邮箱已经被注册过')
        except CommunityUser.DoesNotExist:
            return email


class ResetPasswordForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        self.user_cache = None
        super(ResetPasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        if username and email:
            try:
                self.user_cache = CommunityUser.objects.get(username=username, email=email)
            except CommunityUser.DoesNotExist:
                raise forms.ValidationError('所填用户名或邮箱错误')
        return self.cleaned_data

    def get_user(self):
        return self.user_cache
