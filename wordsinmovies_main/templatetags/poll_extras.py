from django import template

register=template.Library()

class Paginator():
    def __init__(self, has_other_pages = 0,
    has_previous = 0, previous_page_number = None, page_range = list(),
    number = 0, has_next = 0, next_page_number = 0, total_pages = 0 ):
        self.has_other_pages = has_other_pages
        self.has_previous = has_previous
        self.previous_page_number = previous_page_number
        self.page_range = page_range
        self.number = number
        self.has_next = has_next
        self.next_page_number = next_page_number
        self.total_pages = total_pages

@register.simple_tag
def set_paginator(page, total_pages, has_other_pages, page_range):
    page = int(page)
    total_pages = int(total_pages)
    has_other_pages = has_other_pages
    page_range = int(page_range)
    min_page = ((page-1)//page_range)*page_range+1
    paginator = Paginator(  has_other_pages = has_other_pages,
                            has_previous = (page > page_range),
                            previous_page_number = max(min_page - 1, 1),
                            page_range = range(min_page, min(min_page+page_range, total_pages+1)),
                            number = page,
                            has_next = ((total_pages - min_page)>= page_range),
                            next_page_number = min(min_page + page_range, total_pages),
                            total_pages = total_pages,
                            )
    return paginator
