from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from fAshIon.Utils import get_ontology_def


@csrf_exempt
def get_onto_vocabs(request):
    onto_def = get_ontology_def()
    colors = [x for x in onto_def["color"]]
    materials = [x for x in onto_def["material"]]
    items = [x for x in onto_def["item"]]
    return JsonResponse({"allColors": colors,
                         "allMaterials": materials,
                         "allItems": items
                         })

