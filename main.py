
from wikitools import *

# journey(page_rand(), 10)

cat = cat_rand()
pgs = cat_pages(cat)

print(cat)
for p in pgs:
	print(f'  {p}')
