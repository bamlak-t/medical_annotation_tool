from typing import List, Dict, Any
from flask import Flask, jsonify
from flask import request
from flask_cors import CORS

import models.OllamaModel as ollama_model
import models.TorchModel as torch_model
import store
import database
import inference
from enum import Enum
import logging

logging.basicConfig(filename='logs/annotation_app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)

app = Flask(__name__)
CORS(app)

AUTO_TRAIN_PATH = 'auto_train'

# enum for model selection
class ModelType(Enum):
    OLLAMA = 'OLLAMA_MODEL'
    TORCH = 'TORCH_MODEL'

class AnnotationApp:
    """	
    An backend application for annotating text extracts with factors from the taxonomy
    """

    def __init__(self):
        # store manager to load the taxonomy, prompt, and examples
        store_manager = store.Store()

        # inference manager to manage the input and output of the model
        manager = inference.Manager(store_manager)
        self.manager = manager

        # initialise pre-trained and fine-tuned models
        model_params = {
            'store': store_manager,
            'output_parser': manager.output_parser,
            'few_shot_template': manager.few_shot_template
        }
        self.ollama_model = ollama_model.OllamaAnnotationModel(**model_params)
        self.torch_model = None # torch_model.TorchAnnotationModel(**model_params)

        # database to store the annotations results
        self.annotation_db = database.AnnotationDb()

        parsed_taxonomy = store_manager.get_parsed_taxonomy()

        self.code_to_id_dictionary = {
            item['code']: item['code_id'] for item in parsed_taxonomy}
        self.id_to_code_dictionary = {
            item['code_id']: item['code'] for item in parsed_taxonomy}


    def annotate_text(self, 
                      text_extracts: List[str], 
                      text_extract_ids: List[int], 
                      save_response: bool, 
                      redo: bool, 
                      model_type: str) -> Dict[str, Any]:
        """
        Annotate text extracts with factors from the taxonomy

        Args: 
            text_extracts (list): list of text extracts to be annotated
            text_extract_ids (list): list of indices of text extracts to be annotated (empty list implies all text extracts)
            save_response (bool): flag to save the response in the database
            redo (bool): flag to redo the annotation
            model_type (str): type of model to be used for annotation

        Return: 
            dict: dictionary containing annotations and unique factors
        """
        logging.info('Starting annotation of text extracts')

        # list of parsed annotations
        annotations_list = []
        unique_factors = {}

        # select model based on model_type
        model = self.ollama_model if model_type == ModelType.OLLAMA else self.torch_model

        for index, text_extract in enumerate(text_extracts):
            # skip text extracts for selective annotation
            if text_extract_ids and index not in text_extract_ids:
                continue

            # invoke model and parse output into JSON
            logging.info(f'Annotating text extract at index {index}')
            parsed_annotations = model.get_parsed_annotations(text_extract)[
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

        if save_response:
            to_save = []
            for item in annotations_list:
                extract = item['text_extract']
                coded_factors = item['factors']
                
                # aggregate the factors into a string
                labels = ", ".join([self.get_code_by_id(factor_code)
                                    for factor_code in coded_factors])

                to_save.append((extract, labels))

            self.annotation_db.insert_bulk_row(to_save)

        if redo:
            with open(AUTO_TRAIN_PATH + '/train.csv', 'a') as file:
                for item in annotations_list:
                    data_point = f'{self.manager.get_full_prompt()},{item["text_extract"]},,\n'
                    file.write(data_point)

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
    model_type = data.get('model_type', ModelType.OLLAMA.value)

    logging.info(f'Annotating {len(text_extracts)} text extracts with model type {model_type}')

    annotation_app = AnnotationApp()

    result = annotation_app.annotate_text(
        text_extracts, text_extract_ids, 
        save_response=True, 
        redo=len(text_extract_ids) > 0, 
        model_type=ModelType(model_type))

    return jsonify(result)


if __name__ == '__main__':
    app.run(port=5000)
