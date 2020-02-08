# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 12:32:37 2020
@author: Elione Bo
"""


import json
import time
import pdfkit
import os
import re
import requests
import wechatsogou
ws_api = wechatsogou.WechatSogouAPI(captcha_break_time=3)

headers = {
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 QBCore/4.0.1295.400 QQBrowser/9.0.2524.400 Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2875.116 Safari/537.36 NetType/WIFI MicroMessenger/7.0.5 WindowsWechat',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.5;q=0.4'
}

cookies = {
     'devicetype': 'Windows10',
     'lang': 'zh_CN',
     'pass_ticket': 'JQKyaPXTRZu55rkIjvEAf4nhzj08usWX6squSJ0A9A1VrkpA9xd9tvl0/s3Krn/7',
     'version': '6208006f',
     'wap_sid2': 'CMC13O4EElxxVlNxbXRSNV92Y3lWN2pUX0hUUWh0YURSbXYzQzdnNnFqbXhRcW9tdmlvY3F5RXNmcnVTVF9kQXc0ZW1ybWxUWndUSUdIWkRidVd0VGtDSnlsRmRsQmNFQUFBfjCLzu7xBTgNQJVO',
     'wxtokenkey':'777',
     'wxuin': '1305942720'
}

def get_params(offset):
    params = {
        'action': 'getmsg',
        '__biz': 'MzI4ODc5MDUyMA==',
        'f': 'json',
        'offset': '{}'.format(offset),
        'count': '10',
        'is_ok': '1',
        'scene': '126',
        'uin': 'Mjc3MDUzNjgxOQ==',
        'key': '8f4e23a904780af1e5dec8b1ada1b031b529e18535b34009a02b8b0ce06155de8d66926fbbec06f62955aac76dc3e72ef9d3fd04b36c8b329364127cb8af15bc9059753e0058510b20821492c6479860',
        # 'pass_ticket': 'mf2myiNN1c0GYhagys4+lwBZd0Vj63voe7OZqUdKxh9esxBoVW8R1imPMwmOSlly',
        # 'appmsg_token': '1021_AKKMhy%2B%2FHmCaW4J47-5slRtmBiYAjYC4XSiyEg~~',
        # 'x5': '0',
    }

    return params

# 保存文件时，去除名字中的非法字符
def validateTitle(title):
    rstr = r'[\\/:*?"<>|\r\n]+'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title




def get_list_data(offset,error_obs = 0):
    requests.packages.urllib3.disable_warnings() # 禁用urllib
    base_url = 'https://mp.weixin.qq.com/mp/profile_ext'
    res = requests.get(base_url, headers=headers, params=get_params(offset), cookies=cookies,verify=False)
    data = json.loads(res.text)

    can_msg_continue = data['can_msg_continue']
    next_offset = data['next_offset']

    general_msg_list = data['general_msg_list']
    list_data = json.loads(general_msg_list)['list']
    
    pdf_options = {
        'encoding': "UTF-8",
        'quiet':''
    }
    
    for data in list_data:
        date = data["comm_msg_info"]["datetime"]
        date = str(time.strftime('%Y-%m-%d',time.localtime(date)))
        
        try:
            if data['comm_msg_info']['type']==49:
                title = date + '_' + str(validateTitle(data['app_msg_ext_info']['title']))
                title += '_原创' if data['app_msg_ext_info']['copyright_stat']==11 else '_非原创'
                title_path = r'C:\Users\Elione Bo\OneDrive\桌面\test\{}.pdf'.format(title)
                
                content_url = data['app_msg_ext_info']['content_url']
                content_info = ws_api.get_article_content(content_url)
                html_code = content_info['content_html']  
            
            elif data['comm_msg_info']['type']==1:
                title = date + '_' + str(data['comm_msg_info']['id'])
                title += '_原创' if data['app_msg_ext_info']['copyright_stat']==11 else '_非原创'
                title_path = r'C:\Users\Elione Bo\OneDrive\桌面\test\{}.pdf'.format(title)
                
                content_url = data['comm_msg_info']['content']
                html_code = content_url
            
            
            if not os.path.exists(title_path):
                pdfkit.from_string(html_code, title_path ,options=pdf_options)
                print('Done: ' +  title)
           
        except Exception as e:
            #print(e)
            try:
                pdfkit.from_url(content_url, title_path ,options=pdf_options)
                print('Done: ' +  title)
            except:
                error_obs+=1
                print(error_obs)
                #print('____________________________')
                #print(e)
                #print(content_url)
                #print(title)
                #print('____________________________')
            else:
                pass 
        else:
            pass
        
    if can_msg_continue == 1:
        get_list_data(next_offset,error_obs = error_obs)


get_list_data(0)

# 一部分图文可以抓取 pdfkit-fromstring
# 一部分，部分图文可以抓取 pdfkit-formurl
# 剩下的部分，无法抓取通过pdfkit：wkhtmltopdf error

# 尝试通过其他办法抓取
# 多运行几次可以间接解决这个问题


