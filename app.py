from flask import Flask, render_template
import sqlite3


app = Flask(__name__)


@app.route('/')     #路由解析
def index():    #首页
    return render_template("index.html")    #模板渲染

@app.route('/index')
def home():     #首页
    return render_template("index.html")

@app.route('/docu')
def docu():     #纪录片
    datalist = []
    con = sqlite3.connect('D:\pythonProject1\Rankings.db')  #连接数据库
    cur = con.cursor()
    sql = '''
        select *
        from rankings
        order by views desc 
    '''     #创建sql语句
    data = cur.execute(sql)
    for item in data:
        datalist.append(item)
    cur.close()
    con.close()
    return render_template("docu.html", docus = datalist)

@app.route('/score')
def score():     #评分
    scores = []
    num = []
    con = sqlite3.connect('D:\pythonProject1\Docu.db')      #连接数据库
    cur = con.cursor()
    sql = '''
            select rating, count(rating)
            from information
            group by rating
        '''     #创建sql语句
    data = cur.execute(sql)
    for item in data:
        if item[0] != '':
            scores.append(float(item[0]))
            num.append(item[1])
    cur.close()
    con.close()
    return render_template("score.html", scores = scores, num = num)

@app.route('/word')
def word():     #词云
    return render_template("word.html")


if __name__ == '__main__':
    app.run()
