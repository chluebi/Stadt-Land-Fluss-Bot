import discord
import random
import asyncio

client = discord.Client()

#these are setup variables that get set at the beginning of the game (and generally don't change)
categories = []
roundtime = 0 #how long a round takes
roundmax = 0 #for how many rounds the game should go on
jointime = 20 #for how many seconds the jointime goes on
judgetime = 60 #how long people have time to judge the answers
breaktime = 15 #how long players have to wait between rounds

mainchannel = 0 #the channel where the joining takes place
host = client.user

#these variables reset every round
letter = ''
timer = 0 #timer of each round
judgemsg = [] #list of all the messages in the "judge" phase
judgeid = [] #list of all the message ids in the "judge" phase
judgeyes = [] #list of all the positive judges
judgeuser = [] #list of the people that gave the "judge" answers
donemsg = 0 #message at the end of the judge phase
peopledone = 0 #amount of people reacted to the done message
pointsround = [] #amount of points each player got this round
answermsg = [] #list of all the messages in the "playing" phase
endplayer = '' #the name of the player who ended the round early

answers = [] # 2-dimensional array which saves all answers of a round

#these variables steer the whole game
gamestage = 'none'
party = [] # all participants
round = 0 #at which round of the game
points = [] # list of all the points the users have
letterlist = [] #letters that already were in the game once


#misc variables
reactors = []   # the name list of people reacted to the join message
joinid = 0  # the id of the message to join
em = 0 # the embed used for the setup complete/join message




def reset():

    print('resetting')
    global categories
    global roundtime
    global em
    global party
    global round
    global timer
    global letter
    global letterlist
    global answers
    global answermsg
    global mainchannel
    global answermsg
    global donemsg
    global judgemsg
    global judgeyes
    global judgeid
    global judgeuser
    global pointsround
    global peopledone
    global points
    global host
    global joinid
    global reactors
    global gamestage
    global breaktime

    reactors = []  # the name list of people reacted to the join message
    party = []  # all participants
    joinid = 0  # the id of the message to join
    em = 0  # the embed used for the setup complete/join message
    gamestage = 'reset'
    categories = []
    roundtime = 0  # how long a round takes
    round = 0  # at which round of the game
    timer = 10  # timer of each round
    #host = client.user
    letter = ''
    letterlist = []  # letters that already were in the game once
    answermsg = []  # list of all the messages in the "playing" phase
    mainchannel = 0  # the channel where the joining takes place
    judgemsg = []  # list of all the messages in the "judge" phase
    judgeid = []  # list of all the message ids in the "judge" phase
    judgeyes = []  # list of all the positive judges
    judgeuser = []  # list of the people that gave the "judge" answers
    donemsg = 0  # message at the end of the judge phase
    peopledone = 0  # amount of people reacted to the done message
    pointsround = []  # amount of points each player got this round

    answers = []  # 2-dimensional array which saves all answers of a round
    points = []  # list of all the points the users have


    gamestage = 'none'


def is_int(value):

    try:
        prefix = int(value) + 1
        return True
    except ValueError:
        print('ValueError')
        return False


async def countdown():
    await client.wait_until_ready()
    global gamestage
    global timer
    global mainchannel
    global answermsg
    global roundtime
    global endplayer
    global judgetime
    global donemsg
    while not client.is_closed:
            timer -= 1
            await asyncio.sleep(1)
            if timer == 0 and gamestage == 'playing':
                print('going to judging')
                gamestage = 'judging'
                for n in range(len(party)):
                    desc = 'Die Runde ist vorbei, bitte begib dich zurück in den Hauptchat.'
                    em = discord.Embed(title='Stadt, Land, Fluss', description=desc)

                    if not endplayer == '':
                        em.add_field(name='Vorzeitiges Beenden', value=endplayer + ' hat die Runde vorzeitig beendet', inline=False)

                    await client.send_message(party[n], embed=em)

                await asyncio.sleep(2)
                desc = 'Die Runde ist vorbei, bitte begib dich zurück in den Hauptchat.'
                em = discord.Embed(title='Stadt, Land, Fluss', description=desc)

                if not endplayer == '':
                    em.add_field(name='Vorzeitiges Beenden', value=endplayer + ' hat die Runde vorzeitig beendet',inline=False)


                client.send_message(mainchannel, embed=em)


            if timer % 5 == 0 and gamestage == 'playing' and not timer == roundtime:
                for n in range(len(party)):

                    msg = 'Runde {}: **{}** \n'.format(round, letter)
                    msg2 = ''
                    for i in range(len(categories)):
                        m = i + 1
                        msg2 = msg2 + (str(m) + '. ' + categories[i] + ': ' + answers[n][i] + '\n')
                    msg3 = '\n antworte in folgendem Format: *1 Afrika*'
                    msg4 = '\n \n ``Zeit verbleibend: ' + str(timer) + '``'
                    if n >= len(answermsg):
                        n = len(answermsg)-1
                    if n < 0:
                        n = 0
                    print(n)
                    print(answermsg)
                    if timer > 0:
                        await client.edit_message(answermsg[n], msg + msg2 + msg3 + msg4)
                    else:
                        await client.edit_message(answermsg[n], msg + msg2 + msg3)

            if timer == 0 and gamestage == 'judge':
                gamestage = 'judgedone'
                desc = 'Bewertungsphase beendet'
                em = discord.Embed(title='Stadt, Land, Fluss', description=desc)
                await client.send_message(mainchannel, embed=em)


            if timer % 5 == 0 and gamestage == 'judge' and not timer == judgetime:
                msg = 'Fertig mit Bewerten? Klicke auf den grünen Hacken unter dieser Nachricht. \n'
                msg2 = '``Zeit verbleibend: {}``'.format(str(timer))
                if timer > 0:
                    await client.edit_message(donemsg, msg + msg2)
                else:
                    await client.edit_message(donemsg, msg)





@client.event
async def on_message(message):
    global gamestage

    if gamestage == 'reset':
        return

    global categories
    global roundtime
    global em
    global party
    global round
    global timer
    global letter
    global letterlist
    global answers
    global answermsg
    global mainchannel
    global answermsg
    global donemsg
    global judgemsg
    global judgeyes
    global judgeid
    global judgeuser
    global pointsround
    global peopledone
    global points
    global host
    global roundmax
    global jointime
    global endplayer
    global judgetime
    global breaktime

    # split the message to better handle the different inputs
    msgsplit = message.content.split(' ')
    print(str(msgsplit))


    # info and debug commands
    if msgsplit[0] == '$status':
        print('Gamestage: ' + gamestage)

    # the following are host commands
    if message.author == host and message.channel == mainchannel:

        if msgsplit[0] == '$reset':
            reset()
            return


        if msgsplit[0] == '$start' and gamestage == 'join':
            gamestage = 'starting up'
            return

        if msgsplit[0] == '$continue' and gamestage == 'continue':
            gamestage = 'new round'
            return

        if msgsplit[0] == '$endgame':
            await client.send_message(mainchannel, 'Spiel vorzeitig beendet von {}.'.format(host.display_name))
            gamestage = 'gameended'


            if round > 0:
                ranking = [[0 for x in range(3)] for y in range(len(party))]

                for y in range(len(party)):
                    ranking[y][0] = party[y].display_name
                    ranking[y][1] = points[y]
                    ranking[y][2] = pointsround[y]

                print(ranking)

                ranking.sort(key=lambda x: x[1], reverse=True)

                print(ranking)

                msg = 'Punktestand: \n ```\n'
                msg2 = ''

                for i in range(len(party)):
                    msg2 = msg2 + ranking[i][0] + ': ' + str(ranking[i][1]) + ' (+' + str(ranking[i][2]) + ')\n'

                msg2 = msg2 + '```'

                await client.send_message(mainchannel, msg + msg2)

            desc = 'Vielen Dank fürs Spielen.'
            em = discord.Embed(title='Stadt, Land, Fluss', description=desc)
            await client.send_message(message.channel, embed=em)
            reset()
            return


        if msgsplit[0] == '$change' and not (gamestage == 'none' or gamestage == 'setup'):
            oldgamestage = gamestage
            gamestage = 'change'
            if msgsplit[1] == 'roundtime':
                if is_int(msgsplit[2]):
                    await client.send_message(message.channel, 'Rundenlänge erfolgreich von {} auf {} geändert.'.format(roundtime,msgsplit[2]))
                    roundtime = max(-1,int(msgsplit[2]))
                else:
                    await client.send_message(message.channel, 'Bitte gib eine ganze Zahl ein.')

            elif msgsplit[1] == 'roundmax':
                if is_int(msgsplit[2]):
                    await client.send_message(message.channel, 'Anzahl Runden erfolgreich von {} auf {} geändert.'.format(roundmax,msgsplit[2]))
                    roundmax = max(-1,int(msgsplit[2]))
                else:
                    await client.send_message(message.channel, 'Bitte gib eine ganze Zahl ein.')

            elif msgsplit[1] == 'judgetime':
                if is_int(msgsplit[2]):
                    await client.send_message(message.channel, 'Bewertungszeit erfolgreich von {} auf {} geändert.'.format(judgetime,msgsplit[2]))
                    judgetime = max(-1,int(msgsplit[2]))
                else:
                    await client.send_message(message.channel, 'Bitte gib eine ganze Zahl ein.')

            elif msgsplit[1] == 'breaktime':
                if is_int(msgsplit[2]):
                    await client.send_message(message.channel, 'Länge der Pausen erfolgreich von {} auf {} geändert.'.format(breaktime,msgsplit[2]))
                    breaktime = max(-1,int(msgsplit[2]))
                else:
                    await client.send_message(message.channel, 'Bitte gib eine ganze Zahl ein.')

            else:
                print('bad argument for &change')
            gamestage = oldgamestage





    # script for starting a new round
    if gamestage == 'roundend' and message.author == client.user:

        gamestage = 'continue'
        i = 0

        if breaktime > 0:
            breakmsg = await client.send_message(mainchannel,'``Die nächste Runde startet in {} Sekunden``'.format(breaktime))
        else:
            breakmsg = await client.send_message(mainchannel,'Die nächste Runde startet bald')


        while i != breaktime:
            await asyncio.sleep(1)
            if (breaktime-i-1) % 2 == 0:
                if breaktime > 0:
                    await client.edit_message(breakmsg,'``Die nächste Runde startet in {} Sekunden``'.format(breaktime-i-1))
            i += 1

            if gamestage != 'continue':
                break



        gamestage = 'newround'

        answermsg = []  # list of all the messages in the "playing" phase
        judgemsg = []  # list of all the messages in the "judge" phase
        judgeid = []  # list of all the message ids in the "judge" phase
        judgeyes = []  # list of all the positive judges
        judgeuser = []  # list of the people that gave the "judge" answers
        donemsg = 0  # message at the end of the judge phase
        peopledone = 0  # amount of people reacted to the done message
        pointsround = []  # amount of points each player got this round

        desc = 'Die Runde startet in 10 Sekunden, die Antworten werden in Direktnachrichten mit dem Bot geschrieben.'
        em = discord.Embed(title='Stadt, Land, Fluss', description=desc)
        await client.send_message(message.channel, embed=em)

        for i in range(len(party)):
            await client.send_message(party[i], embed=em)

        answers = [[''] * len(categories) for i in range(len(party))]
        print(answers)

        await asyncio.sleep(10)
        timer = roundtime
        gamestage = 'playing'
        round += 1
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVXYZ'
        letter = 0
        while letter == 0 or letter in letterlist:
            letter = alphabet[random.randint(1, len(alphabet) - 1)]

        letterlist.append(letter)

        msg = 'Runde {}: **{}** \n'.format(round, letter)
        msg2 = ''
        for i in range(len(categories)):
            m = i + 1
            msg2 = msg2 + (str(m) + '. ' + categories[i] + '\n')

        msg3 = '\n antworte in folgendem Format: *1 Afrika*'


        for i in range(len(party)):
            sent = await client.send_message(party[i], msg + msg2 + msg3)
            answermsg.append(sent)
            pointsround.append(0)


    # script for gameend and ranking
    if gamestage == 'gameend' and message.author == client.user:
        gamestage = 'gameended'

        desc = 'Vielen Dank fürs Spielen.'
        em = discord.Embed(title='Stadt, Land, Fluss', description=desc)
        await client.send_message(message.channel, embed=em)

        reset()


    # script for points
    if gamestage == 'judgedone' and message.author == client.user:
        gamestage = 'points'
        print(judgeuser)
        pointsround = []
        for i in range(len(party)):
            pointsround.append(0)

        for k in range(len(judgeuser)):
            if judgeyes[k] > -1:
                auth = judgeuser[k]
                authindex = party.index(auth)
                pointsround[authindex] += 1

        print(pointsround)


        for i in range(len(party)):
            points[i] += pointsround[i]

        ranking = [[0 for x in range(3)] for y in range(len(party))]

        for y in range(len(party)):
            ranking[y][0] = party[y].display_name
            ranking[y][1] = points[y]
            ranking[y][2] = pointsround[y]

        print(ranking)

        ranking.sort(key=lambda x: x[1], reverse=True)

        print(ranking)

        msg = 'Punktestand: \n ```\n'
        msg2 = ''

        for i in range(len(party)):
            msg2 = msg2 + ranking[i][0] + ': ' + str(ranking[i][1]) + ' (+' + str(ranking[i][2]) + ')\n'

        msg2 = msg2 + '```'

        await client.send_message(mainchannel, msg + msg2)
        await asyncio.sleep(1)

        """
        for i in range(len(party)):
            points[i] += pointsround[i]
            msg2 = msg2 + party[i].display_name + ': ' + str(points[i]) + ' (+ ' + str(pointsround[i]) + ')\n'
        msg2 = msg2 + '```'
        await client.send_message(mainchannel,msg + msg2)
        await asyncio.sleep(5)
        """

        if gamestage == 'none':
            return

        if round == roundmax:
            gamestage = 'gameend'
            msg = 'Das Spiel ist abgeschlossen.'
            await client.send_message(mainchannel, msg)
        else:
            gamestage = 'roundend'
            msg = 'Runde {} abgeschlossen. Starte nächste Runde...'.format(round)
            await client.send_message(mainchannel,msg)





    # script for judging
    if gamestage == 'judging' and message.author == client.user:
        timer = judgetime
        gamestage = 'judge'
        desc = 'Bewerte die Antworten deiner Mitspieler.'
        em = discord.Embed(title='Stadt, Land, Fluss', description=desc)
        await client.send_message(mainchannel, embed=em)

        for s in range(len(categories)):
            msg = '**' + categories[s] + '**'
            await client.send_message(mainchannel, msg)
            for z in range(len(party)):
                if not answers[z][s] == '':
                    msg = party[z].display_name + ': ' + answers[z][s]
                    rea = await client.send_message(mainchannel, msg)
                    judgemsg.append(rea)
                    judgeid.append(rea.id)
                    judgeyes.append(0)
                    judgeuser.append(party[z])
                    await client.add_reaction(rea,'✅')
                    await client.add_reaction(rea,'❌')
                    await asyncio.sleep(2)

        msg = 'Fertig mit Bewerten? Klicke auf den grünen Hacken unter dieser Nachricht.'

        donemsg = await client.send_message(mainchannel,msg)
        await client.add_reaction(donemsg,'✅')
        print(donemsg)



    # script for the game
    if gamestage == 'playing':
        print('playing')

        if not message.channel.is_private:
            return

        if not message.author in party:
            return
        userindex = party.index(message.author)


        if msgsplit[0] == '$stop':
            if not '' in answers[userindex]:
                timer = 1
                endplayer = message.author.display_name
                return
            else:
                msg = 'Du hast noch nicht bei allen Kategorien ein Wort.'
                await client.send_message(message.author, msg)


        try:
            prefix = int(msgsplit[0]) + 1
        except ValueError:
            print('ValueError')
            return

        prefix -= 1

        if not (prefix > 0 and prefix <= len(categories)):
            return



        answers[userindex][prefix-1] = ' '.join(msgsplit[1:len(msgsplit)])[:100]
        print(answers)

        if not '' in answers[userindex]:
            msg = 'Du hast zu allen Kategorien eine Antwort aufgeschrieben. Schreibe "$stop" um die Runde zu stoppen.'
            await client.send_message(message.author, msg)

        msg = 'Runde {}: **{}** \n'.format(round, letter)
        msg2 = ''
        for i in range(len(categories)):
            m = i + 1
            msg2 = msg2 + (str(m) + '. ' + categories[i] + ': ' + answers[userindex][i] + '\n')
        msg3 = '\n antworte in folgendem Format: *1 Afrika*'
        msg4 = '\n \n ``Zeit verbleibend: ' + str(timer) + '``'

        if timer > 0:
            await client.edit_message(answermsg[userindex], msg + msg2 + msg3 + msg4)
        else:
            await client.edit_message(answermsg[userindex], msg + msg2 + msg3)


    # script for joining
    if msgsplit[0] != 'Spiel' and msgsplit[0] != 'Klicke' and message.author == client.user and gamestage == 'joinstart':
        gamestage = 'join'
        reactmsg = await client.send_message(message.channel, 'Klicke den grünen Hacken um beizutreten!')

        global joinid
        joinid = reactmsg.id
        print(joinid)

        await client.add_reaction(reactmsg,'✅') #add the first reaction

        global reactors
        i = 0

        while i != jointime: #wait "timer" seconds
            await asyncio.sleep(1)
            msg = 'Klicke den grünen Hacken um beizutreten! \n'
            msg3 = ' ``{} Sekunden übrig`` \n'.format(jointime-1-i)
            if len(reactors) > 0:
                msg2 = '\n' + 'Teilnehmer: \n' + '```\n' + '\n'.join(reactors) + '```' #send the participants list
            else:
                msg2 = '' #if nobody joins, we don't need to send the participant list

            if (jointime-i-1) % 2 == 0:
                if  (jointime-i-1) > 0:
                    await client.edit_message(reactmsg, msg + msg3 + msg2)
                else:
                    await client.edit_message(reactmsg, msg + msg2)

            if gamestage == 'none':
                return

            if gamestage == 'starting up':
                break
            i += 1


        gamestage = 'starting up'
        desc = 'Das Spiel startet in 10 Sekunden, die Antworten werden in Direktnachrichten mit dem Bot geschrieben.'
        em = discord.Embed(title='Stadt, Land, Fluss',description=desc)
        await client.send_message(message.channel, embed=em)

        for i in range(len(party)):
            await client.send_message(party[i],embed=em)
            points.append(0)

        endplayer = ''
        answers = [[''] * len(categories) for i in range(len(party))]
        print(answers)

        await asyncio.sleep(10)
        timer = roundtime
        gamestage = 'playing'
        round = 1
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVXYZ'
        letter = alphabet[random.randint(1,len(alphabet)-1)]
        letterlist.append(letter)

        msg = 'Runde {}: **{}** \n'.format(round,letter)
        msg2 = ''
        for i in range(len(categories)):
            m = i + 1
            msg2 = msg2 + (str(m) + '. ' + categories[i] + '\n')

        msg3 = '\n antworte in folgendem Format: *1 Afrika*'

        for i in range(len(party)):
            sent = await client.send_message(party[i],msg + msg2 + msg3)
            answermsg.append(sent)
            print('added object to answermsg')
            pointsround.append(0)

        print(answermsg)

        reactors = []


    #script for the setup
    if msgsplit[0] == '$setup' and gamestage == 'none':


        advanced = False
        if len(msgsplit) >= 2:
            if msgsplit[1] == 'advanced':
                advanced = True



        if message.channel.is_private:
            return

        host = message.author
        mainchannel = message.channel
        gamestage = 'setup'

        msg = 'Bitte gib die Kategorien an: (durch Kommas getrennt)'
        await client.send_message(message.channel, msg)

        categoriesraw = await client.wait_for_message(timeout = 60, author = message.author, channel = message.channel)

        if categoriesraw is None:
            await client.send_message(message.channel, 'Zeit abgelaufen, bitte starte das Setup erneut')
            gamestage = 'none'
            return

        if categoriesraw.content.startswith('$reset'):
            return
        if categoriesraw.content.startswith('$endgame'):
            return

        categoriesraw = categoriesraw.content

        categories = categoriesraw.split(', ')


        msg = 'Bitte gib die Rundenlänge in Sekunden an:'
        await client.send_message(message.channel, msg)

        roundtime = await client.wait_for_message(timeout = 10, author = message.author, channel = message.channel)

        if roundtime.content.startswith('$reset'):
            return
        if roundtime.content.startswith('$endgame'):
            return

        if roundtime is None:
            roundtime = len(categories) * 10
            await client.send_message(message.channel, 'Zeit abgelaufen. Rundenlänge auf Standardwert {} gesetzt.'.format(roundtime))
        elif not is_int(roundtime.content):
            roundtime = len(categories) * 10
            await client.send_message(message.channel, 'Nicht valider Wert eingegeben. Rundenlänge auf Standardwert {} gesetzt.'.format(roundtime))
        else:
            roundtime = int(roundtime.content)
            await client.send_message(message.channel, 'Rundenlänge erfolgreich auf {} gesetzt.'.format(roundtime))


        if roundtime < 1:
            await client.send_message(message.channel, 'Da der eingegebene Wert negativ ist, können Runden nur manuell durch $stop gestoppt werden.')
            roundtime = -1



        msg = 'Bitte gib die Anzahl Runden an:'
        await client.send_message(message.channel, msg)

        roundmax = await client.wait_for_message(timeout=10, author=message.author, channel=message.channel)

        if roundmax.content.startswith('$reset'):
            return
        if roundmax.content.startswith('$endgame'):
            return

        if roundmax is None:
            roundmax = 5
            await client.send_message(message.channel, 'Zeit abgelaufen. Rundenanzahl auf Standardwert {} gesetzt.'.format(roundmax))
        elif not is_int(roundmax.content):
            roundmax = 5
            await client.send_message(message.channel, 'Nicht valider Wert eingegeben. Rundenanzahl auf Standardwert {} gesetzt.'.format(roundmax))
        else:
            roundmax = int(roundmax.content)
            await client.send_message(message.channel, 'Rundenanzahl erfolgreich auf {} gesetzt.'.format(roundmax))


        if roundmax < 1:
            await client.send_message(message.channel, 'Da der eingegebene Wert negativ ist, wird das Spiel unendlich weitergehen, bis es mit $endgame gestoppt wird.')
            roundmax = -1


        if advanced:
            msg = 'Bitte gib an wie lange Spieler zum beitreten haben:'
            await client.send_message(message.channel, msg)

            jointime = await client.wait_for_message(timeout=10, author=message.author, channel=message.channel)

            if jointime.content.startswith('$reset'):
                return
            if jointime.content.startswith('$endgame'):
                return

            if jointime is None:
                jointime = 20
                await client.send_message(message.channel,'Zeit abgelaufen. Beitretezeit auf Standardwert {} gesetzt.'.format(jointime))
            elif not is_int(jointime.content):
                jointime = 20
                await client.send_message(message.channel,'Nicht valider Wert eingegeben. Beitretezeit auf Standardwert {} gesetzt.'.format(jointime))
            else:
                jointime = int(jointime.content)
                await client.send_message(message.channel, 'Beitretezeit erfolgreich auf {} gesetzt.'.format(jointime))

            if jointime < 1:
                await client.send_message(message.channel,'Da der eingegebene Wert negativ ist, kann das Spiel nur manuell durch $start gestartet werden.')
                jointime = -1


            msg = 'Bitte gib an wie lange Spieler zum bewerten der Antworten haben:'
            await client.send_message(message.channel, msg)

            judgetime = await client.wait_for_message(timeout=10, author=message.author, channel=message.channel)

            if judgetime.content.startswith('$reset'):
                return
            if judgetime.content.startswith('$endgame'):
                return

            if judgetime is None:
                judgetime = 180
                await client.send_message(message.channel,'Zeit abgelaufen. Bewertungszeit auf Standardwert {} gesetzt.'.format(judgetime))
            elif not is_int(judgetime.content):
                judgetime = 180
                await client.send_message(message.channel,'Nicht valider Wert eingegeben. Bewertungszeit auf Standardwert {} gesetzt.'.format(judgetime))
            else:
                judgetime = int(judgetime.content)
                await client.send_message(message.channel, 'Bewertungszeit erfolgreich auf {} gesetzt.'.format(judgetime))

            if judgetime < 1:
                await client.send_message(message.channel,'Da der eingegebene Wert negativ ist, kann die nächste Runde erst beginngen wenn alle Spieler ' +
                                                          'bereit sind oder mit $continue')
                judgetime = -1



            msg = 'Bitte gib an wie lange die Pausen zwischen Runden sind:'
            await client.send_message(message.channel, msg)

            breaktime = await client.wait_for_message(timeout=10, author=message.author, channel=message.channel)

            if breaktime.content.startswith('$reset'):
                return
            if breaktime.content.startswith('$endgame'):
                return

            if breaktime is None:
                breaktime = 15
                await client.send_message(message.channel,
                                          'Zeit abgelaufen. Pausenlänge auf Standardwert {} gesetzt.'.format(
                                              breaktime))
            elif not is_int(breaktime.content):
                breaktime = 15
                await client.send_message(message.channel,
                                          'Nicht valider Wert eingegeben. Pausenlänge auf Standardwert {} gesetzt.'.format(
                                              breaktime))
            else:
                breaktime = int(breaktime.content)
                await client.send_message(message.channel,
                                          'Pausenlänge erfolgreich auf {} gesetzt.'.format(breaktime))

            if breaktime < 1:
                await client.send_message(message.channel,
                                          'Da der eingegebene Wert negativ ist, kann die nächste Runde erst mit &contine beginnen')
                breaktime = -1




        gamestage = 'joinstart'


        if host == None:
            host = client.user
        em = discord.Embed(title='Stadt, Land, Fluss', description='Setup complete', colour=0xDEADBF)
        em.set_author(name=host.display_name, icon_url=client.user.default_avatar_url)
        cats = '\n'.join(categories)
        em.add_field(name='Kategorien', value=cats, inline=False)
        if roundtime < 1:
            em.add_field(name='Rundenzeit', value='Manuell', inline=False)
        else:
            em.add_field(name='Rundenzeit', value=str(roundtime), inline=False)
        if roundmax < 1:
            em.add_field(name='Rundenanzahl', value='Manuell', inline=False)
        else:
            em.add_field(name='Rundenanzahl', value=str(roundmax), inline=False)
        if advanced:
            if jointime < 1:
                em.add_field(name='Beitretezeit', value='Manuell', inline=False)
            else:
                em.add_field(name='Beitretezeit', value=str(jointime), inline=False)
            if judgetime < 1:
                em.add_field(name='Bewertungszeit', value='Manuell', inline=False)
            else:
                em.add_field(name='Bewertungszeit', value=str(judgetime), inline=False)
            if breaktime < 1:
                em.add_field(name='Pausenlänge', value='Manuell', inline=False)
            else:
                em.add_field(name='Pausenlänge', value=str(breaktime), inline=False)
        await client.send_message(message.channel, embed=em)




@client.event
async def on_reaction_add(reaction, user):
    global gamestage

    if gamestage == 'judge':
        #if not user in party:  #put this in if you only want people to be able to vote who are in the game
            #return
        global donemsg
        global judgemsg
        global judgeyes
        global peopledone
        global mainchannel
        global judgeid

        print(reaction.message)
        print(donemsg)

        if reaction.message.content.startswith('Fertig') and reaction.message.author ==  client.user:
            print('done')
            if not user in party:
                print('user not in the game reacted to done message')
                return
            if reaction.emoji != '✅':
                return

            peopledone += 1

            if peopledone >= len(party):
                gamestage = 'judgedone'
                desc = 'Bewertungsphase beendet'
                em = discord.Embed(title='Stadt, Land, Fluss', description=desc)
                await client.send_message(mainchannel, embed=em)

        if reaction.message.id in judgeid:
            judgeindex = judgeid.index(reaction.message.id)

            if reaction.emoji == '✅':
                judgeyes[judgeindex] += 1
                print(judgeyes)

            if reaction.emoji == '❌':
                judgeyes[judgeindex] -= 1
                print(judgeyes)


    if gamestage == 'join':
        if user == client.user: #we don't want to count the reaction of the bot
            return

        if reaction.emoji != '✅':
            return

        global joinid

        if reaction.message.id != joinid: #only check for the specific message
            return

        global reactors

        if reactors.count(user.name) > 0: #fix a bug, where people can enter twice if they spam the reaction
            return

        reactmsg = reaction.message.id
        reactors.append(user.name)
        party.append(user)
        print(reactors)
        msg = '{} added a reaction to the following message: *{}*'.format(user, reactmsg)
        print(msg)


@client.event
async def on_reaction_remove(reaction, user):
    global gamestage

    if gamestage == 'judge':
        #if not user in party:  #put this in if you only want people to be able to vote who are in the game
            #return

        global donemsg
        global judgemsg
        global judgeyes
        global peopledone
        global mainchannel
        global judgeid

        print(reaction.message)
        print(donemsg)
        if reaction.message == donemsg:
            if not user in party:
                print('user not in the game reacted to done message')
                return
            if reaction.emoji != '✅':
                return

            peopledone -= 1

            if peopledone >= len(party):
                gamestage = 'judgedone'
                desc = 'Bewertungsphase beendet'
                em = discord.Embed(title='Stadt, Land, Fluss', description=desc)
                await client.send_message(mainchannel, embed=em)

        if reaction.message.id in judgeid:
            judgeindex = judgeid.index(reaction.message.id)

            if reaction.emoji == '✅':
                judgeyes[judgeindex] -= 1
                print(judgeyes)

            if reaction.emoji == '❌':
                judgeyes[judgeindex] += 1
                print(judgeyes)



    if gamestage == 'join':
        if reaction.emoji != '✅':
            return

        global joinid
        if reaction.message.id != joinid:
            return

        global reactors
        reactors.remove(user.name)
        party.remove(user)



@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.loop.create_task(countdown())
client.run('token')
