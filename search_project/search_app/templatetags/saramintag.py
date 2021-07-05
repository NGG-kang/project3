from django import template
from bs4 import BeautifulSoup
from django.utils.safestring import mark_safe

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


