import torch
import logging
import textwrap
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

MODEL_NAME = 'mistralai/Mistral-7B-Instruct-v0.2'
# 'C:/Users/bamla/Desktop/llm_proj/medical_annotation_tool/backend/autotrainer'
ADAPTOR_PATH = 'C:/Users/bamla/Desktop/llm_proj/medical_annotation_tool/notebooks/medllm/checkpoint-379'


class TorchAnnotationModel:
    """
    TorchAnnotationModel class to annotate text extracts with factors from the taxonomy
    """

    def __init__(self, store, output_parser, few_shot_template, model_name=MODEL_NAME, adapter_path=ADAPTOR_PATH) -> None:

        self.store = store
        self.output_parser = output_parser
        self.few_shot_template = few_shot_template

        base_model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
            load_in_4bit=True,
            torch_dtype=torch.float16,
            device_map="auto",
        )

        self.model = PeftModel.from_pretrained(
            base_model,
            adapter_path,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
            load_in_4bit=True,
            device_map="auto",
        )

        # set the model to evaluation mode to disable dropout and batch normalization layers
        self.model.eval()

        self.tokenizer = AutoTokenizer.from_pretrained(
            adapter_path,
            trust_remote_code=True,
        )

        logging.info(
            f'TorchAnnotationModel initialized with model: {model_name}')

    def get_annotations(self, text_extract):
        """
        Get the annotations for a given text extract

        Args:
            text_extract (str): text extract to be annotated

        Return:
            str: string containing annotations
        """

        prompt = self.few_shot_template.format(
            text_extract=text_extract, taxonomy=self.store.get_taxonomy())
        
        print('prompt', prompt)

        input_ids = self.tokenizer.encode(
            prompt, return_tensors="pt").to('cuda')
        generation_output = self.model.generate(
            input_ids=input_ids,
            generation_config=GenerationConfig(
                # these params you'll have to tweak
                do_sample=True,
                temperature=0.3,
                top_p=0.9,
                num_beams=2,
            ),
            return_dict_in_generate=True,
            output_scores=True,
            max_new_tokens=150
        )
        output = self.tokenizer.decode(generation_output.sequences[0])[
            len(prompt):-4]

        return output

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
            output = self.output_parser.parse(annotated.replace("'", '"'))
            return output
        except Exception as e:
            return {'text_extract': text_extract, 'factors': ['Error parsing annotations']}


if __name__ == '__main__':
    import sys
    sys.path.insert(0,  '..')
    import store
    import inference

    TAXONOMY_FILE = '../constants/taxonomy.json'
    PROMPT_FILE = '../constants/prompt.txt'
    EXAMPLES_FILE = '../constants/examples.json'

    store_manager = store.Store(TAXONOMY_FILE, PROMPT_FILE, EXAMPLES_FILE)
    inference_manager = inference.Manager(store_manager)

    model = TorchAnnotationModel(store=store_manager, output_parser=inference_manager.output_parser,
                                 few_shot_template=inference_manager.few_shot_template)

    extract = 'This means that IA was not performed in line with local or national guidance.'

    output = model.get_parsed_annotations(extract)
    print('output', output)