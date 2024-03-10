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

@app.route('/api/annotate', methods=['POST'])
def annotate_text():
    data = request.get_json()
    text_extracts = data.get('text_extracts', [])

    annotations = []
    unique_factors = {}

    for text_extract in text_extracts:
        annotation = model.get_parsed_annotations(text_extract)
        coded_factors = [{code_dictionary[factor]: factor} for factor in annotation['factors']]
        
        for item in coded_factors:
            code_id = list(item.keys())[0]
            if code_id not in unique_factors:
                unique_factors[code_id] = item

        annotations.append(annotation)

    return jsonify({"annotations": annotations, "unique_factors": list(unique_factors.values())})


if __name__ == '__main__':
    app.run(port=5000)