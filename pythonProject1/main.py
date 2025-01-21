import rules
import json


def process_item(obj_dict, name):
    rules.apply_rules(obj_dict, name, 0, name)


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
    run_n_files(["resource/mflix/movies.json", "resource/mflix/comments.json", "resource/mflix/theaters.json"], ["Movies", "Comments", "Theaters"],"mflix_5", "\"Movies, Comments e Theaters\"", "\"1.0\"", [{"collection": "Comments", "ref": "Movies", "key": "movie_id"}])
    print('Done')
