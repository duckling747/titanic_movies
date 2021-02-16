from flask import url_for


def construct_page_links(page_name, collection, **kwargs):
    next_page = url_for(page_name, page=collection.next_num, **kwargs)\
    if collection.has_next else None

    prev_page = url_for(page_name, page=collection.prev_num, **kwargs)\
    if collection.has_prev else None

    first_page = url_for(page_name, page=1, **kwargs)\
    if collection.pages > 1 and collection.page != 1 else None

    last_page = url_for(page_name, page=collection.pages, **kwargs)\
    if collection.pages > 1 and collection.page < collection.pages else None

    return (next_page, prev_page, first_page, last_page)
