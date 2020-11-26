'''
WikiTools -- wikitools.py
author: david rademacher
'''

from random import sample
from bs4 import BeautifulSoup
import requests


# todo: fuzzier search

# beautify - get the BeautifulSoup of a wikipedia article 
def beautify(article):
    leaf = article[0] if isinstance(article, list) else article
    req = requests.get('https://en.wikipedia.org/wiki/'+leaf)
    return BeautifulSoup(req.text, 'html.parser')


# page_rand - return a random page
def page_rand():
    htm = beautify('Special:Random')
    return htm.find(id='firstHeading').text


# cat_rand - return a random category
def cat_rand():
    htm = beautify('Special:Random')
    return sample(htm.find(id='mw-normal-catlinks').find_all('a')[1:], 1)[0].text


# cats - return a list of categories for a page (type: 'normal' or 'hidden')
def cats(page, vis):
    if vis not in ['normal', 'hidden']:
        raise ValueError('vis must be \'normal\' or \'hidden\'')
    htm = beautify(page)
    xpr = 'mw-'+vis+'-catlinks'
    try:
        return ['Category:'+c.text for c in htm.find(id=xpr).find_all('a')[1:]]
    except AttributeError:
        # print(f'{page} has no {vis} categories')
        pass


# filter for good links
def linkable(tag):
    if tag.has_attr('href') and tag.parent.name == 'p':
        ref = tag['href']
        return ref[0] != '#' and ref.startswith('/wiki/') and ref.find(':') == -1
    return False


# get_links - return a list of linked pages
def get_links(page):
    htm = beautify(page)
    master = []
    links = htm.find(id='mw-content-text').find_all(linkable)
    for a in links:
        master.append(a['title'].replace('_',' '))
    return master


# journey - telephone but with output
def journey(start, n):
    return telephone(start, n, say=1)


# telephone - travel along n linked pages
# [starting page, link1, link2, ..., link n]
def telephone(start, n, say=0):
    if n < 1: return
    if say: print(f'{start} ')
    log = [start]
    htm = beautify(start)
    for i in range(n):
        try:
            log.append( sample(get_links(log[-1]), 1)[0] )
        except ValueError:
            log.append( get_links(page_rand()) )
        if say: print(' '*i + ' ↳ ' + f'{log[-1]}')
    return log


"""
cat_pages - return a list of n wikipedia pages randomly selected from a category,
and its subcategories. default value for n will return the entire list.
set subs to 0 to limit search to only pages in top level category.
"""

def cat_pages(root, n=0, subs=1, say=False):
    root = 'Category:' + root.replace(' ','_')
    master = []
    html = beautify(root)

    try:
        page_groups = html.find(id='mw-pages').find_all('div', class_='mw-category-group')
        for g in page_groups:
            for li in g.find_all('li'):
                if li.text.startswith('Template:'): continue
                master.append(li.text)
    except AttributeError:
        print(f'no pages found for \'{html.find(id="firstHeading").text}\'')

    if subs:
        try:
            subcat_groups = html.find(id='mw-subcategories').find_all('div', class_='mw-category-group')
            for g in subcat_groups:
                for li in g.find_all('li'):
                    text = cat_pages(li.find('a').text, subs=0)
                    if text: master += text
        except AttributeError:
            print(f'no subcategories found for \'{html.find(id="firstHeading").text}\'')
    
    if say:
        print(f'{root}')
        for pg in master: print(f' - {pg}')
    else: return master if (n==0 or n>len(master)) else sample(master, n)





