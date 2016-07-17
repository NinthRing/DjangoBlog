import re
from apps.usera.models import CommunityUser, UserProfile


def parse_username(text):
    print(text)
    pattern = re.compile(r'^@(.+?)[:：\s]')
    m = pattern.match(text.strip())

    if m is not None:
        try:
            profile = UserProfile.objects.get(nickname=m.group(1))
            return profile.user
        except UserProfile.DoesNotExist:
            return None
