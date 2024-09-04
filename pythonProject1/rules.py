import json
import re

entity_dict = {}

mongo_db_string_list = []
relations_list = []

padding1 = "     "
padding2 = "  "


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
    if entity_name not in entity_dict.keys():
        entity_dict[entity_name] = {
            "_cardinal": cardinal
        }
    for key in obj_dict.keys():
        key_type = type(obj_dict[key])
        # R3
        if key_type == dict:
            first_key = next(iter(obj_dict[key]))
            if '$' in first_key:
                type_name = first_key.replace('$', '')
                entity_dict[entity_name][key] = type_name
            else:
                apply_rules(obj_dict[key], key, 1)
        # R4
        elif key_type == list:
            item_type = type(obj_dict[key][0])
            if item_type == dict:
                apply_rules(obj_dict[key][0], key, 'N')
            else:
                entity_dict[entity_name][key] = class_str_mapper(item_type) + '[]'
        # R2
        elif key != '_id':
            entity_dict[entity_name][key] = class_str_mapper(key_type)


def build_relations(related_collections):
    entity_name = None
    for key in entity_dict.keys():
        relation = {}
        cardinal = entity_dict[key]['_cardinal']
        formatted_key = str(key).capitalize()
        if cardinal == 0:
            if entity_name is not None and related_collections:
                relation['name'] = entity_name + formatted_key
                relation['entity_list'] = '(' + entity_name + ', ' + formatted_key + ')'
                relations_list.append(relation)
            entity_name = formatted_key
        else:
            relation['name'] = entity_name + formatted_key
            relation['entity_list'] = '(' + entity_name + ', ' + formatted_key + ')'
            relations_list.append(relation)


def add_mongo_str(collection, attr, str_type, padding_attr):
    mongo_str = (padding_attr + attr.capitalize() + ": " + str_type + padding2 + '< ' + collection + '.'
                 + attr.capitalize() + ' >\n')
    mongo_db_string_list.append(mongo_str)


def build_mongo_string_list(link_attr_dict):
    collection_name = '\n'
    for key in entity_dict.keys():
        cardinal = entity_dict[key]['_cardinal']
        formatted_key = str(key).capitalize()
        padding_attr = padding1

        if cardinal == 0:
            collection_name = '\n\n' + formatted_key + 'Collection' + '\n{\n'
            if len(mongo_db_string_list) > 0:
                mongo_db_string_list.append('\n}')
        elif cardinal == 1:
            collection_name = padding1 + formatted_key + ':{' + '\n'
            padding_attr = padding1 + padding2
        elif cardinal == 'N':
            collection_name = padding1 + formatted_key + '['
            padding_attr = padding1 + padding2
        mongo_db_string_list.append(collection_name)

        for attr in entity_dict[key]:
            if attr != "_cardinal":
                if attr in link_attr_dict.keys():
                    add_mongo_str(link_attr_dict[attr], str(attr), str(entity_dict[key][attr]), padding_attr)
                else:
                    add_mongo_str(formatted_key, str(attr), str(entity_dict[key][attr]), padding_attr)

        if cardinal != 0:
            if '{' in collection_name:
                mongo_db_string_list.append(padding1 + '}\n')
            elif '[' in collection_name:
                mongo_db_string_list.append(padding1 + ']\n')

    mongo_db_string_list.append('}')


def export_er_file(solution, description, version):
    file_path = "er/" + solution.lower() + ".txt"
    head_text = "__Solution__: \"" + solution + "\"\n__Description__: " + description + "\n__Version__: " + version
    er_model_title = "\n\n###################  ERModel ######################"
    mongo_title = "\n###################  MongoDBSchema ######################\n"
    relation_name = ""
    relation_collections = "( "

    with open(file_path, 'w') as file:
        file.write(head_text)
        file.write(er_model_title)
    with open(file_path, 'a') as file:
        for key in entity_dict.keys():
            formatted_key = str(key).capitalize()
            relation_name = relation_name + formatted_key
            relation_collections = relation_collections + formatted_key + ','

            entity_dict[key].pop('_cardinal')

            attribute_name = "> " + str(key).capitalize() + "ID"
            er_entities = str(entity_dict[key]).replace("'", "").replace(',', '\n')
            er_entities = re.sub(r'\b_id\b', attribute_name, er_entities)
            file.write('\n\n')
            file.write(formatted_key + "\n" + er_entities)
        file.write('\n\n')
        for r in relations_list:
            file.write(r['name'] + " " + r['entity_list'] + ' {}\n')
        file.write(mongo_title)
        for line in mongo_db_string_list:
            file.write(line)


def just_pretty_print():
    er_entities = str(entity_dict).replace(',', ',\n').replace("}", "}\n")
    print(er_entities)
