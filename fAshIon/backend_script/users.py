import json
import operator
import pprint
import fAshIon.backend_script.prediction as pred

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from fAshIon.Utils import read_output_file, get_ontology_def, dump_output_file, normalize_list, \
    phrase_user_file
from fAshIon.backend_script.gui import get_images

new_user_id = 0


# @csrf_exempt
# def create_user(request):
#     global new_user_id
#     new_user_id += 1
#     body_unicode = request.body.decode('utf-8')
#     body = json.loads(body_unicode)
#     data = body['data']
#     items = data["item"]
#     colors = data["color"]
#     materials = data["material"]
#     image = data["url"]
#     if len(items) == len(colors) == len(materials) == len(image):
#         outfits = []
#         for i in range(len(items)):
#             outfit = {
#                 "id": i,
#                 "item": items[i],
#                 "color": colors[i],
#                 "material": materials[i],
#                 "image": image[i]
#             }
#             outfits.append(outfit)
#         return JsonResponse({})
#     else:
#         return JsonResponse({"info": "wrong"})

def get_user(user_name, user_id):
    filename = phrase_user_file(user_name, user_id)
    user = None
    try:
        user = read_output_file("user/" + filename, json_format=True)
    except FileNotFoundError:
        user = create_user_helper(user_name, user_id, [])
    return user


def create_user_helper(user_name, user_id, outfits):
    user = {
        "name": user_name,
        "id": user_id,
        "outfit": outfits,
        "pref": [],
        "max_outfit_id": len(outfits),
        "max_pref_id": 0
    }
    filename = str(user_id) + "_" + user_name
    dump_output_file(user, filename, "fAshIon/output/user", json_format=True)
    return user


def add_outfit_helper(user_name, user_id, outfit):
    """
    :param user_name: user name
    :param user_id: user id
    :param outfit: outfit without id, already assigned id will be overwritten
    :return: none
    """
    filename = phrase_user_file(user_name, user_id)
    # user = read_output_file("user/" + filename, json_format=True)
    user = get_user(user_name, user_id)
    current_outfits = user["outfit"]
    outfit["id"] = user["max_outfit_id"]
    user["max_outfit_id"] += 1
    current_outfits.append(outfit)
    user["outfit"] = current_outfits
    # pprint.pprint(user)

    dump_output_file(user, filename, "fAshIon/output/user", json_format=True)


@csrf_exempt
def update_pref(request):
    user_name = pred.current_user
    user_id = pred.current_id
    body_unicode = request.body.decode("utf-8")
    body = json.loads(body_unicode)
    pref = body["data"]
    onto_def = get_ontology_def()
    onto_0 = pref.pop("onto_0")
    onto_0_class = "item" if onto_0 in onto_def["item"] else \
        "color" if onto_0 in onto_def["color"] else \
            "material" if onto_0 in onto_def["material"] else "context"
    if onto_0_class == "context":
        onto_0_id = onto_def[onto_0_class].index(onto_0)
    else:
        onto_0_id = onto_def[onto_0_class][onto_0][0]

    onto_1 = pref.pop("onto_1")
    if onto_1 != "":
        onto_1_class = "item" if onto_1 in onto_def["item"] else \
            "color" if onto_1 in onto_def["color"] else \
            "material" if onto_1 in onto_def["material"] else "context"
        onto_1_id = onto_def[onto_1_class][onto_1][0]
        pref["onto_attr"] = [onto_0_class, onto_1_class]
        pref["onto_id"] = [onto_0_id, onto_1_id]
    else:
        pref["onto_attr"] = [onto_0_class]
        pref["onto_id"] = [onto_0_id]

    add_pref_helper(user_name, user_id, pref, active=True)
    return JsonResponse({})


def add_pref_helper(user_name, user_id, pref, active=False):
    """
    :param active: whether preference type is active
    :param user_name: user name
    :param user_id: user id
    :param pref: preference without id, already assigned id will be overwritten
    :return: none
    """
    filename = phrase_user_file(user_name, user_id)
    # user = read_output_file("user/" + filename, json_format=True)
    user = get_user(user_name, user_id)
    current_prefs = user["pref"]

    oa = pref["onto_attr"]
    oi = pref["onto_id"]
    for cp in current_prefs:
        if oa == cp["onto_attr"] and oi == cp["onto_id"]:
            cp["value"] = pref["value"]
            if active:
                cp["modifier"] = pref["modifier"]
                cp["type"] = 1
            dump_output_file(user, filename, "fAshIon/output/user", json_format=True)
            return

    pref["id"] = user["max_pref_id"]
    user["max_pref_id"] += 1
    current_prefs.append(pref)
    user["pref"] = current_prefs
    # pprint.pprint(user)

    dump_output_file(user, filename, "fAshIon/output/user", json_format=True)


def del_user_attr_helper(user_name, user_id, attr_type, attr_id):
    """
    delete whole outfit or pref
    :param user_name: user name
    :param user_id: user id
    :param attr_type: either "outfit" or "pref"
    :param attr_id: attribute id
    :return: none
    """
    filename = phrase_user_file(user_name, user_id)
    # user = read_output_file("user/" + filename, json_format=True)
    user = get_user(user_name, user_id)
    current_attrs = user[attr_type]
    for attr in current_attrs:
        if attr_id == attr["id"]:
            current_attrs.remove(attr)
    user[attr_type] = current_attrs
    # pprint.pprint(user)
    calculate_passive_pref(user_name, user_id)
    dump_output_file(user, filename, "fAshIon/output/user", json_format=True)


@csrf_exempt
def get_user_outfit(request):
    user_name = pred.current_user
    user_id = pred.current_id
    filename = phrase_user_file(user_name, user_id)
    # user = read_output_file("user/" + filename, json_format=True)
    user = get_user(user_name, user_id)
    return JsonResponse({"outfit": user["outfit"]})


@csrf_exempt
def get_user_pref(request):
    user_name = pred.current_user
    user_id = pred.current_id
    filename = phrase_user_file(user_name, user_id)
    # user = read_output_file("user/" + filename, json_format=True)
    user = get_user(user_name, user_id)
    onto_def = get_ontology_def()
    prefs = user["pref"]
    for pref in prefs:
        pref["type"] = "passive" if pref["type"] == 0 else "active"
        pref["onto_0"] = onto_def[pref["onto_attr"][0] + "_id_lookup"][pref["onto_id"][0]]
        pref["onto_1"] = ""
        if len(pref["onto_attr"]) > 1:
            pref["onto_1"] = onto_def[pref["onto_attr"][1] + "_id_lookup"][pref["onto_id"][1]]
    return JsonResponse({"pref": user["pref"]})


@csrf_exempt
def delete_item_in_outfit(request):
    user_name = pred.current_user
    user_id = pred.current_id
    body_unicode = request.body.decode("utf-8")
    body = json.loads(body_unicode)
    outfit_id = body["outfitId"]
    attr_id = body["data"]
    filename = phrase_user_file(user_name, user_id)
    # user = read_output_file("user/" + filename, json_format=True)
    user = get_user(user_name, user_id)
    for outfit in user["outfit"]:
        if outfit["id"] == outfit_id:
            outfit["item"].pop(attr_id)
            outfit["color"].pop(attr_id)
            outfit["material"].pop(attr_id)
            outfit["image"].pop(attr_id)
            break
    dump_output_file(user, filename, "fAshIon/output/user", json_format=True)
    calculate_passive_pref(user_name, user_id)
    return JsonResponse({})


@csrf_exempt
def add_outfit(request):
    user_name = pred.current_user
    user_id = pred.current_id
    user = get_user(user_name, user_id)
    body_unicode = request.body.decode("utf-8")
    body = json.loads(body_unicode)
    fashion_items = body["data"]
    items, colors, materials, images = [], [], [], []
    for fashion_item in fashion_items:
        items.append(fashion_item["item"])
        colors.append(fashion_item["color"] if fashion_item["color"] is not None else "")
        materials.append(fashion_item["material"] if fashion_item["material"] is not None else "")
        images.append([fashion_item["urls"][fashion_item["url_id"]]])
    outfit = {"item": items, "color": colors, "material": materials, "image": images, "id": user["max_outfit_id"]}
    user["max_outfit_id"] += 1
    current_outfits = user["outfit"]
    current_outfits.append(outfit)
    user["outfit"] = current_outfits
    filename = phrase_user_file(user_name, user_id)
    dump_output_file(user, filename, "fAshIon/output/user", json_format=True)
    calculate_passive_pref(user_name, user_id)
    return JsonResponse({})


@csrf_exempt
def update_outfit(request):
    user_name = pred.current_user
    user_id = pred.current_id
    body_unicode = request.body.decode("utf-8")
    body = json.loads(body_unicode)
    outfit_id = body["outfitId"]
    attr_id = body["data"]
    item = body["item"]
    color = body["color"] if body["color"] is not None else ""
    material = body["material"] if body["material"] is not None else ""
    image = body["image"]
    filename = phrase_user_file(user_name, user_id)
    # user = read_output_file("user/" + filename, json_format=True)
    user = get_user(user_name, user_id)
    for outfit in user["outfit"]:
        if outfit["id"] == outfit_id:
            outfit["item"][attr_id] = item
            outfit["color"][attr_id] = color
            outfit["material"][attr_id] = material
            outfit["image"][attr_id] = [image]
            break
    dump_output_file(user, filename, "fAshIon/output/user", json_format=True)
    calculate_passive_pref(user_name, user_id)
    return JsonResponse({})


@csrf_exempt
def get_user_summary(request):
    user_name = pred.current_user
    user_id = pred.current_id
    user = get_user(user_name, user_id)
    summary = {
        "pref_cnt": len(user["pref"]),
        "outfit_cnt": len(user["outfit"])
    }
    items = {}
    colors = {}
    materials = {}
    for outfit in user["outfit"]:
        for item in outfit["item"]:
            items[item] = 1 if item not in items else items[item] + 1
        for color in outfit["color"]:
            if color != "" and color is not None:
                colors[color] = 1 if color not in colors else colors[color] + 1
        for material in outfit["material"]:
            if material != "" and material is not None:
                materials[material] = 1 if material not in materials else materials[material] + 1
    top_item = max(items.items(), key=operator.itemgetter(1))[0]
    top_color = max(colors.items(), key=operator.itemgetter(1))[0]
    top_material = max(materials.items(), key=operator.itemgetter(1))[0]
    summary["top"] = [top_item, top_color, top_material]
    summary["top_cnt"] = [
        items[top_item] if top_item != "" else 0,
        colors[top_color] if top_color != "" else 0,
        materials[top_material] if top_material != "" else 0
    ]
    print()
    return JsonResponse({"summary": summary})


@csrf_exempt
def new_image_for_outfit(request):
    body_unicode = request.body.decode("utf-8")
    body = json.loads(body_unicode)
    image_search = body["search"]
    urls = get_images(image_search, limit=5, print_urls=False, no_download=True)[image_search]
    return JsonResponse({"urls": urls})


@csrf_exempt
def del_user_pref_outfit(request):
    user_name = pred.current_user
    user_id = pred.current_id
    body_unicode = request.body.decode("utf-8")
    body = json.loads(body_unicode)
    puid = body["data"]
    type = body["type"]
    del_user_attr_helper(user_name, user_id, type, puid)
    return JsonResponse({})


def calculate_passive_pref(user_name, user_id):
    filename = phrase_user_file(user_name, user_id)
    # user = read_output_file("user/" + filename, json_format=True)
    user = get_user(user_name, user_id)
    outfits = user["outfit"]
    outfit_cnt = len(outfits)
    items_ = {}
    materials_ = {}
    colors_ = {}
    context_ = [0, 0, 0]
    onto_def = get_ontology_def()

    prefs = user["pref"]
    for pref in prefs:
        if pref["type"] == 0:
            prefs.remove(pref)

    # get stats for ontology attributes
    for outfit in outfits:
        for item in outfit["item"]:
            items_[item] = items_[item] + 1 if item in items_ else 1
            item_context_modifier = onto_def["context_multiplier"][onto_def["item_topic"][onto_def["item"][item][1]]]
            context_ = [sum([c, i * item_context_modifier]) for (c, i) in zip(context_, onto_def["item"][item][2])]
        for material in outfit["material"]:
            materials_[material] = materials_[material] + 1 if material in materials_ else 1
            if material != "":
                context_ = [sum(x) for x in zip(context_, onto_def["material"][material][1])]
        for color in outfit["color"]:
            colors_[color] = colors_[color] + 1 if color in colors_ else 1
    items_.pop("", None)
    materials_.pop("", None)
    colors_.pop("", None)
    if sum(context_) != 0:
        context_ = normalize_list(context_)

    # item, material preference
    items_ = [(k, min(v / float(outfit_cnt), 0.5))
              for _, (k, v) in enumerate(items_.items()) if v >= 3]
    materials_ = [(k, min(v / float(outfit_cnt), 0.5))
                  for _, (k, v) in enumerate(materials_.items()) if v >= 3]

    # color preference
    colors_ = [(k, v) for _, (k, v) in enumerate(colors_.items()) if v >= 3]
    colors_tmp = {}
    for (color, cnt) in colors_:
        if cnt / float(outfit_cnt) < 0.7:
            root_colors = [onto_def["color_id_lookup"][rc] for rc in onto_def["color"][color][1]]
            for rc in root_colors:
                colors_tmp[rc] = colors_tmp[rc] + cnt if rc in colors_tmp else cnt
        else:
            colors_tmp[color] = cnt
    colors_ = [(k, v) for _, (k, v) in enumerate(colors_tmp.items())]
    colors_ = [(k, min(v / float(outfit_cnt), 0.5)) for (k, v) in colors_]

    # context preference
    for i in range(len(context_)):
        if context_[i] > 0.5:
            pref = {"type": 0,  # 0 for passive and 1 for active
                    "value": 0.35,
                    "modifier": 1,
                    "onto_attr": ["context"],
                    "onto_id": [i]}
            add_pref_helper(user_name, user_id, pref)

    # Adding preference to user profile
    for (prefs, onto_class) in zip([items_, materials_, colors_], ["item", "material", "color"]):
        for (keyword, val) in prefs:
            pref = {"type": 0,  # 0 for passive and 1 for active
                    "value": val,
                    "modifier": 1,
                    "onto_attr": [onto_class],
                    "onto_id": [onto_def[onto_class][keyword][0]]}
            add_pref_helper(user_name, user_id, pref)

    return
    # pprint.pprint(items_)
    # pprint.pprint(materials_)
    # pprint.pprint(colors_)
    # pprint.pprint(context_)


def mock_users():
    n = "adam"
    uid = 1
    o = [{"id": 0,
          "item": ["top", "skirt", "heel"],
          "color": ["white", "moon", "white"],
          "material": ["cotton", "silk", ""],
          "image": [["image1"], ["image2"], ["image3"]]
          },
         {"id": 1,
          "item": ["blouse", "skirt", "heel"],
          "color": ["white", "moon", "white"],
          "material": ["", "silk", ""],
          "image": [["image1"], ["image2"], ["image3"]]
          },
         {"id": 2,
          "item": ["bra", "skirt", "heel"],
          "color": ["white", "moon", "white"],
          "material": ["", "", ""],
          "image": [["image1"], ["image2"], ["image3"]]
          },
         {"id": 3,
          "item": ["tshirt", "skirt", "sandal"],
          "color": ["white", "white", "blue"],
          "material": ["cotton", "silk", "denim"],
          "image": [["image1"], ["image2"], ["image3"]]
          },
         {"id": 4,
          "item": ["tshirt", "skirt", "sandal"],
          "color": ["white", "white", "red"],
          "material": ["cotton", "silk", "denim"],
          "image": [["image1"], ["image2"], ["image3"]]
          },
         ]

    p1 = {
        "id": 0,
        "type": 0,
        "value": 0.25,
        "modifier": 1,
        "onto_attr": ["context"],
        "onto_id": [2]
    }
    p2 = {
        "id": 0,
        "type": 0,
        "value": 0.42,
        "modifier": 1,
        "onto_attr": ["color"],
        "onto_id": [2]
    }
    p3 = {
        "id": 0,
        "type": 1,
        "value": 2.42,
        "modifier": 3,
        "onto_attr": ["item", "item"],
        "onto_id": [2, 201]
    }
    p4 = {
        "id": 0,
        "type": 1,
        "value": 0.6,
        "modifier": 2.5,
        "onto_attr": ["item", "material"],
        "onto_id": [902, 12]
    }
    p5 = {
        "id": 0,
        "type": 1,
        "value": 0.8,
        "modifier": 2.3,
        "onto_attr": ["item", "color"],
        "onto_id": [902, 67]
    }
    create_user_helper(n, uid, o)
    add_pref_helper(n, uid, p1)
    add_pref_helper(n, uid, p2)
    add_pref_helper(n, uid, p3)
    add_pref_helper(n, uid, p4)
    add_pref_helper(n, uid, p5)
    calculate_passive_pref(n, uid)

    n = "john"
    uid = 2
    o = [{"id": 0,
          "item": ["jacket", "jean", "boot"],
          "color": ["navy", "blue", "navy"],
          "material": ["leather", "", "leather"],
          "image": [["image1"], ["image2"], ["image3"]]
          },
         {"id": 1,
          "item": ["polo", "jean", "boot"],
          "color": ["black", "cobalt", "navy"],
          "material": ["", "", "leather"],
          "image": [["image1"], ["image2"], ["image3"]]
          },
         {"id": 2,
          "item": ["tank", "trouser", "boot"],
          "color": ["turquoise", "blue", "turquoise"],
          "material": ["", "", "leather"],
          "image": [["image1"], ["image2"], ["image3"]]
          },
         {"id": 3,
          "item": ["jacket", "trouser", "boot"],
          "color": ["silvertone", "sapphire", "blue"],
          "material": ["cotton", "silk", "leather"],
          "image": [["image1"], ["image2"], ["image3"]]
          },
         {"id": 4,
          "item": ["jacket", "chino", "boot"],
          "color": ["sapphire", "white", "black"],
          "material": ["cotton", "silk", "leather"],
          "image": [["image1"], ["image2"], ["image3"]]
          },
         ]
    create_user_helper(n, uid, o)
    calculate_passive_pref(n, uid)


mock_users()
# pprint.pprint(u)
