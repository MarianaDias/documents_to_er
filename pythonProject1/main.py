import rules

if __name__ == '__main__':
    print('Starting transformation')
    obj_dict = rules.read_doc_from_json("resource/sales_unit.json")
    rules.apply_rules(obj_dict, "sales", 0)
    rules.just_pretty_print()
    rules.export_er_file("Sales", "Customers buy items as sale", "1.0")
    print('Done')

