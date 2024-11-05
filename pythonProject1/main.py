import rules
import json


def process_item(obj_dict, name):
    rules.apply_rules(obj_dict, name, 0)

def run_N_files():
    path_list = ["resource/sample_sales_1.json"]
    coll_names = ["Sales"]
    i = 0
    for path in path_list:
        with open(path, 'r') as f:
            for line in f:
                data_dict = json.loads(line)
                process_item(data_dict, coll_names[i])
        i = i + 1
    rules.build_relations(False)
    rules.build_mongo_string_list({})
    rules.export_er_file("sales_1", "\"Sales\"", "\"1.0\"")


if __name__ == '__main__':
    print('Starting transformation')
    run_N_files()
    print('Done')

