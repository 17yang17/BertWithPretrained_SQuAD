素材与源码README
'''
BertWithPretrained_main			#问答模型模块
|----SQuAD			#数据集
|	|----medicine_data.json			#中医问答数据
|	|----train_medicine_data.json			#中医数据训练集
|	|----test_medicine_data.json			#中医数据测试集
|	|----cleaned1_hsk2.json			#hsk+理解中国训练数据
|	|----cleaned_under.json			#理解中国测试数据

|----Tasks			#模型训练
|	|----_init_.py	
|	|----TaskForSQuADQuestionAnswering.py			#使用中医数据集预训练模型
|	|----TaskForSQuADQuestionAnswering1.py			#使用中文问答数据集微调模型代码
|	|----TestForSQuADQuestionAnswering.py		#模型测试代码
|	|----QuestionAnswering.py			#实现问答功能
|	|----wakeup_voice.py			#连接语音-模型-网页模块，实现完整功能
#封装问答模块
|	|----setup_paths.py			#将模块目录路径添加到环境变量中
|	|----qua.py			#调用模块

|----cache			#保存模型
|	|----model.pt			#模型参数

|----hfl/chinese_roberta_wwm_large_ext_pytorch			#BERT模型
|	|----config.json
|	|----pytorch_model.bin
|	|----vocab.txt

|----Web_Classification			#线上评级模块		
|----.idea
|----src
|----templates
|----app.py			#网页代码
'''