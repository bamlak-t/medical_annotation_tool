from langchain_community.llms import Ollama
import logging

MODEL_NAME = 'mistral'
EMBEDDING_MODEL = 'mistral'


class OllamaAnnotationModel:
    """
    OllamaAnnotationModel class to annotate text extracts with factors from the taxonomy
    """

    def __init__(self,  store, output_parser, few_shot_template, model_name=MODEL_NAME, embedding_model=EMBEDDING_MODEL) -> None:
        self.llm = Ollama(model=model_name)
        # OllamaEmbeddings(model=embedding_model)
        self.embedding_model = embedding_model
        self.store = store
        self.output_parser = output_parser
        self.few_shot_template = few_shot_template
        logging.info(
            f'OllamaAnnotationModel initialized with model: {model_name}')

    def get_annotations(self, text_extract):
        """
        Get the annotations for a given text extract

        Args:
            text_extract (str): text extract to be annotated

        Return:
            dict: dictionary containing annotations
        """
        chain = self.few_shot_template | self.llm
        return chain.invoke({'text_extract': text_extract, 'taxonomy': self.store.get_taxonomy()})

    def get_parsed_annotations(self, text_extract):
        """
        Get the parsed annotations for a given text extract

        Args:
            text_extract (str): text extract to be annotated

        Return:
            dict: dictionary containing parsed annotations
        """
        try:
            annotated = self.get_annotations(text_extract)
            output = self.output_parser.parse(annotated)
            return output
        except Exception as e:
            return {'text_extract': text_extract, 'factors': ['Error parsing annotations']}


if __name__ == '__main__':
    import sys
    sys.path.insert(0,  '..') 
    import store
    import inference

    extract = 'This means that IA was not performed in line with local or national guidance.'

    TAXONOMY_FILE = '../constants/taxonomy.json'
    PROMPT_FILE = '../constants/prompt.txt'
    EXAMPLES_FILE = '../constants/examples.json'

    store_manager = store.Store(TAXONOMY_FILE, PROMPT_FILE, EXAMPLES_FILE)
    inference_manager = inference.Manager(store_manager)

    model = OllamaAnnotationModel(store=store_manager, output_parser=inference_manager.output_parser,
                                 few_shot_template=inference_manager.few_shot_template)

    extract = 'This means that IA was not performed in line with local or national guidance.'

    output = model.get_parsed_annotations(extract)
    print('output', output)