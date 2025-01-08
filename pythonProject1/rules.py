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


def build_relations(manual_db_ref):
    entity_name = None
    for key in entity_dict.keys():
        relation = {}
        cardinal = entity_dict[key]['_cardinal']
        formatted_key = str(key)
        if cardinal == 0:
            entity_name = formatted_key
            for collection in manual_db_ref:
                if collection["collection"] == entity_name:
                    relation['name'] = entity_name + collection["ref"]
                    relation['entity_list'] = '(' + entity_name + ', ' + collection["ref"] + ')'
                    relations_list.append(relation)
        else:
            relation['name'] = entity_name + formatted_key
            relation['entity_list'] = '(' + entity_name + ', ' + formatted_key + ')'
            relations_list.append(relation)


def add_mongo_str(collection, attr, str_type, padding_attr, attr_on_er):
    mongo_str = (padding_attr + attr + ": " + str_type + padding2 + '< ' + collection + '.'
                 + attr_on_er + ' >\n')
    mongo_db_string_list.append(mongo_str)

def is_attr_ref(manual_db_ref, target_collection_name, attr):
    for collection in manual_db_ref:
        if collection["collection"] == target_collection_name:
            if collection["key"] == attr:
                return collection
    return None

def build_entity_list_in_collection(manual_db_ref):
    entity_list_in_collection = {}
    root_collection = ""
    for key in entity_dict.keys():
        cardinal = entity_dict[key]['_cardinal']
        formatted_key = str(key)
        if cardinal == 0:
            if root_collection != "":
                entity_list_in_collection[root_collection] = entity_list_in_collection[root_collection] + " >"
            root_collection = formatted_key
            entity_list_in_collection[root_collection] = "< " + formatted_key + "*"
        else:
            entity_list_in_collection[root_collection] = entity_list_in_collection[root_collection] + ", " + formatted_key
        for c in manual_db_ref:
            if c['collection'] == root_collection:
                entity_list_in_collection[root_collection] = entity_list_in_collection[root_collection] + ", " + c['ref']
    entity_list_in_collection[root_collection] = entity_list_in_collection[root_collection] + " >"
    return entity_list_in_collection

def build_mongo_string_list(manual_db_ref):
    collection_name = '\n'
    entity_list_in_collection = build_entity_list_in_collection(manual_db_ref)
    for key in entity_dict.keys():
        cardinal = entity_dict[key]['_cardinal']
        formatted_key = str(key)
        padding_attr = padding1

        if cardinal == 0:
            collection_name = '\n\n' + formatted_key + 'Collection ' + entity_list_in_collection[formatted_key] + '\n{\n'
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
                reference_collection = is_attr_ref(manual_db_ref, formatted_key, attr)
                if reference_collection is not None:
                    add_mongo_str(reference_collection["ref"], str(attr), str(entity_dict[key][attr]), padding_attr, str(reference_collection["ref"]) + "ID")
                elif attr == "_id":
                    add_mongo_str(formatted_key, str(attr), str(entity_dict[key][attr]), padding_attr, formatted_key + "ID")
                else:
                    add_mongo_str(formatted_key, str(attr), str(entity_dict[key][attr]), padding_attr, str(attr))

        if cardinal != 0:
            if '{' in collection_name:
                mongo_db_string_list.append(padding1 + '}\n')
            elif '[' in collection_name:
                mongo_db_string_list.append(padding1 + ']\n')
    mongo_db_string_list.append('}')

def remove_relation_att(entity):
    # Regex to find keys with '_id'
    regex = r'\b(?!_id\b)\w*_id\w*\b'
    attr_to_pop = [k for k in entity if re.search(regex, k)]
    for k in attr_to_pop:
        entity.pop(k)

def write_er_model_to_file(file):
    relation_name = ""
    relation_collections = "( "
    for key in entity_dict.keys():
        formatted_key = str(key)
        relation_name = relation_name + formatted_key
        relation_collections = relation_collections + formatted_key + ','

        entity_dict[key].pop('_cardinal')
        remove_relation_att(entity_dict[key])

        attribute_name = "> " + str(key) + "ID"
        er_entities = str(entity_dict[key]).replace("'", "").replace(',', '\n')
        er_entities = re.sub(r'\b_id\b', attribute_name, er_entities)

        file.write('\n\n')
        file.write(formatted_key + "\n" + er_entities)
    file.write('\n\n')

def write_relationships_to_file(file):
    for r in relations_list:
        file.write(r['name'] + " " + r['entity_list'] + ' {}\n')

def write_mongo_db_map_to_file(file):
    for line in mongo_db_string_list:
        file.write(line)

def export_er_file(solution, description, version):
    file_path = "er/" + solution.lower() + ".txt"
    head_text = "__Solution__: \"" + solution + "\"\n__Description__: " + description + "\n__Version__: " + version
    er_model_title = "\n\n###################  ERModel ######################"
    mongo_title = "\n###################  MongoDBSchema ######################\n"

    with open(file_path, 'w') as file:
        file.write(head_text)
        file.write(er_model_title)
    with open(file_path, 'a') as file:
        write_er_model_to_file(file)
        write_relationships_to_file(file)
        file.write(mongo_title)
        write_mongo_db_map_to_file(file)

def just_pretty_print():
    er_entities = str(entity_dict).replace(',', ',\n').replace("}", "}\n")
    print(er_entities)
