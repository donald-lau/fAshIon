import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google_images_download import google_images_download

# item instantiation
from fAshIon.Utils import get_ontology_def


def init_google_serach():
    return google_images_download.googleimagesdownload()


def get_images(keywords, limit=5, print_urls=True, no_download=True):
    """
    Get images from google search engine
    :param keywords: searching keywords, multiple keywords separate by comma
    :param limit: number of images per keyword
    :param print_urls: flag to print image urls in console
    :param no_download: flag to download images locally
    :return: list of search keywords and dictionary with keywords and corresponding images url
    """
    arguments = {"keywords": keywords,
                 "limit": limit,
                 "print_urls": print_urls,
                 "no_download": no_download,
                 "safe_search": True,
                 "silent_mode": True
                 }
    paths, error_cnt = init_google_serach().download(arguments)
    return paths


def prediction_get_images(color, material, item):
    if color in ["fuchsia", "rose", "velvet", "pearl", "nude", "beach", "camel", "mint", "coffee",
                 "luna", "tan", "moon", "onyx", "forest", "wine", "pineapple", "autumn", "oliver",
                 "bamboo", "coconut", "lemon", "snow", "almond", "sunset"]:
        color += " color "
    if material in ["skin", "crocodile"]:
        material += " material "
    if item in ["wedge", "slipon", "brogue"]:
        item += " shoe"
    elif item in ["stud", "hoop"]:
        item += " earring"
    elif item in ["chain", "cross"]:
        item += " necklace"
    elif item in ["glove", "cape", "lingerie"]:
        item += " fashionable"
    elif item in ["bra"]:
        item = "sport bra"
    elif item in ["top"]:
        item = "fashion topwear"
    search = color + " " + material + " " + item
    urls = get_images(search, limit=4)
    return urls[search]


@csrf_exempt
def image_search(request):
    onto_def = get_ontology_def()
    body_unicode = request.body.decode("utf-8")
    body = json.loads(body_unicode)
    color, material, item = "", "", ""
    if body["color"] is not None and body["color"] != "":
        color = body["color"]
        if color in ["fuchsia", "rose", "velvet", "pearl", "nude", "beach", "camel", "mint", "coffee",
                     "luna", "tan", "moon", "onyx", "forest", "wine", "pineapple", "autumn", "oliver",
                     "bamboo", "coconut", "lemon", "snow", "almond", "sunset"]:
            color += " color "
    if body["material"] is not None and body["material"] != "":
        material = body["material"]
        if material in ["skin", "crocodile"]:
            material += " material "
    item = body["item"]
    if item in ["wedge", "slipon", "brogue"]:
        item += " shoe"
    elif item in ["stud", "hoop"]:
        item += " earring"
    elif item in ["chain", "cross"]:
        item += " necklace"
    elif item in ["glove", "cape", "lingerie"]:
        item += " fashionable"
    elif item in ["bra"]:
        item = "sport bra"
    elif item in ["top"]:
        item = "fashion topwear"

    search = color + " " + material + " " + item

    paths = get_images(search, limit=15, print_urls=False, no_download=True)
    return JsonResponse(paths)


@csrf_exempt
def test_img(request):
    return JsonResponse({})
