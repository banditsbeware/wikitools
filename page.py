from wikitools import *

class page:
	def __init__(self, query='Special:Random'):
		self.htm = beautify(query)
		if len(self.htm(id='noarticletext')):
			raise ValueError(f'no wikipedia page exists for \'{query}\'')
		self.title = self.htm.find(id='firstHeading').text
		self.cats = cats(self.title, 'normal')
		self.hcats = cats(self.title, 'hidden')

	def is_cat(self, cat):
		return 'Category:'+cat in self.cats

	def __repr__(self):
		return 'page()'

	def __str__(self):
		return f'page(\'{self.title}\')'