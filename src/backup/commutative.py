import itertools

#   sample of List.txt
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

# "mirror" of s to be appended to s_set
        # togseqq = sequence that toggles seqqflip
        # if tog = 1 flip else don't flip
        # print('indexlist:\t' + str(indexlist))
        # print('togseqq:\t' + str(togseqq))
        # indexlist = list(reversed(indexlist))

def insert_char(s, char, n):
    return s[:n - 1] + char + s[n - 1:]

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