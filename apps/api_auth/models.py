from django.apps.registry import apps
from django.contrib.auth.hashers import make_password
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
from shortuuidfield import ShortUUIDField

# class UserManager(BaseUserManager):
#     def _create_user(self,telephone,username,password,**kwargs):
#         if not telephone:
#             raise ValueError('请传入手机号码！')
#         if not username:
#             raise ValueError('请传入用户名！')
#         if not password:
#             raise ValueError('请传入密码！')
#
#         user = self.model(telephone=telephone,username=username,**kwargs)
#         user.set_password(password)
#         user.save()
#         return user
#
#     def create_user(self,telephone,username,password,**kwargs):
#         kwargs['is_superuser'] = False
#         return self._create_user(telephone,username,password,**kwargs)
#
#     def create_superuser(self,telephone,username,password,**kwargs):
#         kwargs['is_superuser'] = True
#         return self._create_user(telephone,username,password,**kwargs)
#

# class Role(models.Model):
#     name = models.CharField(default='user',
#         verbose_name="角色",
#         max_length=200,
#         choices=[
#             ("guest", "游客"),
#             ("user", "普通用户"),
#             ("vip", "VIP"),
#             ("svip", "SVIP"),
#             ("admin", "管理员"),
#         ])
#
#     def __str__(self):
#         return self.name
#
#
#     class Meta:
#         verbose_name = "角色表"
#         verbose_name_plural = verbose_name


from django.contrib.auth.models import UserManager


class CustomUserManager(UserManager):
    def _create_user(self, username, openid, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        # email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, openid=openid, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username=None, openid=None, password=None, **extra_fields):
        return self._create_user(username=username, openid=openid, password=password,
                                 **extra_fields)

    def create_superuser(self, username=None, openid=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username=username, openid=openid, password=password,
                                 **extra_fields)

class ApiUser(AbstractBaseUser,PermissionsMixin):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    uid = ShortUUIDField(primary_key=True, verbose_name="uid")
    telephone = models.CharField(max_length=11, verbose_name="telephone", null=True, blank=True)
    email = models.EmailField(max_length=100,verbose_name='email', null=True, blank=True)
    username = models.CharField(unique=True, max_length=255,verbose_name="username", null=True, blank=True)
    openid = models.CharField(unique=True,max_length=255,verbose_name="openid")
    nickname = models.CharField(max_length=1000,verbose_name="nickname", null=True, blank=True)
    headimgurl = models.CharField(max_length=2000,verbose_name='headimgurl', null=True, blank=True)
    sex = models.CharField(max_length=10, verbose_name='sex(F M 0)', default="O", choices=GENDER_CHOICES)
    language = models.CharField(max_length=200,verbose_name='language', null=True, blank=True)
    city = models.CharField(max_length=200,verbose_name='city', null=True, blank=True)
    province = models.CharField(max_length=200,verbose_name='province', null=True, blank=True)
    privilege = models.CharField(max_length=2000,verbose_name='privilege', null=True, blank=True)
    unionid = models.CharField(max_length=2000,verbose_name='unionid', null=True, blank=True)
    country = models.CharField(max_length=200,verbose_name='country', null=True, blank=True)
    age = models.IntegerField(verbose_name='age', default=-1)
    sign = models.TextField(verbose_name='sign', default='',  null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True,verbose_name='create_time')
    update_time = models.DateTimeField(auto_now=True, verbose_name='update_time')
    is_active = models.BooleanField(default=True,verbose_name="is_active")
    is_staff = models.BooleanField(default=False,verbose_name="is_staff")
    is_delete = models.BooleanField(default=False, verbose_name="is_delete")
    popup_flag = models.IntegerField(default=0, verbose_name="popup_flag")
    level = models.IntegerField(default=0, verbose_name="level")
    # role = models.ManyToManyField(
    #     'role',
    #     verbose_name="role",
    #     related_name="role",
    # )

    USERNAME_FIELD = 'username'
    # USERNAME_FIELD = 'telephone'
    REQUIRED_FIELDS = ['openid']

    # EMAIL_FIELD = 'email'

    # objects = UserManager()
    objects = CustomUserManager()

    def __str__(self):
        return self.username if self.username else str(self.pk)

    def __repr__(self):
        return self.username if self.username else str(self.pk)

    def get_full_name(self):
        return self.username if self.username else str(self.pk)

    def get_short_name(self):
        return self.username if self.username else str(self.pk)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = verbose_name
        ordering = ('-create_time',)
