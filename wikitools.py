'''
WikiTools -- wikitools.py
author: david rademacher
'''

from random import sample
from bs4 import BeautifulSoup
import requests

class page:
    def __init__(self, query='Special:Random'):
        self.htm = beautify(query)
        if len(self.htm(id='noarticletext')):
            print(f'unable to find {query}.\nhere\'s a random page')
            self.htm = beautify('Special:Random')
        self.title = self.htm.find(id='firstHeading').text
        self.cats = cats(self.htm, 'normal')
        self.hcats = cats(self.htm, 'hidden')
        self.toc = get_toc(self.htm)
        self.links = get_links(self.title)
        self.related = None

    def generate_related(self):
        self.related = set()
        strs = [f' {i+1}/{len(self.cats)}: {cat}' for i,cat in enumerate(self.cats)]
        maxlen = max([len(s) for s in strs])
        for i,s in enumerate(strs):
            print(f'{s:{maxlen}}',end='\r')
            dp = deep_pages(self.cats[i])
            print(f'{s:{maxlen}} found {len(dp)}')
            self.related |= dp
        print(f'found {len(self.related)} related pages')

    def __repr__(self):
        return 'page()'

    def __str__(self):
        return self.title


search_stem = 'https://en.wikipedia.org/wiki/Special:Search?search='
# fuzzier search than beautify
# returns a list of possible results for the query.
# return a page if query exists.
def search(query):
    #query = query.replace(' ','+')
    req = requests.get(search_stem + query + '&ns0=1')
    results = BeautifulSoup(req.text, 'html.parser')
    try:
        return [link.text for link in results.find('ul',class_='mw-search-results').find_all('a')]
    except AttributeError:
        return page(query)


# beautify - get the BeautifulSoup of a wikipedia article
def beautify(article):
    if isinstance(article, list): raise ValueError(f'beautify({article})\n\ncannot beautify a list\n')
    leaf = article.replace(' ','_')
    req = requests.get('https://en.wikipedia.org/wiki/'+leaf)
    return BeautifulSoup(req.text, 'html.parser')


# get_contents - get the list of content section titles
def get_toc(htm):
    try:
        return [link.text for link in htm.find('div',id='toc').find_all('a')]
    except AttributeError:
        return None


# page_rand - return a random page
def page_rand():
    htm = beautify('Special:Random')
    return htm.find(id='firstHeading').text


# cat_rand - return a random category
def cat_rand():
    htm = beautify('Special:Random')
    return sample(htm.find(id='mw-normal-catlinks').find_all('a')[1:], 1)[0].text


# cats - return a list of categories for a page (type: 'normal' or 'hidden')
def cats(htm, vis):
    if vis not in ['normal', 'hidden']:
        raise ValueError('vis must be \'normal\' or \'hidden\'')
    xpr = 'mw-'+vis+'-catlinks'
    try:
        return [c.text for c in htm.find(id=xpr).find_all('a')[1:]]
    except AttributeError:
        # print(f'{page} has no {vis} categories')
        pass


# regex for good links
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


# get n pages selected randomly from a category
# n=0 will return all pages
def pages_in(category, n=0):
    htm = beautify('Category:' + category.replace(' ','_'))
    try:
        pgs = [a.text for a in htm.find(id='mw-pages').find(class_='mw-content-ltr').find_all('a')]
    except AttributeError: return set()
    if 0 < n and n <= len(pgs): return sample(pgs, n)
    return set(pgs)


# get n categories selected randomly from a category
# n=0 will return all categories
def categories_in(category, n=0):
    htm = beautify('Category:' + category.replace(' ','_'))
    try:
        cts = [i.find('a').text for i in htm.find_all('div', class_='CategoryTreeItem')]
    except AttributeError: return set()
    if 0 < n and n < len(cts): return sample(cts, n)
    return set(cts)


# get all pages within category and direct subcategories
def deep_pages(category):
    pgs = pages_in(category)
    for c in categories_in(category): pgs |= pages_in(c)
    return pgs
