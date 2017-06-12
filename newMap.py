#!usr/dev/evn python
#coding:utf-8
import requests
import time,random
import logging
logging.basicConfig(level=logging.INFO,filename='log.txt')
import traceback
import json
import csv
#data form to post for 'keyword' query of baidu

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Content-Type': 'text/plain',
}

#get time tag, then change its content
def timeTag():
    s=str(1491357535.632).split('.')
    b=list(s[0])#random min and hour
    b[-5:-2]=str(random.randrange(101,999))
    tag=''.join(b)+(s[1] if len( s[1]) ==3 else (s[1]+'3'))
    return tag

#obtain location by the name of city  
def getName():
    #prepare data for Location(method:get)
    query={
        'qt':'cur',
        'wd':'',
        't':'',
        'dtype':1
    }
    fname=open('city.txt','r')#list of city
    ctList=fname.readlines()
    unsolved=open('Unct.txt','ab')
    cityLoc=open('cityLoc.txt','ab')
    unsolved.write('以下城市名字错误，请确认'+'\n')
    length=len(ctList)
    newAppend=[]
    for i,name in enumerate(ctList):
        name=name.strip()
        query['wd']=name
        query['t']=timeTag()
        #logging.info( query)#1
        try:
            #s=requests.Session()
            r=requests.get('http://map.baidu.com',params=query, headers=headers)
            r.raise_for_status()
            #logging.info(r.request.url)#2
            response=json.loads(r.text)
        except:
            logging.info(traceback.print_exc())
            logging.info('+'*20+name+'+'*20)
            continue
        #logging.info(list(response.keys()))
        #logging.info(r.text)
        con=response.get('content') or []
        Dict={}
        Dict['name']=name
        if con:#下次考虑将各个城市的坐标记录下来
            Dict['b'] = con['geo'].split('|')[1].encode('utf-8')    #'(' +  + ')'
            Dict['l'] = con['level']
            Dict['c'] = con['code']
            #logging.info(Dict)#3
            text=getKey(Dict)
            #postKey(Dict,s)
            #保存这些城市相关信息
            cityLoc.write(name+' ' +Dict['b']+' ' +repr(Dict['l'])+' ' +repr(Dict['c'])+'\n')
            if text:
                ctList.append(text)
                newAppend.append(text)
        else:
            logging.info('--alert，返回值问题--Loc()'+name)
            logging.info(str(response.keys())+r.request.url)##新增语句
            unsolved.write(name+'\n')
        newAppend=list(set(newAppend))
        logging.info('-'*30) 
        if i>length+len(newAppend):
            logging.info('#'*50+'\n'+str(i))
            break
    #将没有相关属性的城市写入unsovled
    unsolved.write('以下城市没有湿地属性，请确认'+'\n') 
    for name in newAppend:
        unsolved.write(name+'\n')
    fname.close() 
    unsolved.close() 
    cityLoc.close()
#提交表单信息获取返回json            
def getKey(dict):
    query={
        'newmap':1,
        'reqflag':'pcmap',
        'biz':1,
        'from':'webmap',
        'da_par':'after_baidu',
        'pcevaname':'pc4.1',
        'qt':'spot',
        'from':'webmap',
        'c':'',
        'wd':'湿地',
        'wd2':'',
        'pn':0,
        'nn':0,
        'db':0,
        'sug':0,
        'addr':0,
        '':'',
        'da_src':'pcmappg.poi.page',
        'on_gel':1,
        'src':7,
        'gr':3,
        'l':'',
        'rn':50,
        'tn':'B_NORMAL_MAP',
        'u_loc':'12956722,4839945',
        'ie':'utf-8',
        'b':'12707929.29,3545221.28;12768089.29,3575429.28',
        't':'1491360789273'
    }
    query['b']=dict['b']
    query['l']=dict['l']
    query['c']=dict['c']
    query['t']=timeTag()
    try:
        r=requests.get('http://map.baidu.com',params=query, headers=headers)
        r.raise_for_status()
        response=json.loads(r.text)
    except:
        logging.info(traceback.print_exc())
        logging.info('-'*20+dict.get('name')+'-'*20)
        return dict.get('name')
    #logging.info(r.request.url)#4
    #logging.info(response.keys())#5
    try:
        con=response.get('content') or []
        with open('csvf.csv','ab') as fc:
            w=csv.writer(fc)
            w.writerow([dict.get('name')])
            for item in con:
                result={}
                try:
                    result['diTag']=(item.get('std_tag') or item.get('di_tag')).encode('utf-8')
                    result['name']=(item.get('name')).encode('utf-8')
                    result['pointX']=item.get('diPointX')/100.0#要注意是不是数位是一致的
                    result['ponitY']=item.get('diPointY')/100.0
                    result['area']=item.get('area')
                    
                    #fc.write(json.dumps(result,ensure_ascii=False))
                    #fc.write('\n')
                    w.writerow([result['name'],result['pointX'],result['ponitY'],result['area'],result['diTag']])
                except:
                    logging.info('属性问题'+dict.get('name'))
                    logging.info(item.keys())
        if not con:
            #fc.write('\n'+(dict.get('name')).encode('utf-8')+'\n\n')
            logging.info('info--出现错误，con为【】'+dict.get('name'))
            logging.info('keys of response'+str(response.keys()))##新增语句
            return dict.get('name')
    except:
        logging.info(traceback.print_exc())
        return dict.get('name')
    return 0
    
    
def postKey(dict,session):
    query={
        'newmap':1,
        'reqflag':'pcmap',
        'biz':1,
        'from':'webmap',
        'da_par':'after_baidu',
        'pcevaname':'pc4.1',
        'qt':'usync',
        'mode':'hsync',
        'subkey':'poihistory',
        't':''
    }
    t=timeTag()
    query['t']=t
    tForm=''.join(list(t)[:-3])
    form={"action":"add","detail":{"qt":"s","wd":"湿地","ctime":tForm,"platform":"3"},"ctime":tForm}
    logging.info(json.dumps(form))
    r=session.get('http://map.baidu.com',params=query, headers=headers)
    r.raise_for_status()
    #logging.info(r.request.url)#2
    response=json.loads(r.text)
    logging.info('--出现response为--')
    logging.info(json.dumps(response))
    
    
getName()


