# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 14:50:46 2019

@author: thora
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

#API token and secrets for MKM api
(App_Token, App_Secret, Access_Token, Access_Token_Secret
 ) =   [string.replace('\n','') for string in open('mkm_api_info.txt').readlines()]

def loading_set_info_MKM(set_abr):
    #%%
    url = 'https://api.cardmarket.com/ws/v2.0/games/1/expansions'
    auth = requests_oauthlib.OAuth1(
        App_Token,
        client_secret=App_Secret,
        resource_owner_key=Access_Token,
        resource_owner_secret=Access_Token_Secret,
        realm = url
    )
    
    #Asking for expansions
    
    #response = session.get(url)
    response = requests.get(url,auth = auth)
    root = ET.fromstring(response.text.encode('utf8'))
    expansion_name = []
    expansion_id = []
    expansion_abbreviation = []
    for i in range(len(root)-1):
        #    print root[i][1].text
        expansion_id.append( int(root[i][0].text))
        expansion_name.append( root[i][1].text)
        expansion_abbreviation.append( root[i][7].text)

    #Identifying set name and number
    idx  = np.where(np.in1d(expansion_abbreviation, set_abr))[0][0]
    expansion = expansion_name[idx].upper()
    print '{} selected as expansion'.format(expansion)
    
    #Requesting singles from set
    url_template = 'https://www.mkmapi.eu/ws/v2.0/expansions/{}/singles'
    url = url_template.format(expansion_id[idx])
    
    
    # Singles from specific expansion
    auth = requests_oauthlib.OAuth1(
        App_Token,
        client_secret=App_Secret,
        resource_owner_key=Access_Token,
        resource_owner_secret=Access_Token_Secret,
        realm = url
    )
    #assert False, 'hej'
    response = requests.get(url,auth = auth)
    print  response.status_code
    
    root = ET.fromstring(response.text.encode('utf8'))
    product_id = []
    product_name = []
    product_rarity = []
    for i in range(1,len(root)-1):
        product_id.append( int(root[i][0].text))
        product_name.append( root[i][3].text)
        product_rarity.append( root[i][16].text.lower())
        
#    for item in root[i]:
#        print item
#        print item.text
    assert len(product_name )>0, 'LOADING OF SET FAILED'
    #%%
    return expansion,product_id, product_name, product_rarity

def loading_from_expansion_MKM(expansion):
    #%%

    #url = 'https://www.mkmapi.eu/ws/v2.0/games'
    # 1 is MTG    
    #url to load list of expansions
#    url = 'https://www.mkmapi.eu/ws/v2.0/games/1/expansions'
    url = 'https://api.cardmarket.com/ws/v2.0/games/1/expansions'
    auth = requests_oauthlib.OAuth1(
        App_Token,
        client_secret=App_Secret,
        resource_owner_key=Access_Token,
        resource_owner_secret=Access_Token_Secret,
        realm = url
    )
    
    #Asking for expansions
    
    #response = session.get(url)
    response = requests.get(url,auth = auth)
    print  response.status_code
    root = ET.fromstring(response.text.encode('utf8'))
    expansion_name = []
    expansion_id = []
    expansion_abbreviation = []
    for i in range(len(root)-1):
        expansion_id.append( int(root[i][0].text))
        expansion_name.append( root[i][1].text)
        expansion_abbreviation.append( root[i][7].text)

    #Identifying set name and number
#    idx  = np.where(np.in1d(expansion_abbreviation, set_abr))[0][0]
    idx  = np.where(np.in1d(expansion_name, expansion))[0][0]
#    expansion = expansion_name[idx].upper()
    print '{} selected as expansion'.format(expansion)
    
    #Requesting singles from set
#    url_template = 'https://www.mkmapi.eu/ws/v2.0/expansions/{}/singles'
    url_template = 'https://api.cardmarket.com/ws/v2.0/expansions/{}/singles'
    url = url_template.format(expansion_id[idx])
    
    
    # Singles from specific expansion
    auth = requests_oauthlib.OAuth1(
        App_Token,
        client_secret=App_Secret,
        resource_owner_key=Access_Token,
        resource_owner_secret=Access_Token_Secret,
        realm = url
    )
    #assert False, 'hej'
    response = requests.get(url,auth = auth)
    print  response.status_code
    
    root = ET.fromstring(response.text.encode('utf8'))
    product_id = []
    product_name = []
    product_rarity = []
    for i in range(1,len(root)-1):
        product_id.append( int(root[i][0].text))
        product_name.append( root[i][3].text)
        product_rarity.append( root[i][16].text.lower())
        
#    for item in root[i]:
#        print item
#        print item.text
    assert len(product_name )>0, 'LOADING OF SET FAILED'
    product_id = np.array(product_id)
    product_name = np.array(product_name)
    product_rarity = np.array(product_rarity) 
    #%%
    return expansion,product_id, product_name, product_rarity


def loading_set_info_ScryFall(set_abr):
    #%%
    #API request url template
    list_of_excluded_cards =['Plains','Island','Swamp','Mountain','Forest']
    url = 'https://api.scryfall.com/sets/{}'.format(set_abr)
    response = requests.get(url)
    set_json_output = response.json()
    
    expansion = set_json_output['name'].encode('utf8')
    # =============================================================================
    # Creating folder for set
    # =============================================================================
    set_path = expansion
    if not os.path.exists(set_path):
        os.mkdir(set_path)

    
    print 'SET - ' + expansion
    print 'SET SIZE: {}'.format(set_json_output['card_count'])
    url_cards_in_set = set_json_output['search_uri']

    #Loading initial set page
    response = requests.get(url_cards_in_set)
    json_output = response.json()
    #Preparing to run through json output
    product_id = []
    product_name = []
    product_rarity = []
    product_image_url = []
    image_filename = []
    product_color =[]
    product_color_identity = []
    more_data = True
    while more_data == True:
        print 'Length of the this page : {}'.format(len(json_output['data']))              
        for card in json_output['data']:
            card_name = card['name'].encode('utf8')#.replace(' // ', '_')
#            assert card_name != 'Watchdog', 'STOP'
            if not card_name in list_of_excluded_cards:
                product_name.append(card_name)
                #Collecting color
                product_color_temp = np.array([item.encode('utf8') for item in card['colors']])
                if product_color_temp.size == 0:
                    product_color_temp = np.array(['C'])
                product_color.append(product_color_temp)
                #Collecting color identity
                product_color_identity_temp =np.array([item.encode('utf8') for item in card['color_identity']])
                if product_color_identity_temp.size == 0:
                    product_color_identity_temp = np.array(['C'])
                product_color_identity.append(product_color_identity_temp)
                #Collecting card number
                number = int(card['collector_number'].encode('utf8'))
                product_id.append(number)
                #Collecting rarity
                rarity = card['rarity'].encode('utf8')
                product_rarity.append(rarity)
                image_url = card['image_uris']['normal']
                product_image_url.append(image_url)
                #Downloading image
                image_filename_temp = '{} {}.jpg'.format('%03d'%number, card_name.replace(':',''))    
                image_filename.append(image_filename_temp)
        #Checking for extra pages of set information
        if json_output['has_more']:
            print 'Next page'
            json_output = requests.get(json_output['next_page']).json()   
        else:
            more_data = False  
    # =============================================================================
    #   Checking if images are available and downloading missing images  
    # =============================================================================
    path = os.path.join(set_path,'{}_images'.format(set_abr))
    if not os.path.isdir(path):
        print 'Image path created'
        os.mkdir(path)       
    else:
        print 'Image path exists'
    
    array_of_images_avail =  np.array(glob.glob(os.path.join(path,'*')))
    
    
    for image_url, image_filename_temp in zip(product_image_url,image_filename):
        if (array_of_images_avail.size ==0 
        or not os.path.join(path,image_filename_temp) in array_of_images_avail):
            urllib.urlretrieve(image_url, os.path.join(path,image_filename_temp))
            print '{} Downloaded'.format(image_filename_temp)

#    array_of_images = [os.path.join(path,temp) for temp  in image_filename]
        
    #%%
    #numpyfying output
    product_id = np.array(product_id)
    product_name = np.array(product_name)
    product_rarity = np.array(product_rarity)
    product_color = np.array(product_color)
    return expansion,product_id, product_name, product_rarity, product_color, set_path


