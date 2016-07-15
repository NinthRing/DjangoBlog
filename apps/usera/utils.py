import random
from PIL import Image, ImageDraw, ImageFont
import os
from config.settings import BASE_DIR
import uuid


def default_nickname(user):
    salt = 10010
    number = salt + user.pk
    nickname = "用户%s" % number
    return nickname


def default_mugshot(user):
    # 用户注册时为其生成默认头像
    # 已用户名第一个字母大写或数字为图片文字（若不是字母或者数字则随机指定一个大写字母）
    # 底色随机选择，但底色和字体颜色要相互对比
    # 需要指定尺寸
    # 生成后保存到默认目录并且返回文件所在路径
    username = user.username
    first_letter = username[0]

    if first_letter == '_':  # 因为用户名只允许数字、字母和下划线
        first_letter = chr(random.randint(65, 90)).upper()
    first_letter = first_letter.upper()
    # 开始绘制头像
    image = Image.new('RGB', (100, 100), color=(255, 255, 255))  # 这里需要随机颜色生成
    font_file = os.path.join(BASE_DIR, 'static/usera/fonts/Arial.ttf')
    font = ImageFont.truetype(font=font_file, size=90)
    draw = ImageDraw.Draw(image)

    # 使字母居中
    text_x, text_y = font.getsize(first_letter)
    x = (100 - text_x) / 2
    y = (100 - text_y) / 2
    draw.text((x, y), first_letter, font=font, fill=(0, 0, 0))  # 需要生成和 image 对比的颜色
    name = '%s' % uuid.uuid5(uuid.NAMESPACE_DNS, str(user.pk))
    path = 'static/mugshots/%s.jpg' % name
    image.save(os.path.join(BASE_DIR, path))
    return path
