from typing import List, Dict, Any
from flask import Flask, jsonify
from flask import request
from flask_cors import CORS
import inference
import logging

logging.basicConfig(filename='logs/annotation_app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)


app = Flask(__name__)
CORS(app)


class AnnotationApp:
    """	
    An backend application for annotating text extracts with factors from the taxonomy
    """

    def __init__(self):
        self.store = inference.Store()
        self.model = inference.MedNerModel(
            model_name='biomistral', embedding_model='biomistral')

        self.parsed_taxonomy = self.store.get_parsed_taxonomy()['taxonomy']

        self.code_to_id_dictionary = {
            item['code']: item['code_id'] for item in self.parsed_taxonomy}
        self.id_to_code_dictionary = {
            item['code_id']: item['code'] for item in self.parsed_taxonomy}

    def annotate_text(self, text_extracts: List[str], text_extract_ids: List[int]) -> Dict[str, Any]:
        """
        Annotate text extracts with factors from the taxonomy

        Args: 
            text_extracts (list): list of text extracts to be annotated
            text_extract_ids (list): list of indices of text extracts to be annotated (empty list implies all text extracts)

        Return: 
            dict: dictionary containing annotations and unique factors
        """
        logging.info('Starting annotation of text extracts')

        annotations_list = []
        unique_factors = {}

        for index, text_extract in enumerate(text_extracts):
            # skip text extracts for selective annotation
            if text_extract_ids and index not in text_extract_ids:
                continue

            # invoke model and parse output into JSON
            logging.info(f'Annotating text extract at index {index}')
            parsed_annotations = self.model.get_parsed_annotations(text_extract)[
                'factors']

            # convert factors into respective codes
            coded_factors = [self.code_to_id_dictionary.get(
                factor, -1) for factor in parsed_annotations]

            # keep track of unique factors
            for code_id in coded_factors:
                if code_id not in unique_factors:
                    unique_factors[code_id] = {
                        'code_id': code_id, 'code': self.get_code_by_id(code_id)}

            annotation = {
                'id': index, 'text_extract': text_extract, 'factors': coded_factors}
            annotations_list.append(annotation)

        unique_factors_sorted = [unique_factors[item]
                                 for item in sorted(unique_factors.keys(), key=int)]

        logging.info('Finished annotation of text extracts')
        return {'annotations': annotations_list, 'unique_factors': unique_factors_sorted}

    def get_code_by_id(self, id: str) -> str:
        """
        Get the code associated with a given code_id

        Args:
            id (str): code_id to be converted to code

        Return:
            str: code associated with the given code_id
        """
        return self.id_to_code_dictionary[id] if id != -1 else 'Factor not found in the taxonomy'


@app.route('/api/annotate', methods=['POST'])
def annotate_route():
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'Invalid JSON'}), 400

    text_extracts = data.get('text_extracts', [])
    text_extract_ids = set(data.get('text_extract_ids', []))

    app = AnnotationApp()
    result = app.annotate_text(text_extracts, text_extract_ids)

    return jsonify(result)


if __name__ == '__main__':
    app.run(port=5000)
