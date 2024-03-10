from flask import Flask, jsonify
from flask import request
from flask_cors import CORS
import inference

app = Flask(__name__)
CORS(app)

model = inference.MedNerModel(model_name='biomistral', embedding_model='biomistral')
store = inference.Store()
parsed_taxonomy = store.get_parsed_taxonomy()["taxonomy"]
code_dictionary = {item["code"]: item["code_id"] for item in parsed_taxonomy}

def get_code(factor):
    return factor if factor in code_dictionary else "Factor not found in the taxonomy"

@app.route('/api/annotate', methods=['POST'])
def annotate_text():
    data = request.get_json()
    text_extracts = data.get('text_extracts', [])

    annotations = []
    unique_factors = {}

    for text_extract in text_extracts:
        annotation = model.get_parsed_annotations(text_extract)
        coded_factors = [{code_dictionary.get(factor, "-1"): get_code(factor)} for factor in annotation['factors']]

        annotation['factors'] = []

        for item in coded_factors:
            code_id = list(item.keys())[0]
            annotation['factors'].append(code_id)
            if code_id not in unique_factors:
                unique_factors[code_id] = {"code_id": code_id, "code": item[code_id]}

        annotations.append(annotation)

    unique_factors_sorted = [unique_factors[item] for item in sorted(unique_factors.keys(), key=int)]

    return jsonify({"annotations": annotations, "unique_factors": unique_factors_sorted})


if __name__ == '__main__':
    app.run(port=5000)