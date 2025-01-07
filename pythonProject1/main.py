import rules
import json


def process_item(obj_dict, name):
    rules.apply_rules(obj_dict, name, 0)


def run_n_files(path_list, coll_names, solution, description, version, manual_db_ref=[]):
    i = 0
    for path in path_list:
        with open(path, 'r') as f:
            for line in f:
                data_dict = json.loads(line)
                process_item(data_dict, coll_names[i])
        i = i + 1
    rules.build_relations(manual_db_ref)
    rules.build_mongo_string_list(manual_db_ref)
    rules.export_er_file(solution, description, version)


if __name__ == '__main__':
    print('Starting transformation')
    #run_n_files(["resource/sample_sales_1.json"], ["Sales"], "sales_1", "\"Sales\"", "\"1.0\"")
    #run_n_files(["resource/mflix/movies.json", "resource/mflix/comments.json"], ["Movies", "Comments"],
     #           "mflix_3", "\"Movies e Comments\"", "\"1.0\"", True, {"movie_id": "Movies"})
    run_n_files(["resource/mflix/movies.json", "resource/mflix/comments.json"], ["Movies", "Comments"],
                "mflix_4", "\"Movies e Comments\"", "\"1.0\"", [{"collection": "Comments", "ref": "Movies", "key": "movie_id"}])
    print('Done')
