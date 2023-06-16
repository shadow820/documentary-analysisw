import urllib.request, urllib.error #制定url 获取网页数据
import xlwt #进行Excel操作
import sqlite3 #进行SQLite数据库操作
import json

def main():
    rankings_url = "https://api.bilibili.com/pgc/season/rank/web/list?day=3&season_type=3" #排行榜URL
    documentary_url = "https://api.bilibili.com/pgc/web/season/section?season_id=" #每部纪录片的基础URL
    info_url = "https://api.bilibili.com/pgc/view/web/season?ep_id="   #获取纪录片信息的基础URL
    episode_url = "https://api.bilibili.com/pgc/season/episode/web/info?ep_id=" #纪录片每集的基础URL
    rankings_sql = '''
        create table rankings(
        title text ,
        id numeric primary key ,
        epinum text,
        img text,
        rank numeric ,
        views numeric ,
        rating text ,
        link text
        )
    '''
    docu_sql = '''
        create table information(
        title text primary key,
        areaid numeric,
        areaname text,
        type text,
        ratingnum numeric ,
        rating text ,
        views numeric ,
        coins numeric ,
        dms numeric ,
        favorites numeric ,
        likes numeric ,
        replies numeric ,
        shares numeric 
        )
    '''
    episodes_sql = '''
        create table episodes(
        id numeric primary key,
        ep_id numeric,
        ep_coin numeric ,
        ep_dm numeric ,
        ep_like numeric ,
        ep_reply numeric ,
        ep_share numeric 
        )
    '''
    #爬取排行榜网页
    rankings_list = getRankingsData(rankings_url)   #得到列表
    # print(rankings_list)
    #爬取纪录片id
    season_ids = getId(rankings_list)   #得到列表
    #爬取集数id
    ep_ids = getEpisodeId(documentary_url, season_ids) #得到字典， 键：纪录片id 值：纪录片每集对应的ep_id
    #爬取记录片详细信息
    info_list = getDocuData(info_url, ep_ids)   #得到列表
    # print(info_list)
    #爬取纪录片每集的信息
    episode_info = getEpisodesData(episode_url, ep_ids)     #得到字典， 键：纪录片id 值：对应每集信息的列表
    # print(episode_info)
    # 保存排行榜数据
    rankings_savepath = ".\\B站纪录片排行榜.xls"
    saveRankingsData(rankings_list,rankings_savepath)
    # 保存排行榜数据
    docu_savepath = ".\\B站纪录片详细信息.xls"
    saveDocuData(info_list, docu_savepath)
    #保存每集的信息
    episodes_savepath = ".\\B站纪录片每集信息.xls"
    saveEpiData(episode_info, season_ids, episodes_savepath)
    # #保存排行榜信息到数据库中
    rankings_dbpath = "Rankings.db"
    saveRankingsDB(rankings_list, rankings_sql, rankings_dbpath)
    #保存纪录片详细信息到数据库中
    docu_dbpath = "Docu.db"
    saveDocuDB(info_list, docu_sql, docu_dbpath)
    #保存纪录片每集的信息到数据库中
    episodes_dbpath = "Episodes.db"
    saveEpisodesDB(episode_info, episodes_sql, episodes_dbpath)



#爬取排行榜网页
def getRankingsData(baseurl):
    datalist = []

    print('正在爬取排行榜......')
    con = askURL(baseurl)
    d_json = json.loads(con)
    info_list = d_json['data']['list'] #获取信息列表
    for item in info_list:
        data = []  #保存每一步纪录片信息

        title = item.get('title') #纪录片标题
        data.append(title)

        id = item.get('season_id') #纪录片id
        data.append(id)

        epinum = item.get('desc')   #记录片集数
        data.append(epinum)

        img = item.get('cover') #纪录片图片
        data.append(img)

        rank = item.get('rank')  #纪录片排名
        data.append(rank)

        view = item.get('stat').get('view')  #纪录片播放量
        data.append(view)

        rating = item.get('rating')  #纪录片评分
        data.append(rating)

        url = item.get('url')  #纪录片访问链接
        data.append(url)

        datalist.append(data) #将处理好的纪录片信息放入datalist
    print('爬取排行榜成功!')
    return datalist

#得到season_id
def getId(rlist):
    id = []
    print('正在爬取纪录片的season_id......')
    for item in rlist:
        id.append(item[1])  #id保存在排行榜的第二个位置
    print('爬取season_id成功!')
    return id

#得到纪录片的每一集id, ep_id
def getEpisodeId(baseurl, ids):
    ep_id = {}      #保存每部纪录片对应的集数id

    print('正在爬取纪录片的ep_id......')
    for id in ids:
        url = baseurl + str(id)     #爬取的URL
        info = askURL(url)
        d_info = json.loads(info)   #得到信息的字典

        if 'main_section' not in d_info['result'].keys(): #有些纪录片暂时未更新正片
           ep_id.setdefault(id, [])
        else:
            episodes_list = d_info['result']['main_section']['episodes']    #得到纪录片中每一集的信息
            eid = []    #保存每部纪录片对应的所有集数id
            for i in episodes_list:
                eid.append(i.get('id'))     #获取id
                ep_id.setdefault(id, eid)
    print('爬取ep_id成功!')
    return ep_id

#得到纪录片的详细信息
def getDocuData(baseurl, epids):
    infolist = []

    print('正在爬取记录片详细信息中......')
    for k in epids.keys():
        value = epids.get(k)    #得到集数id用于URL
        data = []  # 保存一部纪录片的详细信息

        if len(value) != 0:
            url = baseurl + str(value[0])     #得到详细信息的URL
        else:
            url = baseurl + str(742688)
        info = askURL(url)
        d_info = json.loads(info)
        datalist = d_info['result']     #得到详细信息列表

        title = datalist.get('season_title')    #得到纪录片名称
        data.append(title)

        area_id = datalist.get('areas')[0].get('id')  #得到地区id
        data.append(area_id)

        area_name = datalist.get('areas')[0].get('name')  #得到地区名称
        data.append(area_name)

        styles = datalist.get('styles')     #得到题材
        data.append(styles)
        if datalist.get('rating') != None:
            ratingnum = datalist.get('rating').get('count')  #得到评分人数
            data.append(ratingnum)

            rating = datalist.get('rating').get('score')  #得到评分
            data.append(rating)
        else:
            data.append('')
            data.append('')

        view = datalist.get('stat').get('views')    #得到播放量
        data.append(view)

        coins = datalist.get('stat').get('coins')   #得到投币量
        data.append(coins)

        danmakus = datalist.get('stat').get('danmakus')     #得到弹幕量
        data.append(danmakus)

        favorites = datalist.get('stat').get('favorites')   #得到追剧量
        data.append(favorites)

        likes = datalist.get('stat').get('likes')   #得到点赞量
        data.append(likes)

        replies = datalist.get('stat').get('reply')     #得到评论数
        data.append(replies)

        shares = datalist.get('stat').get('share')  #得到转发量
        data.append(shares)

        infolist.append(data)   #保存记录片的所有详细信息

    print('爬取记录片详细信息成功！')
    return infolist

#得到纪录片每集的信息
def getEpisodesData(baseurl, epids):
    dict = {}

    print('正在爬取纪录片每一集的信息中......')
    for k in epids.keys():
        value = epids.get(k)    #ep_id的列表
        dlist = []
        for v in value:
            data = []   #保存一部纪录片中每集的信息
            url = baseurl + str(v)  #得到每集信息的URL
            data.append(v) #每集的ep_id
            info = askURL(url)
            d_info = json.loads(info)
            datalist = d_info['data']['stat']   #得到信息的列表

            coins = datalist.get('coin')    #每集投币量
            data.append(coins)

            dms = datalist.get('dm')    #每集弹幕量
            data.append(dms)

            likes = datalist.get('like')    #每集的点赞量
            data.append(likes)

            replies = datalist.get('reply')     #每集的评论数
            data.append(replies)

            views = datalist.get('view')    #每集的播放量
            data.append(views)

            dlist.append(data)  # 保存一部纪录片集的信息
        dict.setdefault(k, dlist)   #保存纪录片id与每集信息的对应关系
    return dict


# 保存排行榜数据
def saveRankingsData(rlist,path):
    print('正在保存排行榜数据中......')
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)     #创建workbook对象
    sheet = book.add_sheet('B站纪录片排行榜', cell_overwrite_ok=True)  #创建工作表
    col = ("标题", "id", "集数", "图片", "排名", "播放量", "评分", "访问链接")   #创建列名
    for i in range(0, 8):
        sheet.write(0, i, col[i])   #写入列标题
    for i in range(0, 100):
        print('第%d条' %(i+1))
        data = rlist[i]     #取其中一部纪录片
        print(data)
        for j in range(0, 8):
            sheet.write(i+1, j, data[j])    #写入信息
    book.save('B站纪录片排行榜.xls')   #保存到Excel表

#保存纪录片详细信息
def saveDocuData(list,path):
    print('正在保存纪录片详细数据中......')
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)     #创建workbook对象
    sheet = book.add_sheet('B站纪录片详细信息', cell_overwrite_ok=True)     #创建工作表
    col = ("名称", "地区id", "地区名称", "题材", "评分人数", "评分", "播放量",  "投币量", "弹幕量", "追剧量", "点赞量", "评论数", "转发量")  #创建列名
    for i in range(0, 13):
        sheet.write(0, i, col[i])   #写入列标题
    for i in range(0, 100):
        print('第%d条' %(i+1))

        data = list[i]  #取其中一部纪录片
        print(data)
        for j in range(0, 13):
            sheet.write(i+1, j, data[j])    #写入详细信息
    book.save('B站纪录片详细信息.xls')  #保存到Excel表

#保存纪录片每集的信息
def saveEpiData(einfo, seasonids, path):
    print('正在保存纪录片每集数据中......')
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)  # 创建workbook对象
    sheet = book.add_sheet('B站纪录片每集信息', cell_overwrite_ok=True)  # 创建工作表
    col = ("纪录片id", "ep_id",  "投币量", "弹幕量", "点赞量", "评论数", "播放量")    #创建列名
    coordinates = 1     #行坐标
    for i in range(0, 7):
        sheet.write(0, i, col[i])   #写入列标题
    for i in range(0, 100):
        print("第%d条" %(i+1))

        data = einfo.get(seasonids[i])  #取其中一部纪录片
        print(data)
        sheet.write(coordinates, 0, seasonids[i])   #写入纪录片id
        for j in range(0, len(data)):
            edata = data[j]
            for k in range(1, 7):
                sheet.write(coordinates, k, edata[k - 1])   #写入每集的信息
            coordinates += 1
    book.save('B站纪录片每集信息.xls')  #保存到Excel表

#保存排行榜信息到数据库中
def saveRankingsDB(datalist, initsql, dbpath):
    init_db(initsql, dbpath)    #创建Rankings数据库
    conn = sqlite3.connect(dbpath)  #连接数据库
    cur = conn.cursor()     #创建游标

    print("正在保存排行榜数据到数据库中......")
    for data in datalist:   #取出一部纪录片的信息
        for index in range(len(data)):
            if type(data[index]) == str:
                data[index] = '"' + data[index] + '"'   #对相应的字符串加上引号
            else:
                continue    #其他类型不加引号
        sql = '''insert into rankings(title, id, epinum, img, rank, views, rating, link)values(%s)'''%','.join('%s'%id for id in data)  #创建插入语句
        print(sql)  #打印sql语句
        cur.execute(sql)    #执行sql语句
        conn.commit()       #提交到数据库中
    cur.close()     #关闭游标
    conn.close()    #关闭与数据库的连接
    print("数据库保存成功！")

#保存纪录片详细信息到数据库中
def saveDocuDB(datalist, initsql, dbpath):
    init_db(initsql, dbpath)  # 创建Docu数据库
    conn = sqlite3.connect(dbpath)  # 连接数据库
    cur = conn.cursor()  # 创建游标

    print("正在保存纪录片详细数据到数据库中......")
    for data in datalist:  # 取出一部纪录片的信息
        for index in range(len(data)):
            if type(data[index]) == str:
                data[index] = '"' + data[index] + '"'  # 对相应的字符串加上引号
            if index == 3:  #对列表的处理
                tmp = ""
                for d in data[index]:
                    tmp += d
                data[index] = '"' + tmp + '"'
            else:
                continue  # 其他类型不加引号
        sql = '''insert into information(title, areaid, areaname, type, ratingnum, rating, views, coins, dms, favorites, likes, replies, shares)
                    values(%s)''' % ','.join('%s' % id for id in data)  # 创建插入语句
        print(sql)  # 打印sql语句
        cur.execute(sql)  # 执行sql语句
        conn.commit()  # 提交到数据库中
    cur.close()  # 关闭游标
    conn.close()  # 关闭与数据库的连接
    print("数据库保存成功！")

#保存纪录片每集的信息到数据库中
def saveEpisodesDB(datadict, initsql, dbpath):
    init_db(initsql, dbpath)    #创建Episodes数据库
    conn = sqlite3.connect(dbpath)  #连接数据库
    cur = conn.cursor()     #创建游标

    print("正在保存纪录片每集数据到数据库中......")
    for k in datadict.keys():   #取出一部纪录片的信息
        datalist = datadict.get(k)
        for data in datalist:
            sql = '''insert into episodes(ep_id, ep_coin, ep_dm, ep_like, ep_reply, ep_share)values({})'''.format(','.join('%s'%id for id in data))  #创建插入语句
            print(sql)  #打印sql语句
            cur.execute(sql)    #执行sql语句
            conn.commit()       #提交到数据库中
    cur.close()     #关闭游标
    conn.close()    #关闭与数据库的连接
    print("数据库保存成功！")

#创建数据库
def init_db(sql, dbpath):
    print("正在创建数据库......")
    conn = sqlite3.connect(dbpath)  #链接数据库
    cursor = conn.cursor()  #创建游标
    cursor.execute(sql)     #执行sql语句
    conn.commit()   #提交操作
    conn.close()    #关闭
    print("创建数据库成功！")


#得到一个指定URL的网页内容
def askURL(url):
    head = {
        'user-agent': 'Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 113.0.0.0Safari / 537.36Edg / 113.0.1774.57'
    }
    print(url, '正在请求URL中......')
    request = urllib.request.Request(url, headers= head) #模仿浏览器向服务器发送请求
    jsoninfo = ""

    try:
        response = urllib.request.urlopen(request) #服务器响应
        jsoninfo = response.read().decode("utf-8") #对响应进行解码
    except urllib.error.URLError as e: #异常处理
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    print('请求成功!')
    return jsoninfo

if __name__ == '__main__':
    main()