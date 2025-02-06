from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

from .models import *
# ApiUser = get_user_model()

class LoginSerializer(serializers.Serializer):
    tk_name = serializers.CharField()
    pass_openid = serializers.CharField(trim_whitespace=False)

    def validate(self, attrs):
        username = attrs.get('tk_name')
        openid = attrs.get('pass_openid')
        if username and openid:
            # user = authenticate(request=self.context.get('request'),
            #                     username=username, password=password)
            user = ApiUser.objects.get(username=username, openid=openid)
            if not user:
                # @TODO
                # 跳转授权注册用户信息
                msg="authorization failed!"
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = "authorization failed!！"
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs

from django.core.exceptions import ValidationError

def validate_image_size(value):
    if value.size < 1024*1024:
        raise ValidationError('Image size is too small')
    if value.size > 10*1024*1024:
        raise ValidationError('Image size is too large')

class Img2ImgrSerializer(serializers.Serializer):
    img = serializers.ImageField(max_length=None, allow_empty_file=False, use_url=True, validators=[validate_image_size])
    model_name = serializers.EmailField()


class UserSerializer(serializers.ModelSerializer):
    # roles = RoleSerializer(many=True, read_only=True)
    # roles = serializers.SerializerMethodField()

    class Meta:
        model = ApiUser
        # exclude = ['password']
        # fields = '__all__'
        fields = ['username', 'telephone','email','nickname','headimgurl', 'sex', 'age', 'city', 'province', 'country', 'sign', 'last_login', 'popup_flag']

    # def get_roles(self, obj):
    #     return [r.name for r in obj.role.all()]