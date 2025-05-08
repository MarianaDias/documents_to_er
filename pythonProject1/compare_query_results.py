import json
import re

def compare_json(obj1, obj2):
    if isinstance(obj1, dict) and isinstance(obj2, dict):
        if set(obj1.keys()) != set(obj2.keys()):
            return False
        for key in obj1:
            if not compare_json(obj1[key], obj2[key]):
                return False
        return True
    elif isinstance(obj1, list) and isinstance(obj2, list):
        if len(obj1) != len(obj2):
            return False
        for item1, item2 in zip(obj1, obj2):
            if not compare_json(item1, item2):
                return False
        return True
    else:
        return obj1 == obj2

def compare_all(data, number_of_queries):
    for i in range(1, number_of_queries + 1):
        native_query_key = "native_query" + str(i)
        query_key = "query" + str(i)
        r = compare_json(data[query_key], data[native_query_key])
        print ("Query " + str(i) + ": " + str(r))

def preprocess_mongo_json(text):
    # Converte ObjectId("...") para apenas "..."
    text = re.sub(r'ObjectId\("([a-fA-F0-9]{24})"\)', r'"\1"', text)
    # Converte ISODate("...") para apenas "..."
    text = re.sub(r'ISODate\("([^"]+)"\)', r'"\1"', text)
    return text

# Lê o arquivo como texto bruto
with open("resource/resultados.json", "r", encoding="utf-8") as f:
    raw_text = f.read()

# Pré-processa para remover os wrappers ObjectId(...) e ISODate(...)
clean_text = preprocess_mongo_json(raw_text)

# Agora carrega com json normalmente
data = json.loads(clean_text)

compare_all(data, 5)
