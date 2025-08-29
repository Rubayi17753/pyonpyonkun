import os
import re
from tqdm import tqdm
import numpy as np

IDSall = '⿲⿳⿰⿱⿺⿸⿹⿵⿷⿶⿴⿻'
IDCcommutatives = '⿺⿹⿻'

def seqqflip(s, ii):

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

    # i = position of commutative IDCs (one at a time)

    indexlist = []
    for char, i in zip(s, range(len(s))):
        if char in IDCcommutatives:
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
    return ''.join((si, seggmirr, sj))

def cartesianpow(listt, n):

    def cartesianprod(listt1, listt2):
        cprod = []
        for cellt1 in listt1:
            for cellt2 in listt2:
                cprod.append((cellt1 + cellt2))
        return cprod
    
    if n > 1:
        return cartesianprod(cartesianpow(listt, n - 1), listt)
        # list(itertools.product(*list(cartesianpow(listt, n - 1)), listt))
    elif n == 1:
        return listt
    else:
        return []

def clonemirror(s):
    ncom = sum(s.count(IDCcomt) for IDCcomt in IDCcommutatives)
    indexlist = []

    if ncom > 0:
        s_set = []   # list of strings to be returned
        
        for char, i in zip(s, range(len(s))):
            if char in IDCcommutatives:
                indexlist.append(i)

        prod2 = cartesianpow([(0,), (1,)], len(indexlist))

        for togseqq in prod2:
            s_nov = s
            for indecs, tog in zip(list(range(ncom)), togseqq):
                if tog == 1:
                    s_nov = seqqflip(s_nov, indecs)
            s_set.append(s_nov)
        return s_set

    else:
        return [s] 