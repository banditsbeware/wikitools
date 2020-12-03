from wikitools import *

p = page('Oology')

print(p.toc)
print(read_section(p, 4))
