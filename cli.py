'''
WikiTools -- cli.py
author: david rademacher
'''

from wikitools import *
from random import sample

print('initializing WikiTools CLI...')
user_pg = page()
print('enter \'h\' for help ✔︎')

comm = dict()
comm['c'] = 'print page categories'
comm['l'] = 'print \'contents\' list'
comm['r'] = 'print related pages'
comm['n'] = 'get a new page'
comm['j'] = 'take a journey'
comm['h'] = 'display commands'
comm['q'] = 'quit'

def print_commands():
    for k,v in comm.items():
        print(f' {k} -> {v}')

def prompt():
    global user_pg
    return input(f'\n▶︎ {user_pg} ◀︎\n  .: ')

def print_cats():
    global user_pg
    print('\nyour page\'s categories: ')
    for cat in user_pg.cats:
        print(f'  {cat[9:]}')

def print_toc():
    global user_pg
    toc = user_pg.toc
    if toc is not None:
        for i in range(len(toc)):
            if toc[i][0] == toc[i-1][0]: print('  ',end='')
            print(toc[i])
    else:
        print('no table of contents found.')

def new_page():
    global user_pg
    n = input('\nrandom page? (y/n) ')
    if n not in ['y','n']: new_page()
    if n == 'y': user_pg = page()
    if n == 'n':
        qry = input('query: ')
        res = search(qry)
        while isinstance(res, list):
            print(f'\nno page found for \"{qry}\".\nsome suggestions:')
            for sg in res:
                print(f' ・{sg}')
            res = search(input('\nquery: '))
        user_pg = res

def take_journey():
    global user_pg
    n = input('how far? (integer) ')
    k = input('one way ticket? (y/n) ')
    print()
    dest = journey(user_pg.title, int(n))[-1]
    if k == 'y': user_pg = page(dest)

while True:
    n = prompt()
    if n == 'c': print_cats()
    if n == 'l': print_toc()
    if n == 'n': new_page()
    if n == 'h': print_commands()
    if n == 'j': take_journey()
    if n == 'q': break
