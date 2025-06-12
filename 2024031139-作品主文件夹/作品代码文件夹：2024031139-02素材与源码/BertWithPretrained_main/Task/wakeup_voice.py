# import sys
# sys.path.append('BertWithPretrained-main/Tasks')
# 用于通过串口与麦克风阵列通信
import sys
sys.path.append("web_classification")
from web_classification import app
import pyaudio
import wave
import serial
import json
import time
import os
import datetime
import hashlib
import base64
import hmac
from urllib.parse import urlencode
import ssl
from wsgiref.handlers import format_date_time
from time import mktime
import _thread as thread
import websocket
from Tasks import bert_qa

woshuo = b'\xa5\x01\x01\x04\x00\x00\x00\xa5\x00\x00\x00\xb0'
queren = b'\xA5\x01\xff\x04\x00\x00\x00\xA5\x00\x00\x00\xB2'

len_r = 0
data_list = []
buf = []
buf_flag = 0
first = 0

# 实现收音并生成音频文件
def record_audio(output_filename, duration=5, channels=1, sample_rate=16000, chunk=1024):
    """
    Record audio from the microphone and save it to a .pcm file.

    Args:
        output_filename (str): The name of the output .pcm file.
        duration (int): The duration of the recording in seconds (default is 5).
        channels (int): Number of audio channels (default is 1 for mono).
        sample_rate (int): Sample rate of the audio (default is 16000 Hz).
        chunk (int): The number of frames per buffer (default is 1024).
    """
    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    # Open the microphone stream
    stream = audio.open(format=pyaudio.paInt16,
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=chunk)

    print("Recording...")

    frames = []
    for _ in range(0, int(sample_rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    print("Recording finished.")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recorded audio to a .pcm file
    with wave.open(output_filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))

    print(f"Audio saved to {output_filename}")

def deal(data_list):
    global first
    str1 = str(data_list)

    f_data = str1.find('{')
    l_data = str1.rfind('}')
    str1 = str1[f_data:l_data + 1]

    str1 = str1.replace("\\", "")
    str1 = str1.replace("', b'", "")
    str1 = str1.replace('"{', "{")
    str1 = str1.replace('}"', "}")

    json_str = json.loads(str1)
    print("json_str: ", json_str)

    if 'code' in json_str and first == 0:
        sss = json_str['content']
        print(json_str['content'])
        first = 1
    else:
        angle = json_str['content']['info']['ivw']['angle']
        print("angle: ", angle)
        return angle


# asr
STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识


class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, AudioFile):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.AudioFile = AudioFile

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"domain": "iat", "language": "zh_cn", "accent": "mandarin", "vinfo": 1, "vad_eos": 10000}

    # 生成url
    def create_url(self):
        url = 'wss://ws-api.xfyun.cn/v2/iat'
        # 生成RFC1123格式的时间戳
        now = datetime.datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/iat " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # print('websocket url :', url)
        return url


# 收到websocket消息的处理
def on_message(ws, message):
    try:
        code = json.loads(message)["code"]
        sid = json.loads(message)["sid"]
        if code != 0:
            errMsg = json.loads(message)["message"]
            print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))

        else:
            data = json.loads(message)["data"]["result"]["ws"]
            # print(json.loads(message))
            result = ""
            for i in data:
                for w in i["cw"]:
                    result += w["w"]
            print("sid:%s call success!,data is:%s" % (sid, json.dumps(data, ensure_ascii=False)))
    except Exception as e:
        print("receive msg,but parse exception:", e)


# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws, a, b):
    print("### closed ###")


# 收到websocket连接建立的处理
def on_open(ws):
    def run(*args):
        frameSize = 8000  # 每一帧的音频大小
        intervel = 0.04  # 发送音频间隔(单位:s)
        status = STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧

        with open(wsParam.AudioFile, "rb") as fp:
            while True:
                buf = fp.read(frameSize)
                # 文件结束
                if not buf:
                    status = STATUS_LAST_FRAME
                # 第一帧处理
                # 发送第一帧音频，带business 参数
                # appid 必须带上，只需第一帧发送
                if status == STATUS_FIRST_FRAME:

                    d = {"common": wsParam.CommonArgs,
                         "business": wsParam.BusinessArgs,
                         "data": {"status": 0, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    d = json.dumps(d)
                    ws.send(d)
                    status = STATUS_CONTINUE_FRAME
                # 中间帧处理
                elif status == STATUS_CONTINUE_FRAME:
                    d = {"data": {"status": 1, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                # 最后一帧处理
                elif status == STATUS_LAST_FRAME:
                    d = {"data": {"status": 2, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                    time.sleep(1)
                    break
                # 模拟音频采样间隔
                time.sleep(intervel)
        ws.close()


# 麦克风连接的usb端口
# timeout这是终止时间，用以终止串口操作。程序就会持续读取timeout秒的时长来读取数据
ser = serial.Serial("/dev/ttyUSB0", 115200, 8, 'N', 1, timeout=5)
#print("Open the serial")

# 在线语音合成功能
def ass_process(text):
    time1 = datetime.datetime.now()
    ass_wsParam = Ws_Param(APPID='0cd15435165917', APISecret='NDIyMmU3NmVhMWU2YWI2NDc2MGYzNzI5',
                           APIKey='64a1f73b27af74206ba435a14e608fe7',
                           AudioFile=text)
    websocket.enableTrace(False)
    ass_wsUrl = ass_wsParam.create_url()
    ass_ws = websocket.WebSocketApp(ass_wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
    ass_ws.on_open = on_open
    ass_ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    time2 = datetime.datetime.now()
    print(time2 - time1)

# 在离线语音唤醒中设置的最长无语音时间
MAX_VOICE_TIMEOUT = 20
# 在线语音识别中设置的最长无语音输入时间
MAX_RECOGNITION_TIMEOUT = 10
# 记录上次接收到语音的时间
last_voice_time = 0
# 记录上次识别到语音的时间
last_recognition_time = 0
# 记录当前是否处于唤醒状态
is_awake = False

# 离线语音唤醒功能
def offline_wakeup():
    global last_voice_time, is_awake

    while True:
        if not is_awake:
            print("Offline wakeup is inactive.")
            time.sleep(1)
            continue

        if time.time() - last_voice_time > MAX_VOICE_TIMEOUT:
            print("No voice input for {} seconds. Going to sleep...".format(MAX_VOICE_TIMEOUT))
            is_awake = False
            break

        time.sleep(1)

# 在线语音识别功能
def asr_process(AudioFile):
    global last_recognition_time, is_awake

    while is_awake:
        if time.time() - last_recognition_time > MAX_RECOGNITION_TIMEOUT:
            print("No voice input for {} seconds during recognition. Exiting...".format(MAX_RECOGNITION_TIMEOUT))
            is_awake = False
            break
        time1 = datetime.datetime.now()
        wsParam = Ws_Param(APPID='0cd15435165917', APISecret='NDIyMmU3NmVhMWU2YWI2NDc2MGYzNzI5',
                           APIKey='64a1f73b27af74206ba435a14e608fe7',
                           AudioFile=AudioFile)
        websocket.enableTrace(False)
        wsUrl = wsParam.create_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
        ws.on_open = on_open
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        time2 = datetime.datetime.now()

        print("Checking for voice input during recognition...")
        time.sleep(1)
import datetime
try:
    while True:
        # serial.read_all()读取一个timeout周期内的全部数据(常用方法)
        # 平时串口通信中，最好使用read_all()方法，并选定合适的timeout
        rcv = ser.read_all()
        len_r = len(rcv)
        if rcv == woshuo:
            ser.write(queren)
        elif len_r > 1:
            buf.append(rcv)
            buf_flag = 1
        elif len_r < 1 and buf_flag == 1:
            buf_flag = 0
            data_list = buf
            buf = []
            angle_msg = deal(data_list)
            last_voice_time = time.time()

            # 从网页中导入测试及推荐结果
            level=app.grade()
            capter=app.text()
            first_answer="您好，我是您的学习助手小飞，您目前的评级为"+level+",您正在学习的课文为"+capter+",若在学习中遇到问题请随时问我，我随时在"
            print("----------------------------------------------------------------------------------------------------------------------------------")
            print("聆听中\n")
            # 调用在线语音合成功能
            thread.start_new_thread(ass_process, (first_answer,))

            end_time=datetime.datetime.now()

            while(True):
                start_time=datetime.datetime.now() #当前时间
                print("聆听中\n")
                if (start_time-end_time>20):  #设置监听20s
                    f=0
                    break
                #实现收音并存入音频文件
                output_filename = "recorded_audio.pcm"  #问题
                record_audio(output_filename, duration=5, channels=1, sample_rate=16000, chunk=1024)
                
                # 在线语音识别的线程启动 #从语音中识别出问题
                thread.start_new_thread(asr_process, (output_filename))
                with open('recognized_text.txt', 'r') as file:
                    content=file.read()
                question="question:"+content
                print(question) #输出问题
                time.sleep(1)  # 等待1秒，以确保识别结果已经写入文件 "recognized_text"

                dir1 = 'bookcapter.txt'  # 传入您需要的 dir1 参数
                model_config = bert_qa.ModelConfig(dir1)
                model, tokenizer = bert_qa.load_model_and_tokenizer(model_config)
                with open(model_config.text_file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
                question = content
                qa="question:"+question
                answer = bert_qa.answer_question(question, text, model, tokenizer)
                print('answer:', answer) #输出答案
                print("聆听中\n")

            # 从识别结果文件中读取内容并调用在线语音合成
                thread.start_new_thread(ass_process, (answer,))  #读答案
                end_time=datetime.datetime.now()

        time.sleep(0.1)
        ser.close()
finally:
    ser.close()
