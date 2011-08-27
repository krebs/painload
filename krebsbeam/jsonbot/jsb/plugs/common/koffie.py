# jsb/plugs/common/koffie.py
#
# Made by WildRover and Junke1990

""" schenk wat koffie! """

## jsb imports

from jsb.lib.commands import cmnds
from jsb.lib.examples import examples

## basic imports

import os
import string
import random

## defines

koffie = []
thee = []
bier = []
wijn = []
fris = []
taart = []
koek = []
chips = []
soep = []
sex = []
roken = []
beledig = []

## init function

def init():
    global koffie
    global thee
    global bier
    global wijn
    global fris
    global taart
    global koek
    global chips
    global soep
    global sex
    global roken
    global beledig
    for i in  koffietxt.split('\n'):
        if i:
            koffie.append(i.strip())
    for i in theetxt.split('\n'):
        if i:
            thee.append(i.strip())
    for i in biertxt.split('\n'):
        if i:
            bier.append(i.strip())
    for i in wijntxt.split('\n'):
        if i:
            wijn.append(i.strip())
    for i in fristxt.split('\n'):
        if i:
            fris.append(i.strip())
    for i in taarttxt.split('\n'):
        if i:
            taart.append(i.strip())
    for i in koektxt.split('\n'):
        if i:
            koek.append(i.strip())
    for i in chipstxt.split('\n'):
        if i:
            chips.append(i.strip())
    for i in soeptxt.split('\n'):
        if i:
            soep.append(i.strip())
    for i in sextxt.split('\n'):
        if i:
            sex.append(i.strip())
    for i in rokentxt.split('\n'):
        if i:
            roken.append(i.strip())
    for i in beledigtxt.split('\n'):
        if i:
            beledig.append(i.strip())
    return 1

## functions

def do(bot, ievent, txt):
    if not bot.isgae and not bot.allowall: bot.action(ievent.channel, txt, event=ievent)
    else: bot.say(ievent.channel, txt, event=ievent)

## koffie command

def handle_koffie(bot, ievent):
    """ arguments: [<nick>] - get/give a coffee """
    rand = random.randint(0,len(koffie)-1)
    try:
        input = ievent.args[0]
        nick = '%s' % input
    except:
        if len('%s') >= 0: nick = ievent.nick
    do(bot, ievent, koffie[rand] + " " + nick)

cmnds.add('koffie', handle_koffie, 'USER')
examples.add('koffie', 'get a koffie quote', 'koffie')

## thee command

def handle_thee(bot, ievent):
    """ arguments: [<nick>] - get/give a thee """
    rand = random.randint(0,len(thee)-1)
    try:
        input = ievent.args[0]
        nick = '%s' % input
    except:
        if len('%s') >= 0: nick = ievent.nick
    do(bot, ievent, thee[rand] + " " + nick)

cmnds.add('thee', handle_thee, 'USER')
examples.add('thee', 'get an thee', 'thee')

## bier command

def handle_bier(bot, ievent):
    """ arguments: [<nick>] - get a beer  """
    rand = random.randint(0,len(bier)-1)
    try:
        input = ievent.args[0]
        nick = '%s' % input
    except:
        if len('%s') >= 0: nick = ievent.nick
    do(bot, ievent, bier[rand] + " " + nick)

cmnds.add('bier', handle_bier, 'USER')
examples.add('bier', 'get a bier', 'bier')

## wijn command

def handle_wijn(bot, ievent):
    """ arguments: [<nick>] - get a wine  """
    rand = random.randint(0,len(wijn)-1)
    try:
        input = ievent.args[0]   
        nick = '%s' % input
    except:
        if len('%s') >= 0: nick = ievent.nick
    do(bot, ievent, wijn[rand] + " " + nick)

cmnds.add('wijn', handle_wijn, 'USER')
examples.add('wijn', 'get a wijn', 'wijn')

## fris command

def handle_fris(bot, ievent):
    """ arguments: [<nick>] - get a fris  """
    rand = random.randint(0,len(fris)-1)
    try:
        input = ievent.args[0]
        nick = '%s' % input
    except:
        if len('%s') >= 0: nick = ievent.nick
    do(bot, ievent, fris[rand] + " " + nick)

cmnds.add('fris', handle_fris, 'USER')
examples.add('fris', 'get a fris', 'fris')

## taart command

def handle_taart(bot, ievent):
    """ arguments: [<nick>] - get a taart  """
    rand = random.randint(0,len(taart)-1)
    try:
        input = ievent.args[0]
        nick = '%s' % input
    except:
        if len('%s') >= 0: nick = ievent.nick
    do(bot, ievent, taart[rand] + " " + nick)

cmnds.add('taart', handle_taart, 'USER')
examples.add('taart', 'get a taart', 'taart')

## koek command

def handle_koek(bot, ievent):
    """ arguments: [<nick>] - get a koek  """
    rand = random.randint(0,len(koek)-1)
    try:
        input = ievent.args[0]
        nick = '%s' % input
    except:
        if len('%s') >= 0: nick = ievent.nick
    do(bot, ievent, koek[rand] + " " + nick)

cmnds.add('koek', handle_koek, 'USER')
examples.add('koek', 'get a koek', 'koek')

cmnds.add('koekje', handle_koek, 'USER')
examples.add('koekje', 'get a koekje', 'koekje')

## chips command

def handle_chips(bot, ievent):
    """ arguments: [<nick>] - get a chips  """
    rand = random.randint(0,len(chips)-1)
    try:
        input = ievent.args[0]
        nick = '%s' % input
    except:
        if len('%s') >= 0: nick = ievent.nick
    do(bot, ievent, chips[rand] + " " + nick)

cmnds.add('chips', handle_chips, 'USER')
examples.add('chips', 'get a chips', 'chips')

## soep command

def handle_soep(bot, ievent):
    """ arguments: [<nick>] - get a soep  """
    rand = random.randint(0,len(soep)-1)
    try:
        input = ievent.args[0]
        nick = '%s' % input
    except:
        if len('%s') >= 0: nick = ievent.nick
    do(bot, ievent, soep[rand] + " " + nick)

cmnds.add('soep', handle_soep, 'USER')
examples.add('soep', 'get a soep', 'soep')

## sex command

def handle_sex(bot, ievent):
    """ arguments: [<nick>] - get a sex  """
    rand = random.randint(0,len(sex)-1)
    try:
        input = ievent.args[0]
        nick = '%s' % input
    except:
        if len('%s') >= 0: nick = ievent.nick
    do(bot, ievent, sex[rand] + " " + nick)

cmnds.add('sex', handle_sex, 'USER')
examples.add('sex', 'get a sex', 'sex')

## roken command

def handle_roken(bot, ievent):
    """ arguments: [<nick>] - get a roken  """
    rand = random.randint(0,len(roken)-1)
    try:
        input = ievent.args[0]
        nick = '%s' % input
    except:
        if len('%s') >= 0: nick = ievent.nick
    do(bot, ievent, roken[rand] + " " + nick)

cmnds.add('roken', handle_roken, 'USER')
examples.add('roken', 'get a roken', 'roken')

## beledig command

def handle_beledig(bot, ievent):
    """ arguments: [<nick>] - get/give an belediging  """
    rand = random.randint(0,len(beledig)-1)
    try:
        input = ievent.args[0]
        nick = '%s' % input
    except:
        if len('%s') >= 0: nick = ievent.nick
    do(bot, ievent, beledig[rand] + " " + nick)

cmnds.add('beledig', handle_beledig, 'USER')
examples.add('beledig', 'get/give an belediging ', 'beledig')

## text definitions

koffietxt = """ schenkt een kopje koffie in voor
schenkt een kopje koffie wiener melange in voor
schenkt een kopje espresso voor je in voor
schenkt een kopje arabica voor je in voor
schenkt je een kopje koffie verkeerd in voor
schenkt een kopje cappuccino in voor
schenkt een kopje cafe choco in voor
schenkt je een kopje koffie van gisteren in voor
vult een kopje met decafe voor
schenkt een kopje toebroek in voor
maak het gerust zelf,
geeft een glas irish-coffee aan
geeft een glas french-coffee aan
schenkt een kopje turkse koffie in voor
schenkt een kopje americano in voor
schenkt een kopje doppio in voor
schenkt een kopje espresso ristretto in voor
schenkt een kopje caffe latte in voor
schenkt een kopje espresso macchiato in voor
schenkt een kopje latte macchiato in voor
schenkt een kopje espresso romano in voor
schenkt een kopje con panna voor in voor
schenkt een kopje mocha in voor
"""

theetxt = """ maak het gerust zelf,
schenkt een kopje groene thee in voor
ja lekker heh, 
schenkt een kopje mintthee in voor 
schenkt een kopje brandnetelthee in voor 
schenkt een kopje bosvruchtenthee in voor
schenkt een kopje citroenthee in voor
schenkt een kopje rooibosthee in voor
schenkt een heerlijk kopje lavendelthee in voor
maakt een kopje fruity forest voor
maakt een kopje tempting red voor
maakt een kopje early grey voor
"""

biertxt = """ reikt een flesje hertog-jan aan voor
tapt een glas witbier voor
geeft een flesje amstel aan
geeft een flesje jupiler aan
geeft een flesje bavaria aan
geeft een flesje grolsch aan
pak het gerust zelf,
geeft een flesje hoegaarden aan
geeft een flesje grimbergen aan
reikt een flesje dommelsch aan voor 
reikt een flesje brand aan voor
schenkt een glas duvel in voor
schenkt een glas chouffe in voor
"""

wijntxt = """ trekt een fles rode wijn open.
geeft een glas rode wijn aan
geeft een glas witte wijn aan
geeft een glas rose aan
geeft een glas champagne aan
trekt een fles appelwijn open, tast toe,
geeft een glas cider aan
geeft een glas champagne aan
pak het gerust zelf maar,
morst rode wijn over je witte shirt, oops... sorry,
ja lekker,
witte, rode of rose, 
geeft een glas droge witte wijn aan
geeft een glas zoete witte wijn aan
trekt de kurk van een fles witte wijn, zuipt hem helemaal leeg *hips* en proost,
schenkt een glas goedkope tafelwijn in voor
een glas chateaux-migraine voor
trekt een fles hema-huiswijn open en schenkt vast een kom in voor
"""

fristxt = """ zet de deur en het raam open voor
geeft een glas cola aan
geeft een glas cola light aan
geeft een glas cherry coke aan
geeft een glas pepsi max aan
geeft een glas sinas aan
geeft een glas fanta aan
geeft een glas sprite aan
geeft een glas 7-up aan
pakt een flesje chocomel voor
geeft een glas jus d'orange aan
schenkt een glas appelsap in voor
sorry, het is te koud voor fris,
wijst naar een lege koelkast. sorry
ja lekker, doe mij ook wat,
"""

taarttxt = """ geeft je een punt appletaart met lekker veel slagroom.
bak het gerust zelf, alles ligt klaar voor je,
geeft een taart met kaas, salami, oregano en knoflook aan
geeft een punt chocoladetaart aan
geeft een punt slagroomtaart aan
geeft een punt appeltaart aan
geeft een punt aardbeientaart aan
geeft een punt vruchtentaart aan
geeft een punt advocaattaart aan
geeft een punt abrikozentaart aan
geeft een punt appelcitroentaart aan
geeft een punt appelkruimeltaart aan
geeft een punt bananentaart aan
geeft een punt boerenjongenstaart aan
geeft een punt bosvruchtentaart aan
geeft een punt champagnetaart aan
geeft een punt kersentaart aan
geeft een punt rijsttaart aan
geeft een punt mokkataart aan
geeft een punt notentaart aan
geeft een punt peche-melbataart aan
geeft een punt perentaart aan
geeft een punt schwarzwaldertaart aan
geeft een punt stroopwafeltaart aan
geeft een punt tiramisutaart aan
geeft een punt yoghurt-sinaastaart aan
geeft een punt zwitserse-roomtaart aan
"""

koektxt = """ geeft een lange vinger aan
geeft een speculaasje aan
geeft een stroopwafel aan
geeft een zandkoekje aan
geeft een sprits aan
geeft een muffin aan
geeft een slagroomsoesje aan
geeft een walnootkoekje aan
geeft een lekker kaaskoekje aan
geeft een honingkoekje aan
geeft een hazelnootkoekje aan
geeft een gemberkoekje aan
geeft een eclair aan
geeft een cremerolletje aan
geeft een chocoladekoekje aan
geeft een pindarotsje aan
geeft een bokkenpootje aan
geeft een lebkuchen aan
geeft een amandelkoekje aan
bak ze gerust zelf,
"""

chipstxt = """ geeft je een bakje bugles.
geeft een zakje naturel chips aan
pakt een zakje wokkels voor
geeft een zakje paprika chips aan
geeft een zakje bolognese chips aan
geeft een zakje barbecue ham chips aan
geeft een zakje cheese onion aan
geeft een zakje mexican salsa aan
pakt een zakje bugles voor
geeft een zakje hamka's.
*crunch* dank je,
loert tevergeefs in een lege chipszak voor
ja lekker,
"""

soeptxt = """ geeft een kom aspergesoep aan
geeft een kom bospaddestoelensoep aan
geeft een kom frisse erwtensoep aan
geeft een kom kip tikka soep aan
geeft een kom kruidige tomatensoep aan
geeft een kom mosterdsoep aan
geeft een kom ossenstaartsoep aan
geeft een kom pittige tomatensoep aan
geeft een kom romige kippensoep aan
geeft een kom romige tomatensoep aan
geeft een bord boerengroentesoep aan
geeft een kom champignonsoep aan
geeft een kom erwtensoep aan
geeft een kom goulashsoep aan
geeft een kom kippensoep aan
geeft een kom tomaten-creme soep aan
geeft een kom tomatensoep aan
geeft een kom bruine bonensoep aan
geeft een kom chinese tomatensoep aan
geeft een kom groentesoep aan
geeft een kom tomaten-groentesoep aan
geeft een kom uiensoep aan
geeft een kom kerrie-cremesoep aan
maak voor ons ook wat,
staart in een lege pan voor
vist een ouwe schoen uit de bouillon voor
"""

sextxt = """ huh? moeilijk? waar?
Snufj!
Nee nu niet, ik heb hoofdpijn.
Wacht dan doe ik een condoom aan.
Veel te koud voor sex.
Veel te warm voor sex.
Ja strakjes, eerst nog even dit afmaken...
Ja lekker!
Moo!
Heb je de sleutel van m'n kuisheidsgordel dan?
Rook jij ook na de sex?
Mag 't licht uit?
"""

rokentxt = """ Er is maar 1 weg na de longen en die moet geasfalteerd worden
Ohhh!!! heerlijk!!!.....
Riet rokers sterven ook!
Het nieuwe lied van K3: Rokus Spokus, iedereen kan roken!
Elk pakje sigaretten verkort je leven met 11 minuten, elke vrijjpartij verlengt je leven met 15 minuten. conclusie: ROKERS NEUK VOOR JE LEVEN!
Niet zeiken lekker ding, ik betaal jouw belasting!
Afspraak: Rook jij mijn laatste, koop jij een nieuwe.
Als mijn moeder dit pakje vind is het van jou!
Roken werkt ontspannend en is dus goed tegen hartklachten en algemene  stress.
Ex-rokers moeten helemaal hun bek houden!
Niet roken bespaard geld? waarom heb jij t dan nooit?
Koop je eigen pakje KLOOTZAK!
Ik rook dus ik ben rijk, neuken?
Ik geef om jouw gezondheid dus blijf godverdomme van mijn peuken af!
Roken is slecht voor de zwangerschap, dat condoom kun je dus in je zak houden.
Roken is ongezond..... een dikke vatsige vetklep ook!
Roken na de sex houd mijn gezondheid in balans.
Moet ik er een bewaren voor na de sex of rook je niet?
Heb je last van je keel door mijn gerook? moet je er ook een opsteken, ik heb nooit last!
Wie meerookt hoort ook me te betalen!
Stoppen? Ik probeer het zo'n 20 keer per dag!
"""

beledigtxt = """schopt
misbruikt
verhuurt
slaat
mept
gooit koffie over
bitchslapt
schiet op
schijt in de mond van
vist in het aquarium van
pakt een koekenpan en slaat daarmee
hackt
stampt zo hard tusse de noten dat je je kindergeld kwijt bent, 
moont
castreert
verloot
"""
