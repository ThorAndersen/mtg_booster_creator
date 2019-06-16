# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 14:10:24 2019

@author: thora

The is creating a new WANT list and adding cards to them

"""
import requests, json
import requests_oauthlib
import xml.etree.ElementTree as ET
import numpy as np
import random
np.set_printoptions(suppress=True)
import time 
import matplotlib as plt
import os 
import glob 
import urllib
import xmltodict
import xml.etree.cElementTree as ET

#API token and secrets for MKM api
(App_Token, App_Secret, Access_Token, Access_Token_Secret
 ) =   [string.replace('\n','') for string in open('mkm_api_info.txt').readlines()]

def create_new_want_list(want_list_name):
    print 'Creating list named: {}'.format(want_list_name)
    url = 'https://api.cardmarket.com/ws/v1.1/wantslist'
    
    root = ET.Element("request")
    doc = ET.SubElement(root, "wantslist")
    
    ET.SubElement(doc, "idGame").text = "1"
    ET.SubElement(doc, "name").text = want_list_name
    
    tree = ET.ElementTree(root)
    tree.write("filename.xml")
    
    xml =  open('filename.xml').read()
    
    auth = requests_oauthlib.OAuth1(
        App_Token,
        client_secret=App_Secret,
        resource_owner_key=Access_Token,
        resource_owner_secret=Access_Token_Secret,
        realm = url
    )
    r = requests.post(url, data = xml, auth = auth)
#    print r.text
    if '200' in str(r) and 'failed' not in str(r.text):
        print '{} - Created'.format(want_list_name)
    elif 'Eine Wantslist mit dem Namen existiert bereits' in str(r.text):
        print 'List alreaddy exists'
    return 

def collect_list_of_wantlists():
    url =  'https://api.cardmarket.com/ws/v2.0/wantslist'
    auth = requests_oauthlib.OAuth1(
        App_Token,
        client_secret=App_Secret,
        resource_owner_key=Access_Token,
        resource_owner_secret=Access_Token_Secret,
        realm = url
    )
    
    response = requests.get(url,auth = auth)    
    #Create dict
    o = xmltodict.parse(response.text.encode('utf8'))
    # Transform dict to json
    output = json.loads(json.dumps(o) )
    
    temp = output['response']['wantslist']
    if type(temp) == list:
        list_of_wants_name = [ temp[i]['name'].encode('utf8') for i in range(len(temp))]
        list_of_wants_ID = [ temp[i]['idWantslist'].encode('utf8') for i in range(len(temp))]
    else:
        list_of_wants_name = []
        list_of_wants_ID = []
    return list_of_wants_name, list_of_wants_ID

def finding_WLs_ID(want_list_name):
    list_of_wants_name, list_of_wants_ID = collect_list_of_wantlists()
    if want_list_name in list_of_wants_name:
        wantlistID = list_of_wants_ID[list_of_wants_name.index(want_list_name)]
    else:
        wantlistID = '0'
    return wantlistID

def add_cards_to_WL(wantlistID,product_list, count_list):
    root = ET.Element("request")
    if True:
        action = ET.SubElement(root, "action").text = 'add'
        #Running through all products to be added
        for i in range(len(product_list)):
            product = ET.SubElement(root, "product")
            if True:
                ET.SubElement(product, "idProduct").text = str(product_list[i])
                ET.SubElement(product, "count").text = str(count_list[i])
                ET.SubElement(product, "idLanguage").text = "1"
                ET.SubElement(product, "minCondition").text = "LP"
                ET.SubElement(product, "wishPrice").text = "0"   
    tree = ET.ElementTree(root)
    tree.write("filename.xml")
    
    xml =  open('filename.xml').read()
#    print xml
#    print ''
    url = 'https://api.cardmarket.com/ws/v1.1/wantslist/{}'.format(wantlistID)
    auth = requests_oauthlib.OAuth1(
        App_Token,
        client_secret=App_Secret,
        resource_owner_key=Access_Token,
        resource_owner_secret=Access_Token_Secret,
        realm = url
    )
    r = requests.put(url, data = xml, auth = auth)
    if '200' in str(r):
        print 'CARDS ADDED TO LIST'
    else:
        print 'FAILED TO ADD CARDS'
    return 
    
def add_cards_to_list(want_list_name, product_list, count_list):
    wantlistID = finding_WLs_ID(want_list_name)
    while wantlistID != '0':
        print 'List exists, creating new list called'
        want_list_name = want_list_name + 'new'
        print want_list_name
        wantlistID = finding_WLs_ID(want_list_name)
    create_new_want_list(want_list_name)
    wantlistID = finding_WLs_ID(want_list_name)
    add_cards_to_WL(wantlistID,product_list, count_list)
    return
    
if __name__ == '__main__': 
    want_list_name = 'test2'
    product_list = [8384, 8388, 8392, 8396, 8400]
    count_list = [1,2,3,4,5]
#    #Creating new list
#    create_new_want_list(want_list_name)
#    #Colelcting naems of existing lists
#    list_of_wants_name, list_of_wants_ID = collect_list_of_wantlists()
#    #Collect ID of specific list name
#    wantlistID = finding_WLs_ID(want_list_name)
#
#    #Adding cards to WL
#    wantlistID = list_of_wants_ID[list_of_wants_name.index(want_list_name)]
#
#    
#    add_cards_to_WL(wantlistID,product_list, count_list)
    #Creating list and adding cards
    add_cards_to_list(want_list_name, product_list, count_list)