import rules
import json


def process_item(obj_dict, name):
    rules.apply_rules(obj_dict, name, 0)

def run_1_file():
    with open("resource/mflix/sample_movie_2.json", 'r') as f:
        i = 0
        for line in f:
            i = i+1
            data_dict = json.loads(line)
            process_item(data_dict, 'movies')
    rules.build_mongo_string_list()
    rules.export_er_file("mflix_movies_2_" + str(i), "Movies", "1.0")

def run_N_files():
    path_list = ["resource/mflix/movies.json", "resource/mflix/comments.json"]
    coll_names = ["Movies", "Comments"]
    i = 0
    for path in path_list:
        with open(path, 'r') as f:
            for line in f:
                data_dict = json.loads(line)
                process_item(data_dict, coll_names[i])
        i = i + 1
    rules.build_relations(True)
    rules.build_mongo_string_list({"movie_id": "Movies"})
    rules.export_er_file("mflix_movies_comments", "Movies e Comments", "1.0")


if __name__ == '__main__':
    print('Starting transformation')
    run_N_files()
    print('Done')

