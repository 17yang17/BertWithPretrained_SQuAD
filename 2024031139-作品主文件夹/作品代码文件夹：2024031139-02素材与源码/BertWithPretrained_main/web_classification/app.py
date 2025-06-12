# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, flash, session
app = Flask(__name__)
# 密钥（secret key）用于保护会话数据安全，并加密数据。没有设置密钥会导致会话无法正常工作。
app.secret_key = 'your_secret_key_here'

# 假设的用户信息，实际开发中应使用数据库
users = {"123": "456"}
grade=""
text=""

# 假设每个问题的分值为1分，正确答案如下
QUESTION_WEIGHTS = {
    'set1_question1': 1, 'set1_question2': 1, 'set1_question3': 1,
    'set2_question1': 3, 'set2_question2': 3, 'set2_question3': 3,
    'set3_question1': 5, 'set3_question2': 5, 'set3_question3': 5
}

CORRECT_ANSWERS = {
    'set1_question1': '7个以上', 'set1_question2': '8', 'set1_question3': '3',
    'set2_question1': '3', 'set2_question2': '菊花', 'set2_question3': '行贿',
    'set3_question1': '他坚持固守了中国艺术精神、并将其推向了极致',
    'set3_question2': '诚哉格里才斯言', 'set3_question3': '书画同源、诗书画印的融为一体'
}


docs = [
    [
        "金太成：李老师，下个月我要参加HSK考试。",
        "李冬生：准备好了吗？",
        "金太成：还可以吧，但是我想考七级以上。",
        "李冬生：你平时学习很努力，应该没问题。",
        "金太成：老师，您还是给我辅导辅导吧。",
        "李冬生：怎么辅导？",
        "金太成：一个星期辅导四次，一次两个小时。",
        "李冬生：这么多次？那你得找三个辅导老师。"

    ],
    [
        "每个国家、民族的文化传统千差万别，不同的国家、民族具有不同的风俗习惯。",
        "在当今日益频繁的国际交往中，我们每到一地，都应该特别留意这一点。",
        "在印度尼西亚，具有良好教养的人在彼此相识之时，应马上把自己的名片递给对方。",
        "如果不送名片，那将难免受到对方长时间的冷遇。",
        "在日本，你每天得准备递送40张名片。",
        "在法国，礼节要求你将自己的身份列在名片上。",
        "在丹麦，一位被邀请到朋友家做客的人应带上鲜花或者一些有趣的精美礼品。",
        "在德国，如果你应邀做客，那么鲜花也是送给女主人的最好礼物，但不能送玫瑰花，他们认为玫瑰花只能送给情人。",
        "而在瑞士，你可以送1束，也可以送20束红玫瑰给你的生意朋友，只要花的数目不是“3”就行；如果花的数目是“3”，则意味着你们是情人。",
        "在法国，人们总是在拜访或参加晚宴的前夕送鲜花给主人。",
        "不过，在法国千万别送菊花——除非你是去参加朋友的葬礼。",
        "在日本，有些参加晚宴的宾客可能会提前离席而去，而且离席时一般都是静悄悄的，不做正式的告别。",
        "因为在这种场合做正式告别，会被视为扰乱宴会气氛，打扰其他在场的宾客。",
        "阿拉伯国家的人初次见面，不能送礼，否则会被视为行贿，还忌讳将酒作为礼物送人；人们见面时，还不能问及家人。",
        "美洲国家的人忌讳黑色和紫色，因为它们暗示结束友谊；人们还忌讳用手帕作为礼物送人，因为它常常和眼泪连在一起，因此被看成不祥之物。"
    ],
    [
        "格里斯认为齐白石不仅是中国的伟大画家，也是世界的伟大画家，齐白石把全身心都投入到自然中去了，没有人比齐白石对自然的了解和感情更深。老人对我们说，齐白石是独一无二的，齐白石画虾，便对虾的结构和神态作了最为细致深入的研究，那种简洁有力的神奇画法，全世界都找不到。格里才老人是一个大自然的卓越歌手，我以前从旧书旧杂志上看到过不少关于他的介绍。",
        "他在1950~1952年期间创作的风景画《伏尔加河远眺》，具有极完美的写实技巧，充满了浓郁的诗意。这样个希施金和列维坦的传人，却如此推尝齐白石的绘画，真有点儿让我大惑不解。",
        "我问老人是否可以去中国教学，老人听了却把头摇得像个拨浪鼓。",
        "他认真地说;'我为什么要去教中国的画家?中国有自己的艺术和文化传统，我希望中国能够珍惜和保护自已的艺术和文化传统。'他还说有一种理论认为各民族的文化应互相融合，而他则认为各民族应该保持自己文化的独立、艺术的独立。老人甚至对我们大老远地跑来俄罗斯学习作画感到不以为然。",
        "他认为中国人对自然界的一草一木、花鸟虫鱼都有极为独特的感受，中国画的结构也很棒，形式感很强。老人说他不是要固执地保护俄罗斯的文化，而是不希望看到全世界的艺术趋向同一。老人指着墙上挂着的齐白石的作品说，从这些作品中可以进入中国的文化和思想。我不得不承认老人的话很有道理。那是一种艺术上和文化上的'远眺'。我终于明白了齐白石为什么能够成为一代大师，也明白了其他众多画虾能手的画中到底少了些什么。所谓中国绘画从传统形态向现代形态的转变云云，是困扰了中国美术家将近一个世纪的难题。本世纪以来，不少前辈艺术家引进西方写实绘画技法以'刷新'中国绘画，其付出的努力的确令人钦敬，但取得的成就却令人怀疑。",
        "齐白石之所以成为中国乃至世界的艺术巨匠，与其认为他受到了西方强势文化的影响，努力实现所谓从传统向现代的转变，还不如说他坚持固守了中国艺术精神、并将其推向了极致更为恰当。",
        "据我的理解，书画同源、诗书画印的融为一体，是中国画区别于西方绘画的根本所在，亦是中国画中的中国艺术精神之根本体现。",
        "从齐白石的毕生艺术追求及其所取得的伟大成就来看，艺术创作中的求新求变，并不意味着一定要吸收和融入异域文化的成分，'借复旧以趋新'有时也不失为一条创造的途径。",
        "唐代的古文运动以及晚清的碑学复兴，意大利文艺复兴时期古希腊雕刻的出土，都曾极大地推动了当时文学或艺术的创新。从书画同源的观点和角度来考察齐白石的艺术，能够比较准确地把握其艺术创作的根本特点。齐白石甚至在进行艺术鉴赏时，亦用了“书”来作为评“画”的标准，如他曾说李可染的画是画中草书，徐青藤的画也是草书，而他自己的画则是正楷。",
        "或有对齐白石'诗第一，印第二，字第三，画第四'的自我评价不以为然者，但也有论者认为这样的评价不无道理，认为齐白石整体艺术创作中的最大成就即在于诗歌艺术上的。",
        "不论各家观点如何纷争，诗书画印都是齐白石艺术创作成就中不可分割的部分，它们相互影响，相互交融，早已成为一个整体，这是已为学界所公认了的。",
        "这样的整体当然完美地体现出了中国艺术的精神。",
        "从这里当然也就'可以进入中国的文化和思想'。",
        "诚哉格里才斯言。"
    ]
]


# 定义路由
@app.route('/')
def index():
    """登录界面"""
    return render_template('login.html')  # 使用render_template函数渲染


@app.route('/login', methods=['POST'])
def login():
    """登录处理
    处理用户登录请求，通过request.form获取用户名和密码，
    如果用户名和密码匹配成功则重定向到'/quiz'路由，否则重定向回登录界面。"""
    username = request.form['username']
    password = request.form['password']
    if username in users and users[username] == password:
        session['username'] = username  # 将用户名添加到会话中
        return redirect(url_for('student', username=username))  # 将用户名作为参数传递给student路由
        # return redirect(url_for('quiz'))
    else:
        flash('用户名或密码错误')  # 显示错误消息
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users:
            flash('用户名已存在，请选择其他用户名')
        else:
            users[username] = password
            flash('注册成功，请登录')
            return redirect(url_for('index'))  # 在注册成功后重定向到登录页面

    return render_template('register.html')


@app.route('/student')
def student():
    """学生页面"""
    # 在这里将username作为参数传递给模板
    username = request.args.get('username',  'Guest')
    return render_template('student.html', username=username)

# 用户提交的问题和选项
user_questions = {}
user_options = {}

@app.route('/quiz')
def quiz():
    """答题页面"""
    questions = {
        'set1_question1': '金同学的hsk考试的目标可能是什么?',
        'set1_question2': '金同学一个星期要辅导几个小时?',
        'set1_question3': '李东生建议金同学找几个老师？',
        'set2_question1': '瑞士送朋友花的时候数字里面不能有什么?',
        'set2_question2': '法国不能送什么花?',
        'set2_question3': '为什么在阿拉伯国家初次见面不能送礼？，这代表什么',
        'set3_question1': '问什么说齐白石可以成为中国乃至世界的艺术巨匠？',
        'set3_question2': '哪一句可以看到作者认同格里斯的话?',
        'set3_question3': '格里斯认为，中国的画区别于西方的根本是什么？'
    }

    options = {
        'set1_question1': ['3', '6', '7个以上'],
        'set1_question2': ['3', '8', '9'],
        'set1_question3': ['3', '2', '1'],
        'set2_question1': ['3', '6', '11'],
        'set2_question2': ['玫瑰', '菊花', '向日葵'],
        'set2_question3': ['不尊重', '嘲笑', '行贿'],
        'set3_question1': ['他坚持固守了中国艺术精神、并将其推向了极致', '他勇于创新，坚持不懈', '齐白石整体艺术创作中的最大成就即在于诗歌艺术上'],
        'set3_question2': ['完美地体现出了中国艺术的精神', '诚哉格里才斯言', '借复旧以趋新'],
        'set3_question3': ['书画同源、诗书画印的融为一体', '可以进入中国的文化和思想', '国绘画从传统形态向现代形态转变']
    }

    return render_template('quiz.html', questions=questions, options=options, docs=docs)


@app.route('/submit', methods=['POST'])
def submit():
    # 获取表单数据
    # 获取表单数据
    total_score = 0
    results = {}

    for question, correct_answer in CORRECT_ANSWERS.items():
        user_answer = request.form.get(question)
        if user_answer == correct_answer:
            total_score += QUESTION_WEIGHTS[question]
            results[question] = 'Correct'
        else:
            results[question] = 'Incorrect'

    # 根据总分计算等级
    grade = '初等' if (0 <= total_score <= 9) else ('中等' if 9 < total_score <= 18 else '高等')
    text = '初级阅读材料' if (0 <= total_score <= 9) else ('中级阅读材料' if 9 < total_score <= 18 else '高级阅读材料')

    return render_template('result.html', docs=docs, total_score=total_score, grade=grade, text=text, results=results, CORRECT_ANSWERS=CORRECT_ANSWERS)


# @app.route('/teacher')
# def teacher_index():
#     """教师主页"""
#     return render_template('teacher_index.html')

def grade():
    return grade

def text():
    return text

if __name__ == '__main__':
    app.run(debug=True)