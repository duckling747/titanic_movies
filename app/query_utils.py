from flask import url_for
from app import db
from app.models import Image


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

def store_image_to_db(filename, image_file):
    img = Image(filename=filename, data=image_file.read())
    db.session.add(img)
    db.session.commit()

def retrieve_image_from_db(filename):
    img = Image.query.get(filename)
    if img is not None:
        return img.data
    else:
        return None
