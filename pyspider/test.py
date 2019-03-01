#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import re

str_page_count = '共411件商品'
page_count = re.match('共(\d{1,})件商品', str_page_count).groups()
if int(page_count[0]) != 0:
    print(123)

print(page_count)