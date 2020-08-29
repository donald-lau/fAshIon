import json

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
# def image_search(request):
#     body_unicode = request.body.decode('utf-8')
#     body = json.loads(body_unicode)
#     search = body['search'] 
#     paths = get_images(search, limit=30, print_urls=False, no_download=True)
#     return JsonResponse(paths)


@csrf_exempt
def get_default_graphs(request):
    try:
        with open("../artefacts/graph/item.png", "rb") as f:
            response = HttpResponse(f.read(), content_type="image/jpeg")
            print(response)
            return response
    except IOError:
        response = HttpResponse(content_type="image/jpeg")
        return response
