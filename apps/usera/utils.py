def default_nickname(user):
    salt = 10010
    number = salt + user.pk
    nickname = "用户 %s" % number
    return nickname
