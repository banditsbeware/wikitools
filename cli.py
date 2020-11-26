from wikitools import *
from page import *

print('initializing WikiTools CLI...')
user_pg = page()
print('enter \'h\' for help ✔︎')

def print_commands():
    print(' c -> print page categories')
    print(' n -> get a new page')
    print(' j -> take a journey')
    print(' h -> display commands')
    print(' q -> quit')

def prompt():
    global user_pg
    return input(f'\n▶︎ {user_pg} ◀︎\n  .: ')

def print_cats():
    print('\nyour page\'s categories: ')
    for cat in user_pg.cats:
        print(f'  {cat[9:]}')

def new_page():
    global user_pg
    n = input('\nrandom page? (y/n) ')
    if n == 'y': user_pg = page()
    elif n == 'n': user_pg = page(input('\nquery: '))
    else: new_page()

def take_journey():
    global user_pg
    n = input('how far? (integer) ')
    k = input('one way ticket? (y/n) ')
    dest = journey(user_pg.title, int(n))[-1]
    if k == 'y': user_pg = page(dest)

while True:
    n = prompt() 
    if n == 'q': break
    if n == 'c': print_cats()
    if n == 'n': new_page()
    if n == 'h': print_commands()
    if n == 'j': take_journey()
        
