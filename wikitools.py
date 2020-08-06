from random import sample
from bs4 import BeautifulSoup
import requests


# beautify - get the BeautifulSoup of a wikipedia article 
def beautify(article):
	leaf = article[0] if isinstance(article, list) else article
	req = requests.get('https://en.wikipedia.org/wiki/'+leaf)
	return BeautifulSoup(req.text, 'html.parser')


# page_rand() - return a random page
def page_rand():
	htm = beautify('Special:Random')
	return htm.find(id='firstHeading').text


# cat_rand - return a random category
def cat_rand():
	htm = beautify('Special:Random')
	return sample(htm.find(id='mw-normal-catlinks').find_all('a')[1:], 1)[0].text


# cat_sample - return n random pages from a category root
# currently accumulates the list, then samples--could be better to go depth-first 
def cat_sample(root, n=1, depth=0):
	pgs = cat_pages(root, depth)
	if pgs: return (sample(pgs, n)[0] if n==1 else sample(pgs, n))
	else: return False


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
	if say: print(f'{start} ', end='')
	log = [start]
	htm = beautify(start)
	for i in range(n):
		try:
			log.append( sample(get_links(log[-1]), 1)[0] )
			if say: print(f'-> {log[-1]} ', end='')
		except ValueError:
			# print(f'!!no links found for {log[-1]} - leaping randomly')
			log.append( get_links(page_rand()) )
			if say: print(f'?? {log[-1]} ', end='')
	return log


# cat_pages - return a list of wikipedia pages under a given category
def cat_pages(root, depth=0):
	root = 'Category:' + root.replace(' ','_')
	master = []
	html = beautify(root)

	if html.find(id='mw-pages') is None:
		return False

	page_groups = html.find(id='mw-pages').find_all('div', class_='mw-category-group')
	for g in page_groups:
		for li in g.find_all('li'):
			if li.text.startswith('Template:'): continue
			master.append(li.text)

	if depth:
		subcat_groups = html.find(id='mw-subcategories').find_all('div', class_='mw-category-group')
		for g in subcat_groups:
			for li in g.find_all('li'):
				text = cat_pages(li.find('a').text)
				if text: master += text
	
	return master