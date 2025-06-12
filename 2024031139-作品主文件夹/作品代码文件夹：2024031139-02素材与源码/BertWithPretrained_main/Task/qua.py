# import sys
# sys.path.append('BertWithPretrained-main/Tasks')

from Tasks import bert_qa
if __name__=="__main__":
    dir1 = './data/context.txt'  # 传入您需要的 dir1 参数
    model_config = bert_qa.ModelConfig(dir1)
    model, tokenizer = bert_qa.load_model_and_tokenizer(model_config)
    with open(model_config.text_file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    print("=================================================")
    print(text)
    question = input("您的问题是什么: ")
    answer = bert_qa.answer_question(question, text, model, tokenizer)
    print('Answer:', answer)
