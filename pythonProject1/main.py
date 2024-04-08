import rules
import json
def process_item(obj_dict, file_name):
    rules.apply_rules(obj_dict, "sales", 0)
    rules.just_pretty_print()
    rules.export_er_file(file_name, "Customers buy items as sale", "1.0")


if __name__ == '__main__':
    print('Starting transformation')
    with open("resource/small_sample.json", 'r') as f:
        i = 0
        for line in f:
            i = i+1
            data_dict = json.loads(line)
            process_item(data_dict, 'sales' + str(i))
    print('Done')

