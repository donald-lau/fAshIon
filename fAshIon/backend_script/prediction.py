import json
import pprint
import numpy as np

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from fAshIon.Utils import read_output_file, get_ontology_def, phrase_model_id, normalize_list, phrase_user_file
from fAshIon.backend_script.gui import get_images, prediction_get_images
from fAshIon.backend_script.users import get_user

current_user = "default"
current_id = 0


@csrf_exempt
def set_user(request):
    global current_user
    global current_id
    body_unicode = request.body.decode("utf-8")
    body = json.loads(body_unicode)
    user_id = body["user_id"].split("_")
    current_user = user_id[0]
    current_id = user_id[1]
    return JsonResponse({})


@csrf_exempt
def predict(request):
    global current_user
    global current_id

    # phrasing user input from request
    body_unicode = request.body.decode("utf-8")
    body = json.loads(body_unicode)
    data = body["data"]
    input_items = data["item"]
    input_colors = data["color"]
    input_materials = data["material"]
    # get ontology definition
    onto_def = get_ontology_def()
    # for item prediction
    outfit_component = {"top": 0,
                        "bottom": 0,
                        "footwear": 0,
                        "accessory": 0,
                        "fullwear": 0,
                        "outerwear": 0}
    component_max = 100
    rec_limit = 10

    ############################################################################
    # Get user preference
    ############################################################################
    filename = phrase_user_file(current_user, current_id)
    user = get_user(current_user, current_id)
    # user = read_output_file("user/" + filename, json_format=True)
    user_prefs = {"context": set(),
                  "item": set(),
                  "color": set(),
                  "material": set()}
    for pref in user["pref"]:
        if pref["onto_attr"] == ["context"]:
            user_prefs["context"].add(pref["onto_id"][0])
        if "item" in pref["onto_attr"]:
            item = pref["onto_attr"].index("item")
            user_prefs["item"].add(pref["onto_id"][item])
        if "color" in pref["onto_attr"]:
            color = pref["onto_attr"].index("color")
            user_prefs["color"].add(pref["onto_id"][color])
        if "material" in pref["onto_attr"]:
            material = pref["onto_attr"].index("material")
            user_prefs["material"].add(pref["onto_id"][material])

    # for each input item and its (optional) material get their normalized context score
    # item_context := [score_for_formal, score_for_semi_casual, score_for_casual]
    inputs_context = np.zeros(3)
    for i in range(len(input_items)):
        item = input_items[i]
        material = input_materials[i]
        #  onto_def["item_topic"] = ["top", "bottom", "foot", "accessory", "fullwear", "outerwear"]
        item_type = onto_def["item_topic"][onto_def["item"][item][1]]
        outfit_component[item_type] = component_max

        context = normalize_list(onto_def["item"][item][2])
        if material != "":
            context = [sum(x) for x in zip(context, normalize_list(onto_def["material"][material][1]))]
        context = [x * onto_def["context_multiplier"][item_type] for x in context]
        inputs_context = [sum(x) for x in zip(inputs_context, context)]
    inputs_context = normalize_list(inputs_context)

    ############################################################################
    # User preference on context
    ############################################################################
    context_prefs = user_prefs["context"]
    if len(context_prefs) != 0:
        for pref in user["pref"]:
            if pref["onto_attr"] == ["context"]:
                inputs_context[pref["onto_id"][0]] += pref["value"] * pref["modifier"]
                if inputs_context[pref["onto_id"][0]] < 0:
                    inputs_context[pref["onto_id"][0]] = 0
    inputs_context = normalize_list(inputs_context)
    # print(inputs_context)

    ############################################################################
    # Item prediction
    ############################################################################
    # get similarity for potential recommendations, not using context info
    potential_items = {}
    item_matrix = read_output_file(phrase_model_id(["item"], "_matrix"), "fAshIon/output/matrix")["matrix"]
    # populate potential_items with first input item
    first_item = input_items[0]
    first_item_id = onto_def["item"][first_item][0]
    first_context_mul = onto_def["context_multiplier"][onto_def["item_topic"][onto_def["item"][first_item][1]]]
    for _, (k, v) in enumerate(onto_def["item"].items()):
        sim = item_matrix[first_item_id][v[0]] * first_context_mul if first_item_id != v[0] else 0
        reasoning = [{
            "type": "generic",
            "value": sim,
            "onto_0": first_item,
            "onto_1": k,
            "modifier": 1
        }]
        potential_items[k] = {
            "sim": sim,
            "reason": reasoning
        }
    # update potential_items with remaining item
    for item in input_items:
        if item != first_item:
            item_id = onto_def["item"][item][0]
            item_context_mul = onto_def["context_multiplier"][onto_def["item_topic"][onto_def["item"][item][1]]]
            for _, (k, v) in enumerate(onto_def["item"].items()):
                sim = item_matrix[item_id][v[0]] * item_context_mul if item_id != v[0] else 0
                reasoning = [
                    {
                        "type": "generic",
                        "value": sim,
                        "onto_0": item,
                        "onto_1": k,
                        "modifier": 1
                    }
                ]
                reasons = potential_items[k]["reason"]
                reasons.extend(reasoning)
                sim = potential_items[k]["sim"] + sim
                potential_items[k] = {
                    "sim": sim,
                    "reason": reasons
                }

    ############################################################################
    # User preference on item
    ############################################################################
    for pref in user["pref"]:
        if "item" in pref["onto_attr"]:
            val = pref["value"] * pref["modifier"]
            pref_type = "passive" if pref["type"] == 0 else "active"
            # preference on single item
            if len(pref["onto_attr"]) == 1:
                item_id = pref["onto_id"][0]
                item = onto_def["item_id_lookup"][item_id]
                sim, reasons = potential_items[item]["sim"], potential_items[item]["reason"]
                reasoning = {
                    "type": pref_type,
                    "value": pref["value"],
                    "onto_0": item,
                    "onto_1": "",
                    "modifier": pref["modifier"]
                }
                reasons.append(reasoning)
                sim += val
                potential_items[item]["sim"], potential_items[item]["reason"] = sim, reasons
            # preference on two items
            elif len(pref["onto_attr"]) == 2 and \
                    pref["onto_attr"][0] == pref["onto_attr"][1]:  # both are items
                item_0_id = pref["onto_id"][0]
                item_0 = onto_def["item_id_lookup"][item_0_id]
                item_1_id = pref["onto_id"][1]
                item_1 = onto_def["item_id_lookup"][item_1_id]
                if item_0 in input_items or item_1 in input_items:  # at least one in the preference is in inputs
                    non_input = item_0 if item_1 in input_items else item_1
                    sim, reasons = potential_items[non_input]["sim"], potential_items[non_input]["reason"]
                    for reason in reasons:
                        if (item_0 == reason["onto_0"] and item_1 == reason["onto_1"]) or \
                                (item_1 == reason["onto_0"] and item_0 == reason["onto_1"]):
                            reasons.remove(reason)
                            reason["modifier"] = pref["modifier"]
                            reason["type"] = "passive" if pref["type"] == 0 else "active"
                            reasons.append(reason)
                            sim += val - reason["value"]
                            potential_items[non_input]["sim"] = sim
                            break

    ############################################################################
    # update potentials similarity using context info
    ############################################################################
    for i, (k, v) in enumerate(potential_items.items()):
        k_context = onto_def["item"][k][2]
        potential_items[k]["sim"] = potential_items[k]["sim"] * np.dot(normalize_list(k_context), inputs_context)

    # put the potentials in a list and rank them based on sim-comp value
    potential_list = [(v["sim"], k) for i, (k, v) in enumerate(potential_items.items())]
    potential_list.sort(reverse=True)

    # update outfit flags
    if outfit_component["top"] == component_max or outfit_component["bottom"] == component_max:
        outfit_component["fullwear"] = component_max
    elif outfit_component["fullwear"] == component_max:
        if outfit_component["top"] != component_max and outfit_component["bottom"] != component_max:
            outfit_component["top"] = component_max
            outfit_component["bottom"] = component_max
    outfit_component["accessory"] = 0

    # select potential as recommendation if its type isn't flagged or
    # recommendations of its type doesn't have too many already compare to other types
    rec_items = []
    lowest_type_cnt = 0
    # TODO: change how to select item when one class has too many
    for (sim, potential) in potential_list:
        if potential not in input_items:
            potential_type = onto_def["item_topic"][onto_def["item"][potential][1]]
            if outfit_component[potential_type] < component_max and \
                    ((potential_type != "accessory" and outfit_component[potential_type] - lowest_type_cnt < 3) or
                     (potential_type == "accessory" and outfit_component[potential_type] - lowest_type_cnt < 1)):
                rec = potential_items[potential]
                rec["item"] = potential
                rec_items.append(rec)
                outfit_component[potential_type] += 1
                lowest_type_cnt = min([v for _, (_, v) in enumerate(outfit_component.items())])
                if len(rec_items) >= rec_limit:
                    break

    ############################################################################
    # Material prediction
    ############################################################################
    rec_materials = []
    potential_materials = {}
    item_material_matrix = read_output_file(phrase_model_id(["item", "material"], "_matrix")
                                            , "fAshIon/output/matrix")["matrix"]
    for rec in rec_items:
        ############################################################################
        # generic sim-comp value for material based on recommendation item
        ############################################################################
        rec_item = rec["item"]
        nearby_material = item_material_matrix[onto_def["item"][rec_item][0]]
        nearby_material = nearby_material[: len(onto_def["material_id_lookup"])]
        for material_id, sim in enumerate(nearby_material):
            material = onto_def["material_id_lookup"][material_id]
            reasoning = [{
                "type": "generic",
                "value": sim,
                "onto_0": rec_item,
                "onto_1": material,
                "modifier": 1
            }]
            potential_materials[material] = {
                "sim": sim,
                "reason": reasoning
            }

        ############################################################################
        # User preference on material
        ############################################################################
        for pref in user["pref"]:
            if "material" in pref["onto_attr"]:
                val = pref["value"] * pref["modifier"]
                pref_type = "passive" if pref["type"] == 0 else "active"
                # preference on single material
                if len(pref["onto_attr"]) == 1:
                    material_id = pref["onto_id"][0]
                    material = onto_def["material_id_lookup"][material_id]
                    sim, reasons = potential_materials[material]["sim"], potential_materials[material]["reason"]
                    reasoning = {
                        "type": pref_type,
                        "value": pref["value"],
                        "onto_0": material,
                        "onto_1": "",
                        "modifier": pref["modifier"]
                    }
                    reasons.append(reasoning)
                    sim += val
                    potential_materials[material]["sim"], potential_materials[material]["reason"] = sim, reasons
                # preference on material and item
                elif len(pref["onto_attr"]) == 2 and "item" in pref["onto_attr"]:
                    item_id = pref["onto_id"][pref["onto_attr"].index("item")]
                    item = onto_def["item_id_lookup"][item_id]
                    # if item in pref is same as recommendation item
                    if rec_item == item:
                        material_id = pref["onto_id"][pref["onto_attr"].index("material")]
                        material = onto_def["material_id_lookup"][material_id]
                        sim, reasons = potential_materials[material]["sim"], potential_materials[material]["reason"]
                        for reason in reasons:
                            if rec_item in [reason["onto_0"], reason["onto_1"]] and \
                                    material in [reason["onto_0"], reason["onto_1"]]:
                                reasons.remove(reason)
                                reason["modifier"] = pref["modifier"]
                                reason["type"] = "passive" if pref["type"] == 0 else "active"
                                reasons.append(reason)
                                sim += val - reason["value"]
                                potential_materials[material]["sim"] = sim
                                break

        ############################################################################
        # update potentials value using context info
        ############################################################################
        for _, (material, sim_reasoning) in enumerate(potential_materials.items()):
            sim = sim_reasoning["sim"]
            sim = sim * np.dot(normalize_list(onto_def["material"][material][1]), inputs_context)
            sim_reasoning["sim"] = sim

        potential_list = [(v["sim"], k) for _, (k, v) in enumerate(potential_materials.items())]
        potential_list.sort(reverse=True)

        _, potential = potential_list[0]
        rec = potential_materials[potential]
        rec["material"] = potential
        rec_materials.append(rec)

    ############################################################################
    # Color prediction
    ############################################################################
    # get similarity for potential recommendations based on input color
    rec_colors = []
    potential_colors = {}
    color_matrix = read_output_file(phrase_model_id(["color"], "_matrix"), "fAshIon/output/matrix")["matrix"]
    root_color_scheme = np.full(len(onto_def["color_topic"]), 0)
    input_colors = list(filter(None, input_colors))
    if len(input_colors) > 0:
        first_color = input_colors[0]
        first_color_id = onto_def["color"][first_color][0]
        for _, (k, v) in enumerate(onto_def["color"].items()):
            # sim = color_matrix[first_color_id][v[0]] if first_color_id != v[0] else 0
            sim = color_matrix[first_color_id][v[0]]
            potential_colors[k] = sim
        for color in input_colors:
            if color != first_color:
                color_id = onto_def["color"][color][0]
                for _, (k, v) in enumerate(onto_def["color"].items()):
                    # sim = color_matrix[color_id][v[0]] if color_id != v[0] else 0
                    sim = color_matrix[color_id][v[0]]
                    potential_colors[k] = potential_colors[k] + sim
        potential_colors = [(v, k) for _, (k, v) in enumerate(potential_colors.items())]
        potential_colors.sort(reverse=True)
        potential_colors = potential_colors[:10]
        for (_, color) in potential_colors:
            root_colors = onto_def["color"][color][1]
            for rc in root_colors:
                root_color_scheme[rc] += 1
        root_color_scheme = normalize_list(root_color_scheme)
    else:
        root_color_scheme = np.full(len(onto_def["color_topic"]), 1)

    item_color_matrix = read_output_file(phrase_model_id(["item", "color"], "_matrix")
                                         , "fAshIon/output/matrix")["matrix"]
    material_color_matrix = read_output_file(phrase_model_id(["material", "color"], "_matrix")
                                             , "fAshIon/output/matrix")["matrix"]
    for i in range(len(rec_items)):
        rec_item = rec_items[i]["item"]
        rec_material = rec_materials[i]["material"]
        rec_item_id = onto_def["item"][rec_item][0]
        rec_material_id = onto_def["material"][rec_material][0]
        nearby_colors = item_color_matrix[rec_item_id]
        nearby_colors = nearby_colors[: len(onto_def["color_id_lookup"])]
        potential_colors = {}
        for color_id, sim in enumerate(nearby_colors):
            color = onto_def["color_id_lookup"][color_id]
            reasoning = [{
                "type": "generic",
                "value": sim,
                "onto_0": rec_item,
                "onto_1": color,
                "modifier": 1
            }]
            potential_colors[color] = {
                "sim": sim,
                "reason": reasoning
            }
        nearby_colors = material_color_matrix[rec_material_id]
        nearby_colors = nearby_colors[: len(onto_def["color_id_lookup"])]
        for color_id, sim in enumerate(nearby_colors):
            color = onto_def["color_id_lookup"][color_id]
            reasons = potential_colors[color]["reason"]
            reasoning = [{
                "type": "generic",
                "value": sim,
                "onto_0": rec_material,
                "onto_1": color,
                "modifier": 1
            }]
            reasons.extend(reasoning)
            sim = potential_colors[color]["sim"] + sim
            potential_colors[color] = {
                "sim": sim,
                "reason": reasons
            }

        ############################################################################
        # User preference on color
        ############################################################################
        for pref in user["pref"]:
            if "color" in pref["onto_attr"]:
                val = pref["value"] * pref["modifier"]
                pref_type = "passive" if pref["type"] == 0 else "active"
                # preference on single color
                if len(pref["onto_attr"]) == 1:
                    color_id = pref["onto_id"][0]
                    color = onto_def["color_id_lookup"][color_id]
                    sim, reasons = potential_colors[color]["sim"], potential_colors[color]["reason"]
                    reasoning = {
                        "type": pref_type,
                        "value": pref["value"],
                        "onto_0": color,
                        "onto_1": "",
                        "modifier": pref["modifier"]
                    }
                    reasons.append(reasoning)
                    sim += val
                    potential_colors[color]["sim"], potential_colors[color]["reason"] = sim, reasons
                # preference on color and item
                elif len(pref["onto_attr"]) == 2 and \
                        ("item" in pref["onto_attr"] or "material" in pref["onto_attr"]):
                    attr = "item" if "item" in pref["onto_attr"] else "material"
                    attr_id = pref["onto_id"][pref["onto_attr"].index(attr)]
                    attr = onto_def[attr + "_id_lookup"][attr_id]
                    # if item in pref is same as recommendation item
                    if rec_item == attr or rec_material == attr:
                        color_id = pref["onto_id"][pref["onto_attr"].index("color")]
                        color = onto_def["color_id_lookup"][color_id]
                        sim, reasons = potential_colors[color]["sim"], potential_colors[color]["reason"]
                        for reason in reasons:
                            if color in [reason["onto_0"], reason["onto_1"]] and \
                                    (rec_item in [reason["onto_0"], reason["onto_1"]] or
                                     rec_material in [reason["onto_0"], reason["onto_1"]]):
                                reasons.remove(reason)
                                reason["modifier"] = pref["modifier"]
                                reason["type"] = "passive" if pref["type"] == 0 else "active"
                                reasons.append(reason)
                                sim += val - reason["value"]
                                potential_colors[color]["sim"] = sim
                                break

        ############################################################################
        # update potentials value using root color scheme info
        ############################################################################
        for _, (color, sim_reasoning) in enumerate(potential_colors.items()):
            sim = sim_reasoning["sim"]
            roots = onto_def["color"][color][1]
            for root in roots:
                sim = sim * (1 + root_color_scheme[root])
            sim_reasoning["sim"] = sim

        potential_list = [(v["sim"], k) for _, (k, v) in enumerate(potential_colors.items())]
        potential_list.sort(reverse=True)

        _, potential = potential_list[0]
        rec = potential_colors[potential]
        rec["color"] = potential
        rec_colors.append(rec)

    ############################################################################
    # Prediction to Json
    ############################################################################
    rec_json = {"pred_cnt": len(rec_items)}
    for i in range(len(rec_items)):
        image_urls = prediction_get_images(rec_colors[i]["color"],
                                           rec_materials[i]["material"],
                                           rec_items[i]["item"])
        # image_urls = get_images(image_search, limit=3)
        rec_json[i] = {
            "item": rec_items[i],
            "material": rec_materials[i],
            "color": rec_colors[i],
            "url_max_id": len(image_urls),
            "urls": image_urls
        }

    # pprint.pprint(rec_json)
    return JsonResponse(rec_json)
