#find potential websites that have problems
from bs4 import BeautifulSoup, SoupStrainer, Comment
from selenium import webdriver
import requests
import urllib.request
import sys
import csv
import re
import pandas as pd
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from datetime import date,timedelta,datetime

today = (datetime.now() - timedelta(days = 1 )).date()

driver_path = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
chrome_options = Options()
chrome_options.add_argument("--headless")
# chrome_options.headless = True # also works
browser = webdriver.Chrome(driver_path,options=chrome_options)
data = urllib.request.urlopen('https://www.shakeout.org')
soup = BeautifulSoup(data,'html.parser')
cenList=[]
dictFind={}
catSpecific={}
for lister in soup.findAll("ul", {"id": "region_list"}):
    for link in lister.findAll("a"):
        url = link.get('href')
        cenList.append(url.split('/')[-2])
print(len(cenList))
cols = ["Individuals/Families","individuals","Childcare and Pre-Schools","K-12 Schools and Districts","Colleges and Universities","Local Government","State Government","Federal/National Government (Including Military)","Tribes/Indigenous Peoples","Businesses","Hotels and Other Lodgings","Healthcare","Senior Facilities/Communities","Disability/AFN Organizations","Non-Profit Organizations","Neighborhood Groups","Preparedness Organizations","Faith-based Organizations","Museums, Libraries, Parks, etc.","Volunteer/Service Clubs,Youth Organizations","Animal Shelter/Service Providers","Agriculture/Livestock Sector","Volunteer Radio Groups","Science/Engineering Organizations","Media Organizations","Other",'date'] # list of categories
dictionaryReturn = {}
california={}
for region in cenList:
    browser.get('https://www.shakeout.org/'+region+'/participants.php?start=All')
    html = browser.page_source
    soup = BeautifulSoup(html,'html.parser')
    comments = soup.findAll(text=lambda text:isinstance(text, Comment))
    [comment.extract() for comment in comments]
    table = soup.findAll("tr")
    if region == 'www.shakeoutbc.ca':
        print(table)
    colUnused = cols[:]
    for row in table:
        tmp_list = []
        for item in row.findAll("td"):
            tmp_list.append(item.getText())
        try:
            if len(tmp_list) > 1 and tmp_list[0] in cols:
                dictionaryReturn[tmp_list[0]].append(tmp_list[1])
                catSpecific[region][tmp_list[0]]=tmp_list[1]
                dictFind[region][tmp_list[0]]=tmp_list[1]
                colUnused.remove(tmp_list[0])
            elif len(tmp_list_ > 1) and tmp_list[0] not in cols:
                pass
                #california[region][tmp_list[0]]=tmp_list[1]
            else:
                dictFind[region][tmp_list[0]]=tmp_list[1]
                if region == 'california' or region=='California':
                    california[region][tmp_list[0]]=tmp_list[1]
        except:
            try:
                if len(tmp_list) > 1 and tmp_list[0] in cols:
                    dictionaryReturn[tmp_list[0]]=[tmp_list[1]]
                    catSpecific[region]={tmp_list[0]:tmp_list[1]}
                    dictFind[region]={row:tmp_list[1]}
                    #colUnused.remove(tmp_list[0])
                elif len(tmp_list) > 1 and tmp_list[0] not in cols:
                    pass
                    #california[region]={tmp_list[0]:tmp_list[1]}
                else:
                    if region == 'california' or region=='California':
                        california[region]={row:tmp_list[1]}
                    dictFind[region]={row:tmp_list[1]}
            except:
                pass
    try:
        if len(table) > 1:
            for cat in colUnused:
                try:
                    dictionaryReturn[cat].append(0)
                except:
                    dictionaryReturn[cat]=[]
            dictionaryReturn['date'].append('2022-05-12')
            dictionaryReturn['region'].append(region)
            print('appended',region)
    except:
        if len(table) > 1:
            for cat in colUnused:
                try:
                    dictionaryReturn[cat].append(0)
                except:
                    dictionaryReturn[cat]=[]
            dictionaryReturn['date']=['2022-05-12']
            dictionaryReturn['region']=[region]
my_data = dict([ (k,pd.Series(v)) for k,v in dictionaryReturn.items() ])
df = pd.DataFrame(my_data)
retStr = df.to_csv(index=False)
r=open('testStat.csv','w',encoding="utf-8")
r.write(retStr)
r.close()
retStr = 'state,category,number,date'
csvList = ['state','category','number','date']
toWriteAg=True
toWriteCo=True
toWriteCa=True
try:
    with open('outputData-aggreg.csv','r') as reader:
        if retStr in reader:
            toWriteAg = False
except:
    pass
try:
    with open('outputData-california.csv','r') as reader:
        if retStr in reader:
            toWriteCa = False
except:
    pass
try:
    with open('outputData-commons.csv','r') as reader:
        if retStr in reader:
            toWriteCo = False
except:
    pass
with open('outputData-california.csv', 'a+') as csv_file:
    csvwriter = csv.writer(csv_file, delimiter=',')
    if toWriteCa:
        csvwriter.writerow(csvList)
    for session in california:
        #csvwriter.writerow([session] + list(dictFind[session].keys()))
        for item in california[session]:
            if 'individuals' in item:
                csvwriter.writerow([session, 'Individuals/Families', california[session][item],today])
            else:
                csvwriter.writerow([session, item, california[session][item],today])

with open('outputData-aggreg.csv', 'a+') as csv_file:
    csvwriter = csv.writer(csv_file, delimiter=',')
    if toWriteAg:
        csvwriter.writerow(csvList)
    for session in catSpecific:
        #csvwriter.writerow([session] + list(dictFind[session].keys()))
        for item in catSpecific[session]:
            if 'individuals' in item:
                csvwriter.writerow([session, 'Individuals/Families', catSpecific[session][item],today])
            else:
                csvwriter.writerow([session, item, catSpecific[session][item],today])

with open('outputData-commons.csv', 'a+') as csv_file:
    csvwriter = csv.writer(csv_file, delimiter=',')
    if toWriteCo:
        csvwriter.writerow(csvList)
    for session in dictFind:
        #csvwriter.writerow([session] + list(dictFind[session].keys()))
        for item in dictFind[session]:
            if 'individuals' in item:
                csvwriter.writerow([session, 'Individuals/Families', dictFind[session][item],today])
            else:
                csvwriter.writerow([session, item, dictFind[session][item],today])

'''
failedPage= {}
donotopen=['.png','.mp4','.pdf','javascript:popUp','.aif','.jpg','.gif','.mp3']
green = ['.html']
traversed = []
failed_Pages = []
accessibleNot = {}
accessibilityCheck = ['Read More','Click Here','click here','read more','here','more','More','info','Info']
level = 1
base_url = ["shakeout.org","grandesecousse.org"]
r = open('C:/Users/junhu/Documents/SCEC WORK/websitebroken-SHAKEOUT.csv','r')
listSite=[]
for i in r.read().split('\n'):
    listSite.append(i)
r.close()
dict_link={}
def isIn(web_url):
    for ext in donotopen:
        if ext in web_url:
            return True
    return False
def filetext():
    retStr = 'webpage with undescriptive links, content\n'
    for link in list(accessibleNot.keys()):
        itemList=(' , ').join(acessibleNot[link])
        retStr += link +','+itemList +'\n'
    r=open('brokenWebDict.csv','w')
    r.write(retStr)
    r.close()
def opener(parent,url):
    try:
        failedPage[parent].append(url)
    except:
        failedPage[parent] = [url]
    return True
def getList(url="https://www.shakeout.org/",parent='https://www.shakeout.org/',level=1,LL=[],cmp_list=[]):
    LL.append(parent)
    print(url)
    #print('parsing a level', level,'page',url)
    if url in cmp_list:
        #print(url,' will be analyzed')
        return True
    if url in traversed:
        print(url, 'link already analyzed')
        return True
    traversed.append(url)
    try:
        page = requests.get(url,timeout = 10)
    except requests.exceptions.ConnectionError:
        LL.append('connection error')
        dict_link[url]=LL
        #print('page connection error', url)
        try:
            failedPage[parent].append(url)
        except:
            failedPage[parent] = [url]
        failed_Pages.append(url)
        
        return True
    except requests.exceptions.MissingSchema:
        LL.append('connection error')
        dict_link[url]=LL
        return True
    except requests.exceptions.InvalidSchema:
        LL.append('invalid schema')
        dict_link[url]=LL
        #print('page schema error', url)
        try:
            failedPage[parent].append(url)
        except:
            failedPage[parent] = [url]
        failed_Pages.append(url)
        return True
    except:
        LL.append('slow page')
        dict_link[url]=LL
        #print('slow page', url)
        try:
            failedPage[parent].append(url)
        except:
            failedPage[parent] = [url]
        failed_Pages.append(url)
        return True
        
    if page == 'hsjfhj' :
        return True
    elif int(page.status_code) >= 399:
        LL.append('page not found!')
        dict_link[url]=LL
            #print('page 400 code error',url)
        try:
            failedPage[parent].append(url)
        except:
            failedPage[parent] = [url]
        failed_Pages.append(url)
        return True
    elif base_url[0] not in url and base_url[1] not in url:
        LL.append('page out of bounds of program!')
        dict_link[url]=LL
        return True
    elif isIn(url):
        LL.append('did not open this!')
        dict_link[url]=LL
        #print('done')
        return True
    else:
        try:
            data = urllib.request.urlopen(url)
        except:
            LL.append('error')
            dict_link[url]=LL
            return True
        try:
            soup = BeautifulSoup(data,'html.parser')
        except AssertionError:
            LL.append('error')
            dict_link[url]=LL
            return True
        comments = soup.findAll(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]
        #print(len(soup.findAll('a')))
        #print(soup.findAll('a'))
        count = 1
        if level > 1:
            cmp_list=[]
        else:
            cmp_list=[]
        #print(cmp_list)
        for link in soup.findAll('a'):
            newLink = link.get('href')
            content = link.string
            if content in accessibilityCheck:
                #print(url)
                try:
                    accessibleNot[url].append(content)
                except:
                    accessibleNot[url] = [content]
                #print(traversed)
            #newLink = 'https://www.accuweather.com'
            if newLink == None:
                pass
            elif newLink in listSite:
                #print('nonurl:'+newLink)
                opener(url,newLink)
            elif newLink not in traversed and newLink +'index.html' not in traversed and newLink+'/index.html' not in traversed and newLink.replace('/index.html','/') not in traversed and newLink.strip('/') not in traversed and (base_url[0] in newLink or base_url[1] in newLink) and newLink+'/' not in traversed:
                count += 1
                #print(url,traversed)
                #traversed.append(url)
                getList(newLink,url,level+1,LL[:],cmp_list[:])
            #print('There are ',count,'pages of level',level + 1 )     
            #print('failed pages caught:',len(failedPage))
            #print('level', level , 'done')
        return True
#traversed=[]
getList()
print(len(traversed))
#filetext()
j = set()
for i in traversed:
    j.add(i)
retStr=''
for k in j:
    
    retStr+=k+'\n'
r=open('linkedSites-new.csv','w',encoding="utf-8")
r.write(retStr)
r.close()
newStr='Final Page\n'
for i,j in dict_link.items():
    newStr+=i+','+','.join(j)+'\n'
r=open('filePath-new.csv','w',encoding="utf-8")
r.write(newStr)
r.close()
newStr='Broken URLS\n'
for i in failed_Pages:
    newStr+=i+'\n'
r=open('brokenPage-new.csv','w',encoding="utf-8")
r.write(newStr)
r.close()
newStr='Broken Links for Page\n'
for i,j in failedPage.items():
    newStr+=i+','+','.join(j)+'\n'
r=open('brokenPageByURL-new.csv','w',encoding="utf-8")
r.write(newStr)
r.close()'''

