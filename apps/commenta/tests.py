from django.test import TestCase
import re

# Create your tests here.

if __name__ == '__main__':
    text = "@哇哈哈：范德萨发斯蒂芬"
    pattern = re.compile(r'^@(.+?)[:：\s]')
    m = pattern.match(text.strip())
    print(m, '====')
    print(m.group(1))
