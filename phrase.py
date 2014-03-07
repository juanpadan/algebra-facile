#!/usr/bin/python
LETT="qwertyuiopasdfghjklzxcvbnm"
NUM="1234567890"

import fractions
Frac = fractions.Fraction
#debug imports
import code
import readline
import rlcompleter
#fine debug imports

#TODO supporto divisione e frazioni

"""
lo scopo di questo modulo è fornire una classe Polinomio per gestire le
espressioni e un phraser che data una stringa ritorna un oggetto Polinomio
corrispondente all'espressione semplificata

"""


################################ polinomizzazione bruta ###################

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

def prodotto_variabili(a,b,esp_a = 1,esp_b=1):
    """da due dizionari lettera:esponente ritorna il prodotto e aggiungi un
    evntuale esponente per ciascun dizionario per cui sara' moltiplicato
    ciascun secondo termine del dizonario associato"""
    out = {}
    for lett, esp in a.items():
        out.update({lett:esp*esp_a})
    for lett, esp in b.items():
        if lett not in out:
            out.update({lett:esp*esp_b})
        else:
            t = out[lett]
            out.update({lett:esp*esp_b+t})
    return out


def interpreta_monomio(esp):
    """dato un monomio in forma ad esempio "5a2b4" lo trasforma in modo 
    uniforme, ritorna il valore intero, un dizionario lettera:esopnente"""
    esp += "\0"#TODO sostituire con \0
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
            cifre = ""
            #variabile temporanea in cui memorizza le cifre dell'esponente
            lett = esp[i]
            i += 1
            while esp[i] in NUM:
                cifre += esp[i]
                i+=1
            lx.update({lett:int(cifre)}) #inserisci nel dict
        elif esp[i]!="\0":
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


def monomizza(esp):#ok
    """trasforma in monomio un'espressione di sole moltiplicazioni,
    ritorna la coppia valore intero, lettere"""
    #todo verifica integrita'
    esp += "\0"
    numeratore = []#lista dei monomi in forma canonica al numeratore
    tmp = "" #stringa temporanea
    denominatore = [] 
    i = 0
    prodotto = False
    for c in esp:
        tmp += c
        if c in "*/":
            prodotto = True
            tmp = ""
            break
    
    if not prodotto:
        numeratore = [tmp]
    else:#tutto sto casino solo se ci sono un * o un /
        esp = "*"+esp # all'inizio della stringa mettti al numeratore
        while esp[i]!="\0":
            if esp[i] =="*":
                i+=1
                while esp[i] not in "*/\0": 
                    tmp +=esp[i]
                    i+=1
                numeratore.append(tmp)
                tmp = ""
                
            elif esp[i] =="/":
                i+=1
                while esp[i] not in "*/\0": 
                    tmp +=esp[i]
                    i+=1
                denominatore.append(tmp)
                tmp = ""
    
    #print(numeratore,"/",denominatore)
    if len(numeratore)==0:
        raise Exception("numeratore vuoto")
    coeficente = Frac(1,1)
    lett = {}
    for monomio in numeratore:
        t,lt = interpreta_monomio(monomio)
        lett = prodotto_variabili(lett,lt)
        coeficente *= t
    
    for monomio in denominatore:
        t,lt = interpreta_monomio(monomio)
        lett = prodotto_variabili(lett,lt,1,-1)
        coeficente /= t    
    

    return (coeficente,lett)


def polinomizza(esp):
    """da espressione priva di parentesi ricava polinomio come lista
    di coppie [valore,lettere]"""
    esp = esp
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
            if compara_variabili(out[j][1],l[0][1]):
                #^^^verifica che i monomi abbiano la stessa parte letterale
                
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


########## classi
#i monomi sono gestiti come coppie [coeficente,{let:esp,...}]
#il coeficente e' un oggetto Fractions





class Polinomio:
    def __init__(self,val=[],den=[]):
        """accetta una stringa contenente un polinomio 
        o un lista di monomi standard"""
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
    
    def __truediv__(self,altro):
        out =[]
        for c1,v1 in self.pol:
            for c2,v2 in altro.pol:
                out.append([c1/c2,prodotto_variabili(v1,v2,1,-1)])
        return Polinomio(semplifica_polinomio(out))



    def __str__(self):
        out = ""
        for i,j in self.pol:
            if i>=0:
                num = "+"+str(i.numerator)
            else:
                num=str(i.numerator)
                
            den = str(i.denominator)
            for v,e in j.items():#FIXME eliminare variabili con esponente 0
                if e == 1:
                    num += v
                elif e >1:
                    num += v+str(e)
                else:
                    den += v+str(int(-e))
            out += num
            if den != "1":
                out += "/"+den
        return out
    
    def __repr__(self):
        return self.__str__()


    def esegui_operazione(self,operatore,altro):
        if operatore == "+":
            return self+altro

        if operatore == "-":
            return self-altro

        if operatore == "*":
            return self*altro


########################### Risolutore ################################

def controlla_sintassi(esp):
    """questa funzione interrompe l'esecuzione del programma 
    (allo stato attuale) in caso di sintassi non valida"""
    #TODO aggiungere controlli piu' profondi:
    #riduzzione spazi
    #segni vaganti a inizio e fine linea
    par = 0 #controlla che ogni parentesi si chiuda
    for c in esp:
        if c == "(":
            par += 1
        elif c == ")":
            par -=1
        if par == -1:
            raise Exception("errore: parentesi non corrispondenti")
    if par != 0:
        raise Exception("errore: parentesi non corrispondenti")

def raggruppa(indice,stringa):
    """accetta indice di inizio della parentesi e la stringa, raggruppa 
    in una stringa il contenuto della parentesi. Ritorna il la coppia 
    (nuovoinidice,stringa)"""
    
    indice+=1
    inizio = indice
    par = 1
    out = ""
    while par>0:
        
        if stringa[indice]=="(":
            par +=1
        elif stringa[indice]==")":
            par -=1
        indice+=1
    return (indice,stringa[inizio:indice-1])



def tokenizza(esp):
    """separa monomi e se espressioni in una lista eg:
    [Polinomio(a),Polinomio(b),Polinomio(c),"*",Polinomio(d)]"""
    i = 0
    out = []
    tmp = ""
    while i<len(esp):
        
        if esp[i] in "+-":
            out.append(Polinomio(tmp))
            tmp = esp[i]
            i+=1
            
        elif esp[i] in "*/":
            if esp[i+1]=="(":
                out.append(Polinomio(tmp))
                out.append(esp[i])
                tmp=""
            elif esp[i-1]==")":    
                out.append(esp[i])
            else:
                tmp+=esp[i]#la monomizzazzione tratta gia' il prodotto
            i+=1
            
        elif esp[i] == "(":
            i,sub = raggruppa(i,esp)#i e' gia' al carattere successivo
            out.append(risolvi(sub))
        
        else:
            tmp+=esp[i]
            i+=1
            
    out.append(Polinomio(tmp))
    return list(out)

def risolvi(esp):
    controlla_sintassi(esp)#eccezione se invalida
    lista = tokenizza(esp)
    
    out = []
    i = 0
    while i<len(lista):
        if type(lista[i])==type(str()):
            out[-1] = out[-1].esegui_operazione(lista[i],lista[i+1])
            i+=2
        else:
            out.append(lista[i])
            i+=1
    pol = Polinomio([])
    for p in out:
        pol+=p
    return pol

###test code

print("semplifica un'espressione algebrica (vuoto per chiudere)")
print("per convenzione 3ac/2b=(3ac)/(2b)")
print("esplicitare la moltiplicazione prima di una parentesi:")
print("21(a+b) = 21+a+b, 21*(a+b) = 21a+21b")
a = "babagia"
while a != "":
    a = input("-->")
    print (risolvi(a))


#avvia console
p = Polinomio #accesso piu' semplice al Polinomi

vars = globals()
vars.update(locals())
readline.set_completer(rlcompleter.Completer(vars).complete)
readline.parse_and_bind("tab: complete")
shell = code.InteractiveConsole(vars)
shell.interact()
