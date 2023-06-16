import jieba    #分词
from matplotlib import pyplot as plt     #绘图，数据可视化
from wordcloud import WordCloud         #词云
from PIL import Image                   #图片处理
import numpy as np                     #矩阵运算
import sqlite3                          #数据库

con = sqlite3.connect("D:/pythonProject1/Rankings.db")
cur = con.cursor()
sql = 'select title from rankings'
data = cur.execute(sql)
text = ""
for item in data:
    text = text + item[0]
cur.close()
con.close()

cut = jieba.cut(text)   #分词
string = ' '.join(cut)

img = Image.open(r'D:\flaskProject1\static\assert\images\bird.png')     #打开遮罩图片
img_array = np.array(img)   #将图片处理成数组
wc = WordCloud(
    background_color= 'white',
    mask= img_array,
    font_path='STKAITI.TTF'
)   #创建词云对象
wc.generate_from_text(string)   #将分好的词放入词云对象中

#绘制图片
fig = plt.figure(1)     #找到第一个位置进行绘制
plt.imshow(wc)  #按照wc规则显示
plt.axis('off')     #不显示横纵坐标

plt.savefig(r'D:\flaskProject1\static\assert\images\word.jpg', dpi = 500)   #保存图片