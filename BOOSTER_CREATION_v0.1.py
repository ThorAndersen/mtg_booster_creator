#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 11:49:26 2018

@author: thor
"""
import glob
import os
from PIL import Image
import numpy as np
import random
np.set_printoptions(suppress=True)
#importing custom module
import set_info_functions as SIF
import want_list_functions as WANT
# =============================================================================
# SET SET ABRIVATION
# =============================================================================
#Identifying specific set
#set_abr = 'TMP' # Weatherlight
#set_abr = 'EXO' #Exodus
set_abr = 'MIR' #Mirage
#set_abr = 'STH' #Stronghold
    
# =============================================================================
# List of excluded cards
# =============================================================================
excluded_cards = ['Lion\'s Eye Diamond', 'City of Traitors', 'Mox Diamond']
# =============================================================================
# SET THE NUMBER OF BOOSTER WANTED
# =============================================================================
number_of_boosters = 3*8

# =============================================================================
# Defining booster construction
# =============================================================================
sampsize_rare = 1
sampsize_uncommon = 3 
sampsize_common = 11

# =============================================================================
# Loading set images and single names
# =============================================================================
(expansion, product_id, product_name, product_rarity, product_color, set_path
 ) = SIF.loading_set_info_ScryFall(set_abr)

# =============================================================================
# Removing excluded cards from set output
# =============================================================================
for card_temp in excluded_cards:
    delete_idx = np.where(product_name == card_temp)[0]
    if delete_idx.size > 0:
        print 'Deleting --- {} --- from set'.format(card_temp)
        product_id = np.delete(product_id,delete_idx)
        product_name = np.delete(product_name,delete_idx)
        product_rarity = np.delete(product_rarity,delete_idx)
        product_color = np.delete(product_color,delete_idx)
#%%

# =============================================================================
# Identifying rarity
# =============================================================================
product_name_array = np.array(product_name)

COMMON_idx = np.where( (np.array(product_rarity) == 'common') ) [0]
UNCOMMON_idx = np.where( (np.array(product_rarity) == 'uncommon') ) [0]
RARE_idx = np.where( (np.array(product_rarity) == 'rare') ) [0]
MYTHIC_idx = np.where( (np.array(product_rarity) == 'mythic') ) [0]

# =============================================================================
# Creating boosters
# =============================================================================

print '-----------------------------------------------------------------------'
print 'CREATING BOOSTERS '
print '-----------------------------------------------------------------------' 
booster = []
booster_split = []
for i in range(number_of_boosters):
    while True:
        common_sample_idx = random.sample(COMMON_idx, sampsize_common)
        common_colors = product_color[common_sample_idx]
        if len(np.shape(common_colors)) > 1:
            common_colors = np.concatenate(common_colors)
        #Checking if all colors are in the booster at common
        common_color_check = np.all(np.isin(np.array([['U'],['W'],['B'],['R'],['G']])
                        ,common_colors))
        #
        uncommon_sample_idx = random.sample(UNCOMMON_idx, sampsize_uncommon)
        uncommon_colors = product_color[uncommon_sample_idx]
#        if len(np.shape(uncommon_colors)) > 1:
        if True:
            uncommon_colors = np.concatenate(uncommon_colors)
        #Checking that at least 2 different colors are in the uncommons
        uncommon_color_check = np.sum(np.isin(np.array(['U','W','B','R','G','C'])
                                ,uncommon_colors)) >= 2
        
        if common_color_check and uncommon_color_check:
            break
        else:
            print 'Wrong color distribution, running again'
    rare_sample_idx = random.sample(RARE_idx, sampsize_rare)
    #Create booster
    booster_temp = rare_sample_idx +  uncommon_sample_idx + common_sample_idx
    booster.extend(booster_temp)
    booster_split.append(booster_temp)
print '-----------------------------------------------------------------------' 

#%%
#Check that there are not more than 8 repetitions of cards

#Sorting boosters

uniques = np.unique(booster)

times_uniques = np.array([booster.count(uniques[i]) for i in range(len(uniques))] )

print '-----------------------------------------------------------------------'
#Want lists must be split by 150 cards
split = 149
want_list_no = 0
want_list_name_template = os.path.join(set_path,'{}{}.txt')
want_list_name = want_list_name_template.format(set_abr,want_list_no)



f = open(want_list_name,'w')
for i in range(len(uniques)):
        name_temp = product_name[uniques[i]].encode('utf8')
        print '{} {} ({})'.format(times_uniques[i],name_temp, expansion)
        f.write('{} {} ({})'.format(times_uniques[i],name_temp, expansion))
        f.write('\n')
        
        if i == split:
            f.close()
            want_list_no += 1
            want_list_name = want_list_name_template.format(set_abr,want_list_no)
            f = open(want_list_name, 'w')
            
            print '-------- WANTs LIST SPLIT ------'
            split +=150
f.close()
print '-----------------------------------------------------------------------'        

# WANTS LISTS HAVE A LIMITATION OF 150 CARDS
print 'Number of unique cards'
print len(uniques)


# =============================================================================
# Plotting boosters
# =============================================================================
text = raw_input("Skal der laves billeder af boosters? [y/n]: ")
if text == 'y':
    #Loading images from set abrivation
    set_folder = os.path.join(set_path,'{}_images'.format(set_abr.upper()))
    array_of_images =  np.array(glob.glob(os.path.join(set_folder,'*')))
    
    #Selecting booster
    #booster_number = 0
    #cards_in_booster = booster_split[booster_number]
    for booster_number, cards_in_booster in enumerate(booster_split):
        print 'Creating booster image: {}'.format(booster_number)
        #Loading image paths
        booster_images = array_of_images[cards_in_booster]
    #    print [product_name[i] for i in cards_in_booster]
        
        #extracting card dimensions
        img = Image.open(booster_images[0])
        width,hight = img.size
        #Number of cards in booster
        no_cib = len(cards_in_booster) 
        #Card arrangement in booster
        booster_arangement = np.array([0,0,0,0,0,0,0,0,1,1,1,1,1,1,1])
        #Defining the corners of each card
        left = np.append(np.arange(8),np.arange(7)) * width
        right = left + width
        bottom = booster_arangement * hight
        top = bottom + hight
        #list_of_corners = zip(left,right,bottom,top)
        list_of_corners = zip(left,bottom,right,top)
            
        # =============================================================================
        # Creating the image    
        # =============================================================================
        #Creating empty image
        booster_result = Image.new("RGB", (max(right),max(top)))
        #Stiching in images of each card in the booster
        for index, file in enumerate(booster_images):
          path = os.path.expanduser(file)
          img = Image.open(path)
          img.thumbnail((width, hight), Image.ANTIALIAS)
          booster_result.paste(img, list_of_corners[index])
        
        booster_path = os.path.join(set_path,'boosters')
        if not os.path.isdir(booster_path):
            os.mkdir(booster_path)
        booster_result.save(os.path.join(booster_path,'booster_{}.jpg').format(booster_number))
#        booster_result.show()
        
# =============================================================================
# Add to wants lists og MKM
# =============================================================================
#%%
text = raw_input("Skal der laves want lister paa MKM? [y/n]: ")
if text == 'y':
    (MKM_expansion,MKM_product_id, MKM_product_name, MKM_product_rarity
     ) = SIF.loading_from_expansion_MKM(expansion) #SET ABR DOES NOT MATCH BETWEEN SCRYFALL AND MKM
    if MKM_expansion == expansion:
        cards_names_abc_sort_idx = np.argsort(product_name[uniques])
        card_names_abc = product_name[uniques][cards_names_abc_sort_idx]
        times_uniques_abc = times_uniques[cards_names_abc_sort_idx]
        
        card_idx_MKM = np.in1d(MKM_product_name,card_names_abc) 
        card_names_MKM = MKM_product_name[card_idx_MKM]
        MKM_abc_sort_idx = np.argsort(card_names_MKM)
        count_list = times_uniques_abc
        product_list = MKM_product_id[card_idx_MKM][MKM_abc_sort_idx]
        
    #    for name1, name2,count in zip(card_names_abc,card_names_MKM[MKM_abc_sort_idx],count_list):
    #        print name1
    #        print name2
    #        print count
    #        print '------'
        
        #Splitting want lists into 150 unique cards at best
        max_uniques = 150.
        start_idx = 0
        for i in np.arange(np.ceil(len(product_list)/max_uniques)).astype(int):
            want_list_name = set_abr + str(i)
            end_idx = int(max_uniques * (i+1))
            if len(card_names_abc[start_idx:]) > end_idx:
                print 'Splitting want list'
                temp_product_list = product_list[start_idx:end_idx]
                temp_count_list = count_list[start_idx:end_idx]
            else:
                print 'last want list'
                temp_product_list = product_list[start_idx:]
                temp_count_list = count_list[start_idx:]            
            start_idx = end_idx
            WANT.add_cards_to_list(want_list_name, temp_product_list, temp_count_list)
