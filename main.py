from page import page
from wikitools import *

h = page()

print(h)
for p in h.htm('p'):
	print(p.text)


# journey(page_rand(), 10)

# cat = cat_rand()
# pgs = cat_pages(cat, 10)

# print(f'\n{cat}:')
# for i,p in enumerate(pgs):
# 	print(f'{i+1}. {p}')
