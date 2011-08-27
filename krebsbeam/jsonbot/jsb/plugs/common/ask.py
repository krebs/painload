# jsb/plugs/common/ask.py
#
#

""" ask a user a question and relay back the response. """

## jsb imports

from jsb.lib.commands import cmnds
from jsb.lib.callbacks import callbacks
from jsb.lib.persist import PlugPersist
from jsb.lib.examples import examples
from jsb.lib.fleet import getfleet

## basic imports

import logging

## defines

defaultJID = 'bart@jsonbot.org' 

questions = PlugPersist('questions')
experts = PlugPersist('experts')
subjects = PlugPersist('subjects')

## ask-precondition

def askprecondition(bot, event):
    """ check to see whether the callback needs to be executed. """
    global questions
    if event.userhost in questions.data and not event.iscmnd: return True

## ask-callback

def askcallback(bot, event):
    """ this is the callbacks that handles the responses to questions. """
    sendto = questions.data[event.userhost]
    jid = []
    channels = []
    try: (printto, txt) = event.txt.split(':', 1)
    except ValueError: printto = False ; txt = event.txt
    txt = txt.strip()
    done = []
    fleet = getfleet()
    for botname, type, userhost, channel in sendto:
        if not printto or userhost != printto: continue
        askbot = fleet.makebot(type)
        if not askbot: askbot = fleet.makebot('xmpp', 'askxmppbot')
        logging.debug("ask - %s %s %s %s" % (botname, type, userhost, channel))
        if askbot:
            for jid in channel: askbot.say(channel, "%s says: %s" % (event.userhost, txt))
        else: logging.warn("ask - can't find %s bot in fleet" % type) ; continue
        try:
            questions.data[event.userhost].remove([botname, type, userhost, channel])
            questions.save()
        except ValueError: pass
        done.append(channel)
        break
    if done: event.reply('answer sent to ', done)

callbacks.add('MESSAGE', askcallback, askprecondition)
callbacks.add('DISPATCH', askcallback, askprecondition)
callbacks.add('WEB', askcallback, askprecondition)
callbacks.add('CONVORE', askcallback, askprecondition)
callbacks.add('PRIVMSG', askcallback, askprecondition)

## ask command

def handle_ask(bot, event):
    """ 
        arguments: <subject> <question> - this command lets you ask a question that gets dispatched to jabber 
        users that have registered themselves for that particular subject. 

    """
    try: subject, question = event.rest.split(' ', 1)
    except ValueError:
        event.missing('<subject> <question>')
        return
    try: expertslist = experts.data[subject]
    except KeyError:
        if '@' in subject: expertslist = [subject, ]
        else: expertslist = [defaultJID, ]
    fleet = getfleet()
    xmppbot = fleet.getfirstjabber()
    if xmppbot:
        for expert in expertslist: xmppbot.say(expert, "%s (%s) asks you: %s" % (event.userhost, bot.cfg.name, question))
    else:
        logging.warn("ask - can't find jabber bot in fleet")
        return
    asker = event.userhost
    for expert in expertslist:
        if not questions.data.has_key(expert): questions.data[expert] = []
        questions.data[expert].append([bot.cfg.name, bot.type, event.userhost, event.channel])
    questions.save()
    event.reply('question is sent to %s' % ' .. '.join(expertslist))

cmnds.add('ask', handle_ask, ['OPER', 'USER', 'GUEST'], options={'-w': False})
examples.add('ask', 'ask [group|JID] question .. ask a groups of users a question or use a specific JID', 'ask ask-bot what is the mercurial repository')

## ask-stop command

def handle_askstop(bot, event):
    """ no arguments - remove any waiting data for the user giving the command. """
    try: del questions.data[event.userhost]
    except KeyError: event.reply('no question running')

cmnds.add('ask-stop', handle_askstop, ['OPER', 'USER', 'GUEST'])
examples.add('ask-stop', 'stop listening to answers', 'ask-stop')

## ask-join command

def handle_askjoin(bot, event):
    """ arguments: <subject> - join the expert list of a subject. """
    if bot.type != 'xmpp':
        event.reply('this command only works in jabber')
        return    
    try: subject = event.args[0]
    except IndexError:
        event.missing('<subject>')
        return
    if not experts.data.has_key(subject): experts.data[subject] = []
    if not event.userhost in experts.data[subject]:
        experts.data[subject].append(event.userhost)
        experts.save()
    expert = event.userhost
    if not subjects.data.has_key(expert): subjects.data[expert] = []
    if not subject in subjects.data[expert]:
        subjects.data[expert].append(subject)
        subjects.save()
    event.done()

cmnds.add('ask-join', handle_askjoin, ['OPER', 'USER', 'GUEST'])
examples.add('ask-join', 'ask-join <subject> .. join a subject as an expert', 'ask-join ask-bot')

## ask-part command

def handle_askpart(bot, event):
    """ arguments: <subject> - leave the expert list of a subject. """
    if bot.type != 'xmpp':
        event.reply('this command only works in jabber')
        return    
    try: subject = event.args[0]
    except IndexError: event.missing('<subject>')
    try: experts.data[subject].remove(event.userhost)
    except (ValueError, KeyError): pass
    try: subjects.data[event.userhost].remove(subject)
    except (ValueError, KeyError): pass
    event.done()

cmnds.add('ask-part', handle_askpart, ['OPER', 'USER', 'GUEST'])
examples.add('ask-part', 'leave the subject expert list', 'ask-part ask-bot')

## ask-list command

def handle_asklist(bot, event):
    """ show all available subjects. """
    event.reply('available subjects: ', experts.data.keys())

cmnds.add('ask-list', handle_asklist, ['OPER', 'USER', 'GUEST'])
examples.add('ask-list', 'list available subjects', 'ask-list')

## ask-experts command

def handle_askexperts(bot, event):
    """ arguments: <subject> - show all the experts on a subject. """
    try: subject = event.args[0]
    except IndexError:
        event.missing('<subject>')
        return
    try: event.reply('experts on %s: ' % subject, experts.data[subject])
    except KeyError: event.reply('we dont know any experts on this subject yet')

cmnds.add('ask-experts', handle_askexperts, ['OPER', 'USER', 'GUEST'])
examples.add('ask-experts', 'list all experts on a subject', 'ask-experts ask-bot')

## ask-subjects command

def handle_asksubjects(bot, event):
    """ arguments: <JID> - show all the subjects an expert handles. """
    try: expert = event.args[0]
    except IndexError:
        event.missing('<JID>')
        return
    try: event.reply('subjects handled by %s: ' % expert, subjects.data[expert])
    except KeyError: event.reply('%s doesnt handle any subjects' % expert)

cmnds.add('ask-subjects', handle_asksubjects, ['OPER', 'USER', 'GUEST'])
examples.add('ask-subjects', 'list all the subjects an expert handles', 'ask-subjects bthate@gmail.com')
