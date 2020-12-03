'''
WikiTools -- wikitools.py
author: david rademacher
'''

from random import sample
from bs4 import BeautifulSoup
import requests

class page:
    def __init__(self, query):
        self.htm = beautify(query)
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


search_stem = 'https://en.wikipedia.org/w/index.php?search='
search_leaf = '&title=Special%3ASearch&fulltext=1&ns0=1'

# fuzzier search than beautify
# returns a list of possible results for the query.
# return a page if query exists.
def search(query):
    query = query.replace(' ','+')
    req = requests.get(search_stem + query + search_leaf)
    htm = BeautifulSoup(req.text, 'html.parser')
    links = [result.find('a').text for result in htm.find_all('li',class_='mw-search-result')]
    if htm.find_all('p',class_='mw-search-exists'):
        return links[0]
    else:
        return links


# beautify - get the BeautifulSoup of a wikipedia article
def beautify(article):
    leaf = article.replace(' ','_')
    req = requests.get('https://en.wikipedia.org/wiki/'+leaf)
    return BeautifulSoup(req.text, 'html.parser')


# get_contents - get the list of content section titles
def get_toc(htm):
    toc = []
    try:
        for item in htm.find('div',id='toc').find_all('li'):
            num = item.find('span',class_='tocnumber').text
            str = item.find('span',class_='toctext').text
            toc.append((num, str))
        return toc
    except AttributeError:
        return None


# read_section - print readable contents from section sec of page
def read_section(page, sec):
    blob = ''
    section = page.toc[sec][1].replace(' ','_')
    htm = page.htm

    # find start heading
    for title in htm.find_all('span',class_='mw-headline'):
        if title['id'] == section: section_head = title.parent

    # add paragraph text, stopping before next section
    blob += f'\n〈 {section_head.text} 〉\n'
    for sib in section_head.next_siblings:
        if sib.name == 'h3': blob += f'〈 {sib.text} 〉\n'
        if sib.name == 'p': blob += f'\t{sib.text}\n'
        if sib.name == 'h2': break

    # remove brackets (references)
    s = blob.find('[')
    while s >= 0:
        blob = blob[:s] + blob[blob.find(']')+1:]
        s = blob.find('[')
    return blob


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
