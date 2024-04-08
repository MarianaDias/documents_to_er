import json

entity_dict = {}


def read_all(file_path):
    all_obj = []
    with open(file_path, 'r') as f:
        for line in f:
            all_obj.append(json.loads(line))
    return all_obj


def read_doc_from_json(file_path):
    with open(file_path, 'r') as f:
        data_dict = json.load(f)
        return data_dict


def class_str_mapper(c):
    if c == str:
        return "string"
    elif c == bool:
        return "boolean"
    elif c == int:
        return "int"
    elif c == float:
        return "float"


def apply_rules(obj_dict: object, entity_name: object, cardinal: object) -> object:
    # R1
    entity_dict[entity_name] = {
        "_cardinal": cardinal
    }
    for key in obj_dict.keys():
        key_type = type(obj_dict[key])
        # R3
        if key_type == dict:
            first_key = next(iter(obj_dict[key]))
            if '$' in first_key:
                entity_dict[entity_name][key] = first_key.replace('$', '')
            else:
                apply_rules(obj_dict[key], key, 1)
        # R4
        elif key_type == list:
            item_type = type(obj_dict[key][0])
            if item_type == dict:
                apply_rules(obj_dict[key][0], key, 'N')
            else:
                entity_dict[entity_name][key] = [class_str_mapper(item_type)]
        # R2
        elif key != '_id':
            entity_dict[entity_name][key] = class_str_mapper(key_type)


def export_er_file(solution, description, version):
    file_path = "er/" + solution.lower() + ".txt"
    head_text = "Solution: " + solution + "\nDescription: " + description + "\nVersion: " + version
    er_model_title = "\n\n###################  ERModel ######################"

    with open(file_path, 'w') as file:
        file.write(head_text)
        file.write(er_model_title)
    with open(file_path, 'a') as file:
        for key in entity_dict.keys():
            formatted_key = str(key).capitalize()
            er_entities = str(entity_dict[key]).replace(',', ',\n')
            file.write('\n\n')
            file.write(formatted_key + " " + er_entities)


def just_pretty_print():
    er_entities = str(entity_dict).replace(',', ',\n').replace("}", "}\n")
    print(er_entities)
