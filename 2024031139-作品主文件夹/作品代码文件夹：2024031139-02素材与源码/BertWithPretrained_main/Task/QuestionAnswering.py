from transformers import BertForQuestionAnswering, BertTokenizer
import logging
import torch
import os

class ModelConfig:
    def __init__(self):
        self.project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.pretrained_model_dir = os.path.join(self.project_dir, "./hfl/chinese_roberta_wwm_large_ext_pytorch")
        self.text_file_path = os.path.join(self.project_dir, './data/context.txt')
        self.model_save_dir = os.path.join(self.project_dir, 'cache')
        self.logs_save_dir = os.path.join(self.project_dir, 'logs')
        self.model_save_path = os.path.join(self.model_save_dir, 'model.pt')
        self.device=torch.device('cpu')
        self.batch_size = 2
        self.max_query_len = 64
        self.doc_stride = 128
        self.epochs = 2

        self.model_val_per_epoch = 1
        logging.basicConfig(level=logging.DEBUG, filename='qa.log')
        self.log_file_path = os.path.join(self.logs_save_dir, 'wendaoutput.log')

 
    

if __name__ == '__main__':
    model_config = ModelConfig()
    config = model_config
    loaded_state_dict = torch.load('./cache/model.pt', map_location=torch.device('cpu'))    
    model = BertForQuestionAnswering.from_pretrained(config.pretrained_model_dir, state_dict=loaded_state_dict)
    tokenizer = BertTokenizer.from_pretrained(config.pretrained_model_dir)
     

    def answer_question(question, answer_text):
        '''
        Takes a `question` string and an `answer_text` string (which contains the
        answer), and identifies the words within the `answer_text` that are the
        answer. Prints them out.
        '''
        # ======== Tokenize ========
        # Apply the tokenizer to the input text, treating them as a text-pair.
        input_ids = tokenizer.encode(question, answer_text)

        # Report how long the input sequence is.
        print('Query has {:,} tokens.\n'.format(len(input_ids)))

        # ======== Set Segment IDs ========
        # Search the input_ids for the first instance of the `[SEP]` token.
        sep_index = input_ids.index(tokenizer.sep_token_id)

        # The number of segment A tokens includes the [SEP] token istelf.
        num_seg_a = sep_index + 1

        # The remainder are segment B.
        num_seg_b = len(input_ids) - num_seg_a

        # Construct the list of 0s and 1s.
        segment_ids = [0]*num_seg_a + [1]*num_seg_b

        # There should be a segment_id for every input token.
        assert len(segment_ids) == len(input_ids)

        # ======== Evaluate ========
        # Run our example question through the model.
        start_scores, end_scores = model(torch.tensor([input_ids]), # The tokens representing our input text.
                                        token_type_ids=torch.tensor([segment_ids]),return_dict = False) # The segment IDs to differentiate question from answer_text

        # ======== Reconstruct Answer ========
        # Find the tokens with the highest `start` and `end` scores.
        answer_start = torch.argmax(start_scores)
        answer_end = torch.argmax(end_scores)

        # Get the string versions of the input tokens.
        tokens = tokenizer.convert_ids_to_tokens(input_ids)

        # Start with the first token.
        answer = tokens[answer_start]

        # Select the remaining answer tokens and join them with whitespace.
        for i in range(answer_start + 1, answer_end + 1):
            
            # If it's a subword token, then recombine it with the previous token.
            if tokens[i][0:2] == '##':
                answer += tokens[i][2:]
            
            # Otherwise, add a space then the token.
            else:
                answer +=  tokens[i]


        print('question: "' + question + '"')


        print('Answer: "' + answer + '"')

    import textwrap
    # 配置日志记录
    logging.basicConfig(level=logging.INFO, filename=model_config.log_file_path, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

    # 禁止输出警告信息到控制台
    logging.getLogger("transformers").setLevel(logging.ERROR)
    # Wrap text to 80 characters.
    wrapper = textwrap.TextWrapper(width=80) 
    with open(model_config.text_file_path, 'r', encoding='utf-8') as file:
        text = file.read()

            

    print("=================================================")
    print(wrapper.fill(text))

    question = input("您的问题是什么: ")
    answer_question(question, text)