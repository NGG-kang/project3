import json
from django import template
from bs4 import BeautifulSoup
from django.utils.safestring import mark_safe
from datetime import datetime, timedelta
import ast

register = template.Library()


# next page용 덧셈
@register.filter
def plus(value, arg):
    if not value or not arg:
        return 1
    return int(value) + int(arg)

# previous page용 뺄셈
@register.filter
def minus(value, arg):
    if not value or not arg:
        return 1
    return int(value) - int(arg)

# template에 for range가 없어서 직접 range로 만들어줘야함
# 그래서 없거나 0, 1이면 1부터 2미만까지 하도록 만듦
# 아니면 1부터 n+1까지 반복하도록
@register.filter
def pages(page):
    if not page or int(page) == 0 or int(page) == 1:
        return range(1, 2)
    return range(1, int(page)+1)

# 검색 갯수가 있으면 count 반환, 없으면 0
@register.filter
def is_count(count):
    if count:
        return count
    return 0

# 마지막 페이지인지 확인, True시 next 버튼 비활성화
@register.filter
def is_last_page(page, page_cal):
    page = int(page)
    page_cal = int(page_cal)
    if page == page_cal or page == 0 or page == 1:
        return True
    return False

# 검색결과 카운터
@register.filter
def counter(counter, page):
    return ((int(page)-1) * 25) + int(counter)


# 마크 세이프 필터
@register.filter
def safe_mark(context):
    from django.utils.html import format_html
    return format_html(mark_safe(context))

# 만들어진지 7일 이후의 날이 언제인지
@register.filter
def next_seven_days(created_at):
    return created_at+timedelta(days=7)

# 잡담 전용 mark safe필터
# 잡담이 string 형태로 와서 string -> dict -> mark_safe 방식으로 데이터 뿌려줌
@register.filter(is_safe=True)
def jobdam_to_dict(jobdam):
    jobdam = ast.literal_eval(jobdam)
    href = jobdam['href']
    title = jobdam['title']
    date = jobdam['date']
    text = '<td style="cursor:pointer;" onclick="window.open(\''+href+'\')">'+title+'</td>' \
           '<td style="cursor:pointer;" onclick="window.open(\''+href+'\')">'+date+'</td>'
    return mark_safe(text)


@register.filter
def minus_one(value):
    return int(value)-1

# photo 개수를 range로 바꿔주는것, 이건 어디나 써도 될듯
@register.filter
def photo_range(photos):
    count = len(photos)
    return range(count)

@register.filter
def is_same_int(x, y):
    if int(x)==int(y):
        return True
    return False


@register.filter
def timestamp_to_date(value):
    try:
        ts = float(value)
    except:
        return None
    return datetime.fromtimestamp(ts)

@register.filter
def unpack_kwargs(value):
    value = ast.literal_eval(value)
    company_name = value['company_name']
    href = value['url']
    text = '<td style="cursor:pointer;" onclick="window.open(\''+href+'\')">'+company_name+'</td>' \
           '<td style="cursor:pointer;" onclick="window.open(\'' + \
        href+'\')">'+href+'</td>'
    return mark_safe(text)

