from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from .utils import default_nickname, default_mugshot


class CommunityUser(AbstractUser):
    """
    AbstractUser 已含有 username、password、first_name、last_name、email、is_staff、is_active、date_joined、last_login 属性
    """
    sign_up_ip = models.GenericIPAddressField('注册时IP', null=True)
    last_login_ip = models.GenericIPAddressField('最后一次登录IP', null=True)

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    GENDER_CHOICES = (
        ('M', '帅哥'),
        ('F', '美女'),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile')
    nickname = models.CharField('昵称', max_length=50, blank=True)
    mugshot = models.ImageField('头像', upload_to='static/mugshots/', blank=True)  # 不要给CharField相关的属性设置null=True
    gender = models.CharField('性别', max_length=1, choices=GENDER_CHOICES, blank=True)
    birthday = models.DateField('生日', blank=True, null=True)
    self_intro = models.TextField('个人简介', blank=True)
    website = models.URLField('个人网站', max_length=200, blank=True)
    github = models.URLField('GitHub主页地址', max_length=200, blank=True)
    sector = models.CharField('所在公司或学校', max_length=200, blank=True)
    occupation = models.CharField('职业', max_length=50, blank=True)

    # concerned_users = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name='关注的人',
    #                                          related_name='concerned_users')
    # followers = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name='粉丝', related_name='followers')

    def __str__(self):
        return '{} : {}'.format(self.user, self.nickname)


# 用户注册后为其创建一个 profile，提供默认的头像和昵称
# 1.为 User 的 Model 设置一个 post_save signal，用户模型被保存后调用回调函数，创建该用户关联的
# profile，为其设置默认昵称和头像

def create_profile(sender, **kwargs):
    # 目前无论用户是否激活都先为其创建 profile，也许更好的在用户激活后再创建
    user_instance = kwargs.pop('instance')
    created = kwargs.pop('created')

    if created:
        # 生成默认昵称
        nickname = default_nickname(user_instance)
        mugshot = default_mugshot(user_instance)
        # 生成默认头像
        UserProfile.objects.create(user=user_instance, nickname=nickname, mugshot=mugshot)


# 必须指定发送者，否则任何一个model save时都会调用该方法
post_save.connect(create_profile, dispatch_uid='usera.models.profile', sender=CommunityUser)
