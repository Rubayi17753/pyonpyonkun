import os
import re
from tqdm import tqdm
import numpy as np
import itertools

# ⿲⿳ ⿰⿱ ⿺⿸⿹ ⿵⿷⿶ ⿴ ⿻
IDCcommutativelist = ('⿺','⿹','⿻')

#sample of List.txt
#   0   1   2   3
#   丆	丆1	(⿱,一,丿)	.
#   丆	丆2	(⿱,一,㇒)	.
#   心	心1	(⿰,㇒,(⿻,乚,(⿰,丶,丶)))	.
#   勺	勺1	(⿹,勹,丶)	.
#   勺	勺2	(⿹,勹,一)	.
# Contractions			
#   (⿰,㇒,乛)		[⺈]	
#   (⿰,丿,丨)		[丌]	
#   (⿰,丿,丿)		[勿]	

#   if type[0] = '.' put char into PRIMES
#       effect no change
#   else put char into COMPOSITES
#       decompose until sequence contains no prime

# Reminder to self: after copying spreadsheet to List.txt enact following F&R:
#   1\t > \t

def insert_char(s, char, n):
    return s[:n - 1] + char + s[n - 1:]

def decomposs(seqq, compodict, composet, condensedict):
    compocountdict2 = -1
    while compocountdict2 != 0:
        compocountdict2 = 0
        elms = seqq.replace('(','').replace(')','').split(',')
        for elm in elms:
            if elm in composet:
                seqq = seqq.replace(elm, compodict[elm])
                # print(elm)
                compocountdict2 += 1
        for segment in condensedict:
            while segment in seqq:
                seqq = seqq.replace(segment, condensedict[segment])
    return seqq

def clonee1(l, compocountdict):
    multchar = []
    multcomp = []       # List comprising number of ways to compose char where > 1
    multcomppost = []   # Positions of chars in multcomp
    for index in range(len(l)):
        elm = l[index]
        compocount = compocountdict.get(elm, 0)
        if compocount > 1:
            multchar.append(elm)
            multcomp.append(compocount)
            multcomppost.append(index)

    return (multcomp, multcomppost, multchar)

def clonee2(l, multcomp, multcomppost):
    clonelist = []

    rangelist = [list(range(1, n + 1)) for n in multcomp]
    #   for range in rangelist:     
    #       range[0] = ''
    prodlist = list(itertools.product(*rangelist))
    for prod in prodlist:
        for ndex, post in zip(prod, multcomppost):  # Cartesian matrices and where to insert them
            if ndex == 1:
                ndexs = ''
            else:
                ndexs = str(ndex)
            clonelist.append(insert_char(l, ndexs, post + 2))

    return clonelist    # Bear in mind: if no multcomp, clonelist = []

def seq2net(seqqnov):
    seqqnet = seqqnov
    for charc in ('()⿲⿳⿰⿱⿺⿸⿹⿵⿷⿶⿴⿻'):
        seqqnet = seqqnet.replace(charc, '')  
    seqqnet = seqqnet.replace(',', ' ')
    while '  ' in seqqnet:
        seqqnet = seqqnet.replace('  ', ' ')
    return seqqnet

def extractbracket(s):
    bracketlist = []
    n = 0
    if s.count('(') == s.count(')') and s.count('(') != 0:
        post = list()
        ord = list()
        ord2 = list()
        sn = 0
        dx = 0

        # Identify bracket positions
        for char, n in zip(s, range(len(s))):
            if char == '(':     
                post.append(n)
                ord.append(sn)
                ord2.append(sn)
                sn += 1

            elif char == ')':   
                post.append(n)
                dx = ord2[-1] + 0.5
                ord.append(dx)
                ord2 = ord2[:-1]

        # Construct bracketlist
        for k in range(int(max(ord) + 0.5)):
            snindex = post[ord.index(k)]
            dxindex = post[ord.index(k + 0.5)]
            bracketlist.append(s[snindex : dxindex + 1])

    return(bracketlist)

def locatebracketpair(s, n):
    if s[n] == '(':
        point = 0
        for char, index in zip(s[n:], range(len(s[n:]))):
            if char == '(':
                point += 1
            elif char == ')' and point == 1:
                x = index
                break
            elif char == ')':
                point -= 1
        return s[n : n+x+1]
    else:
        return ''

def clonemirror(s):
    ncom = sum(s.count(IDCcomt) for IDCcomt in IDCcommutativelist)
    indexlist = []

    if ncom > 0:
        s_set = []   # list of strings to be returned
        
        for char, i in zip(s, range(len(s))):
            if char in IDCcommutativelist:
                indexlist.append(i)

        prod2 = cartesianpow([(0,), (1,)], len(indexlist))
        # print('prod2:\t' + str(prod2))
        # print('indexlist:\t' + str(indexlist))
        # print(prod2)

        for togseqq in prod2:
            s_nov = s   # "mirror" of s to be appended to s_set
            # togseqq = sequence that toggles seqqflip
            # if tog = 1 flip else don't flip
            # print('indexlist:\t' + str(indexlist))
            # print('togseqq:\t' + str(togseqq))
            # indexlist = list(reversed(indexlist))
            for indecs, tog in zip(list(range(ncom)), togseqq):
                if tog == 1:
                    s_nov = seqqflip(s_nov, indecs)
            s_set.append(s_nov)
            # print(s_nov)
        return s_set

    else:
        return [s] 
    
def seqqflip(s, ii):
        # i = position of commutative IDCs (one at a time)

        indexlist = []
        for char, i in zip(s, range(len(s))):
            if char in IDCcommutativelist:
                indexlist.append(i)    

        i = indexlist[ii]
        char = s[i]

        ssin = s[i+2 : ]
        if ssin[0] == '(':
            comsin = locatebracketpair(ssin, 0)
        else:
            comsin = ssin.split(',')[0]

        sdex = ssin[len(comsin) + 1:]
        if sdex[0] == '(':
            comdex = locatebracketpair(sdex, 0)
        else:
            comdex = sdex.split(',')[0].strip(')')
        
        seggmirr = ''.join((char, ',', comdex, ',', comsin))
        j = i + len(seggmirr)
        si = s[:i]
        sj = s[j:]
        # print('string:' + '\t' + s + '\t' + str(i))
        # print('segmentation:' + ' | ' + si + ' | ' + comsin  + ' | ' + comdex + ' | ' + sj)
        return ''.join((si, seggmirr, sj))

def cartesianpow(listt, n):
    if n > 1:
        return cartesianprod(cartesianpow(listt, n - 1), listt)
        # list(itertools.product(*list(cartesianpow(listt, n - 1)), listt))
    elif n == 1:
        return listt
    else:
        return []

def cartesianprod(listt1, listt2):
    cprod = []
    for cellt1 in listt1:
        for cellt2 in listt2:
            cprod.append((cellt1 + cellt2))
    return cprod

