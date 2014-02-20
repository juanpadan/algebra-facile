#!/usr/bin/python
LETT="qwertyuiopasdfghjklzxcvbnm"
NUM="1234567890"

#debug
import code
import readline
import rlcompleter

#TODO supporto divisione e frazioni

def risolvi(esp):
    esp = esp + "\0" #fine esplicita
    mon = 0
    out = [] #lista di elementi
    #TODO rimuovi spazi
    #TODO verificate integrita' sintassi 
    par = 0 #controlla che ogni parentesi si chiuda
    for c in esp:
        if c == "(":
            par += 1
        elif c == ")":
            par -=1
        if par == -1:
            raise Exception("errore: parentesi non corrispondenti")

        if c == "/": #temporaneo
            raise Exception("Ilsupporto alla divisione sara' presto aggiunto")
    if par != 0:
        raise Exception("errore: parentesi non corrispondenti")

    tmp = ""#variabile ch prende il valore del monomio temporaneo
    i = 0
    pol = [] #lista di monomi
    out = Polinomio([])
    prec = Polinomio([])
    #se vi e' una parentesi e poi un * o un  tmp avra' valore "" e prec sara' il valore della 
    #parentesi ridotta a polinomio su cui saranno eseguite le normali operazioni
    #eseguite con Polinomio(tmp)
    while esp[i] != "\0":
        if esp[i] in "*-" and esp[i+1] == "(":
            s = esp[i]
            if not prec.pol:
                prec = Polinomio(tmp)
            tmp=""
            par = 1
            i+=2
            sub = ""
            while par>0:
                if esp[i]==")":
                    par-=1
                    if par>0:
                        sub+=esp[i]
                elif esp[i]=="(":
                    par+=1
                    sub+=esp[i]
                else:
                    sub += esp[i]
                i+=1
            if s == "*":
                prec *= risolvi(sub)       #
            elif s == "/":                 # puo' essere ottimizzato con multiprocessing
                prec /= risolvi(sub)       #

        elif esp[i] in "+-" and esp[i+1]=="(":
            s = esp[i]
            if prec.pol:
                out += prec
                prec = Polinomio([])
            else:
                out += Polinomio(tmp)
                tmp = ""
            sub = ""
            i+=2
            par = 1
            while par>0:
                if esp[i]==")":
                    par-=1
                    if par>0:
                        sub+=esp[i]
                elif esp[i]=="(":
                    par+=1
                    sub+=esp[i]
                else:
                    sub+=esp[i]
                i+=1
            if s == "+":
                prec = Polinomio(sub)
            elif s == "-":
                prec -= Polinomio(sub)
        
        elif esp[i] == "(":#TODO fix ugly hack
            esp=esp[:1]+"*"+esp[1:]

        elif esp[i] in "+-":
            if prec.pol:
                out += prec
                prec = Polinomio([])
            else:
                out += Polinomio(tmp)
                tmp = ""
                
                
            if esp[i]=="-":
                tmp+="-"
            i+=1
      
            
        else:
            tmp+=esp[i]
            i+=1
    #end wile
        
    if prec.pol:
        out += prec
        prec = Polinomio([])
    else:
        out += Polinomio(tmp)
        tmp = ""
    return out




def prodotto_variabili(a,b):
    """da due dizionari lettera:esponente ritorna il prodotto"""
    out = {}
    for lett, esp in a.items():
        out.update({lett:esp})
    for lett, esp in b.items():
        if lett not in out:
            out.update({lett:esp})
        else:
            t = out[lett]
            out.update({lett:esp+t})
    return out



def compara_variabili(a,b):
    """verifica che due dizionari siano congruenti"""
    #TODO verifica singolarita' di variabile
    if len(a)==len(b):
        out = True
        for i in range(len(a)):
            ca = sorted(a.keys())
            cb = sorted(b.keys())
            if ca[i]!=cb[i]:#if keys are not equal
                out = False
                break
            elif a[ca[i]]!=b[cb[i]]:#if keys are equal test values
                out = False
                break
        return out
    else:
        return False






def monomizza(esp):#ok
    """trasforma in monomio un'espressione di sole moltiplicazioni, ritorna la coppia valore intero, lettere"""
    #todo verifica integrita'
    lista = []
    mon = ""
    for c in esp:
        if c !="*":
            mon +=c
        else:
            lista.append(mon)
            mon = ""

    lista.append(mon)

    if len(lista)==0:
        raise Exception("lista vuota")
    coeficente = 1
    lett = {}
    for x in lista:
        t,lt = interpreta_monomio(x)
        lett = prodotto_variabili(lett,lt)
        coeficente *= t

    return (coeficente,lett)


def interpreta_monomio(esp):
    """dato un monomio in forma ad esempio "5a2b4" lo trasforma in modo uniforme, ritorna
    il valore intero, un dizionario lettera:esopnente"""
    esp += " "#TODO sostituire con \0
    x = ""#cifre di x poi convrtite da int
    lx = {}#lettere
    i = 0 #cursor

    if esp[0] == "-":#controllo negativita'
        neg = -1
        i = 1
    else:
        neg = 1

    #raccogli il coeficente
    while esp[i] in NUM:
        x+=esp[i]
        i+=1

    #TODO aggiungere il supporto a lettere separate (es aba = a2b)
    #raccogli lettere
    while esp[i] in LETT:
        if esp[i+1] in NUM:#raccogli cifre esponente
            cifre = ""#variabile temporanea in cui memorizza le cifre dell'esponente
            lett = esp[i]
            i += 1
            while esp[i] in NUM:
                cifre += esp[i]
                i+=1
            lx.update({lett:int(cifre)}) #inserisci nel dict
        elif esp[i]!=" ":
            lx.update({esp[i]:1}) #quando la lettera e' gia' presente
            i+=1
        else:
            pass #FIXME forse comportamneto indefinito

    if not len(lx) and x=="":
        x =0
    elif x=="":
        x = 1
    x = int(x)*neg
    return (x,lx)

def polinomizza(esp):
    """da espressione priva di parentesi ricava polinomio come lista
    di coppie [valore,lettere]"""
    esp = esp + " "
    out = []
    mon = ""
    for c in esp:
        if c == "+":
            out.append(monomizza(mon))
            mon = ""
        elif c == "-":
            out.append(monomizza(mon))
            mon = "-"
        else:
            mon += c
    out.append(monomizza(mon))

    return semplifica_polinomio(out)

def semplifica_polinomio(lista):
    l = list(lista) #elimina riferimento
    out = []
    while len(l)!=0: #passa per tutti gli elementi della lista
        j = 0

        simile = False
        while j<len(out):
            simile = False
            if compara_variabili(out[j][1],l[0][1]):#verifica che i monomi abbiano la stessa parte letterale
                v = out[j][0] #vecchio coeficente
                out[j] = (v+l[0][0], l[0][1])
                simile = True
                l.pop(0)
                break
            j +=1
        if not simile:
            out.append(l[0])
            l.pop(0)
	
    no0 = []
    while len(out)>0:#TODO optimize
        if out[0][0]!=0:
            no0.append(out[0])
        out.pop(0)
            #elimina coeficente 0
    return no0


### classi
#i monomi sono gestiti come coppie [coeficente,{let:esp,...}]


class Polinomio:
    def __init__(self,val):
        "accetta una stringa contenente un polinomio o un lista di monomi standard"
        # FORSE TODO spostare qui il codice della polinomizzazione
        #TODO aggiunger il supporo ai polinomi fratti
        if type(val)==type([]):
            self.pol = semplifica_polinomio(val)
        elif type(val)==type(""):
            self.pol = polinomizza(val)
        else:#tipo e' polinomio
            self.pol = list(val.pol)

    def __add__(self,altro):
        out = []
        out.extend(list(self.pol))
        out.extend(list(altro.pol))
        return Polinomio(semplifica_polinomio(out))

    def __sub__(self,altro):
        out=[]
        out.extend(self.pol)
        for mon in altro.pol:
            out.append([mon[0]*(-1),mon[1]])
        return Polinomio(semplifica_polinomio(altro))

    def __mul__(self,altro):
        out =[]
        for c1,v1 in self.pol:
            for c2,v2 in altro.pol:
                out.append([c1*c2,prodotto_variabili(v1,v2)])
        return Polinomio(semplifica_polinomio(out))

    def appendi(self,altro):
        self.pol.append(altro)
        self.pol = semplifica_polinomio(self.pol)

    def __str__(self):
        out = ""
        for i,j in self.pol:
            if i>=0:
                out += "+"
            out+=str(i)
            for v,e in j.items():
                out+= v
                if e>1:
                    out+=str(e)
        return out

    def esegui_operazione(self,operatore,altro):

        if operatore == "+":
            return self+altro

        if operatore == "-":
            return self-altro

        if operatore == "*":
            return self*altro

###test code

##print polinomizza("3a3b5*2b+3")
print (Polinomio("3q+4w-5e+6r"))
print (risolvi("a*(c+d)"))
a = "  "
while a != "":
    a = input("risolvi (vuoto per chiudere)-->")
    print (risolvi(a))
#print risolvi("a143+b")

#avvia console
p = Polinomio #accesso piu' semplice al Polinomi

vars = globals()
vars.update(locals())
readline.set_completer(rlcompleter.Completer(vars).complete)
readline.parse_and_bind("tab: complete")
shell = code.InteractiveConsole(vars)
shell.interact()
