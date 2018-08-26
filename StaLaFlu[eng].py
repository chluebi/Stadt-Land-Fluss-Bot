import discord
import random
import asyncio
import os

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

#user managment
leavers = [] #people who once were in the game but left the game
bans = [] #people who can't join this instance of the game


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
    #mainchannel = 0  # the channel where the joining takes place
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
                gamestage = 'judging'
                for n in range(len(party)):
                    desc = 'The round is over, please go back to the main channel.'
                    em = discord.Embed(title='Scattergories', description=desc)

                    if not endplayer == '':
                        em.add_field(name='Premature ending.', value=endplayer + ' stopped the round prematurely.', inline=False)

                    if not party[n] in leavers:
                        await client.send_message(party[n], embed=em)
                        
                await asyncio.sleep(2)
                desc = 'The round is over, please go back to the main channel.'
                em = discord.Embed(title='Scattergories', description=desc)

                if not endplayer == '':
                    em.add_field(name='Premature ending.', value=endplayer + ' stopped the round prematurely.',inline=False)

                if len(party) == 0:
                    await client.send_message(mainchannel, embed=em)


            if timer % 5 == 0 and gamestage == 'playing' and not timer == roundtime:
                for n in range(len(party)):

                    msg = 'Round {}: **{}** \n'.format(round, letter)
                    msg2 = ''
                    for i in range(len(categories)):
                        m = i + 1
                        msg2 = msg2 + (str(m) + '. ' + categories[i] + ': ' + answers[n][i] + '\n')
                    msg3 = '\n please answer like the following: *1 Africa*'
                    msg4 = '\n \n ``Time remaining: ' + str(timer) + '``'
                    if n >= len(answermsg):
                        n = len(answermsg)-1
                    if n < 0:
                        n = 0

                    if party[n] not in leavers:
                        if timer > 0:
                            await client.edit_message(answermsg[n], msg + msg2 + msg3 + msg4)
                        else:
                            await client.edit_message(answermsg[n], msg + msg2 + msg3)

            if timer == 0 and gamestage == 'judge':
                gamestage = 'judgedone'
                desc = 'Judgephase ended'
                em = discord.Embed(title='Scattergories', description=desc)
                await client.send_message(mainchannel, embed=em)


            if timer % 5 == 0 and gamestage == 'judge' and not timer == judgetime:
                msg = 'Done with judging? React to this message. \n'
                msg2 = '``Time remaining: {}``'.format(str(timer))


                if donemsg != 0:
                    if timer > 0:
                        await client.edit_message(donemsg, msg + msg2)
                    else:
                        await client.edit_message(donemsg, msg)

            await client.change_presence(game=discord.Game(name='$help'))





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
    global leavers
    global bans

    # split the message to better handle the different inputs
    msgsplit = message.content.split(' ')
    print(str(msgsplit))


    # info and debug commands
    if msgsplit[0] == '$status':
        print('Gamestage: ' + gamestage)


    # general commands for all users

    if msgsplit[0] == '$help':
        embed = discord.Embed(title="Scattergories", description="Helpmenu")
        embed.add_field(name='$commands', value='Commands for participants.')
        embed.add_field(name='$hostcommands', value = 'Commands for the host.')
        embed.add_field(name='$rules', value='Rules for the game.')
        await client.send_message(message.channel,embed=embed)

    if msgsplit[0] == '$commands':
        embed = discord.Embed(title="Scattergories", description="Commands")
        embed.add_field(name='$join', value='Join an ongoing game. *can only be used between rounds*')
        embed.add_field(name='$leave', value='Leave an ongoing game. *can only be used between rounds*')
        await client.send_message(message.channel, embed=embed)

    if msgsplit[0] == '$hostcommands':
        embed = discord.Embed(title="Scattergories", description="Host commands")
        embed.add_field(name='$endgame', value='Ends the game prematuerly.')
        embed.add_field(name='$start', value='Start a game prematurely. *Can only be used during the join phase*')
        embed.add_field(name='$continue', value='Start the next round prematurely. *Can only be used between rounds*')
        embed.add_field(name='$change <variable> <value>', value='Change one of the following variables: roundtime, roundmax, judgetime, breaktime')
        await client.send_message(message.channel, embed=embed)

    if msgsplit[0] == '$rules':
        embed = discord.Embed(title="Scattergories: Rules", description="Every round a random letter is chosen. Find words that fit the categories and the letter.")
        await client.send_message(message.channel, embed=embed)

    if gamestage == 'continue': #join and leave commands
        if msgsplit[0] == '$leave':
            if message.author in party:
                leavers.append(message.author)
                await client.send_message(mainchannel,'{} left the game.'.format(message.author.display_name))
            else:
                await client.send_message(message.channel,'You arent in any ongoing games.')

        if msgsplit[0] == '$join':
            if message.author in party:
                if message.author in leavers:
                    leavers.remove(message.author)
                    await client.send_message(mainchannel,'{} joined the game again.'.format(message.author.display_name))
                else:
                    await client.send_message(message.channel,'You are already in a game.')
            else:
                party.append(message.author)
                points.append(0)
                await client.send_message(mainchannel,'{} joined the game.'.format(message.author.display_name))

    if msgsplit[0] == '$reset':
        reset()
        return


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


                ranking.sort(key=lambda x: x[1], reverse=True)

                msg = 'Points: \n ```\n'
                msg2 = ''

                for i in range(len(party)):
                    msg2 = msg2 + ranking[i][0] + ': ' + str(ranking[i][1]) + ' (+' + str(ranking[i][2]) + ')\n'

                msg2 = msg2 + '```'

                await client.send_message(mainchannel, msg + msg2)

            desc = 'Thanks for playing.'
            em = discord.Embed(title='Scattergories', description=desc)
            await client.send_message(message.channel, embed=em)
            reset()
            return


        if msgsplit[0] == '$change' and not (gamestage == 'none' or gamestage == 'setup'):
            oldgamestage = gamestage
            gamestage = 'change'
            if msgsplit[1] == 'roundtime':
                if is_int(msgsplit[2]):
                    await client.send_message(message.channel, 'Roundlenght successfully changed from {} to {}.'.format(roundtime,msgsplit[2]))
                    roundtime = max(-1,int(msgsplit[2]))
                else:
                    await client.send_message(message.channel, 'Please enter a number.')

            elif msgsplit[1] == 'roundmax':
                if is_int(msgsplit[2]):
                    await client.send_message(message.channel, 'Amount of rounds successfully changed from {} to {}.'.format(roundmax,msgsplit[2]))
                    roundmax = max(-1,int(msgsplit[2]))
                else:
                    await client.send_message(message.channel, 'Please enter a number.')

            elif msgsplit[1] == 'judgetime':
                if is_int(msgsplit[2]):
                    await client.send_message(message.channel, 'Judgetime successfully changed from {} to {}.'.format(judgetime,msgsplit[2]))
                    judgetime = max(-1,int(msgsplit[2]))
                else:
                    await client.send_message(message.channel, 'Please enter a number.')

            elif msgsplit[1] == 'breaktime':
                if is_int(msgsplit[2]):
                    await client.send_message(message.channel, 'Lenghts of pauses successfully changed from {} to {}.'.format(breaktime,msgsplit[2]))
                    breaktime = max(-1,int(msgsplit[2]))
                else:
                    await client.send_message(message.channel, 'Please enter a number.')

            else:
                print('bad argument for &change')
            gamestage = oldgamestage





    # script for starting a new round
    if gamestage == 'roundend' and message.author == client.user:

        gamestage = 'continue'
        i = 0

        if breaktime > 0:
            breakmsg = await client.send_message(mainchannel,'``The next round starts in {} seconds.``'.format(breaktime))
        else:
            breakmsg = await client.send_message(mainchannel,'The next round starts soon')

        await client.send_message(mainchannel, 'New players can join with $join \n'+
                            'If you want to leave the game, use $leave')

        while i != breaktime:
            await asyncio.sleep(1)
            if (breaktime-i-1) % 2 == 0:
                if breaktime > 0:
                    await client.edit_message(breakmsg,'``The next round starts in {} seconds.``'.format(breaktime-i-1))
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

        desc = 'The round starts in 10 seconds. Answers will be sent through the DMs.'
        em = discord.Embed(title='Scattergories', description=desc)
        await client.send_message(message.channel, embed=em)

        for i in range(len(party)):
            if party[i] not in leavers:
                await client.send_message(party[i], embed=em)

        answers = [[''] * len(categories) for i in range(len(party))]
        print(answers)

        await asyncio.sleep(10)
        timer = roundtime
        endplayer = ''
        gamestage = 'playing'
        round += 1
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVXYZ'
        letter = 0
        while letter == 0 or letter in letterlist:
            letter = alphabet[random.randint(1, len(alphabet) - 1)]

        letterlist.append(letter)

        msg = 'Round {}: **{}** \n'.format(round, letter)
        msg2 = ''
        for i in range(len(categories)):
            m = i + 1
            msg2 = msg2 + (str(m) + '. ' + categories[i] + '\n')

        msg3 = '\n please answer like the following: *1 Africa*'


        for i in range(len(party)):
            if party[i] not in leavers:
                sent = await client.send_message(party[i], msg + msg2 + msg3)
                answermsg.append(sent)
            else:
                answermsg.append(0)
            pointsround.append(0)


    # script for gameend and ranking
    if gamestage == 'gameend' and message.author == client.user:
        gamestage = 'gameended'

        desc = 'Thanks for playing.'
        em = discord.Embed(title='Scattergories', description=desc)
        await client.send_message(message.channel, embed=em)

        reset()


    # script for points
    if gamestage == 'judgedone' and message.author == client.user:
        gamestage = 'points'
        pointsround = []
        for i in range(len(party)):
            pointsround.append(0)

        for k in range(len(judgeuser)):
            if judgeyes[k] > -1:
                auth = judgeuser[k]
                authindex = party.index(auth)
                pointsround[authindex] += 1



        for i in range(len(party)):
            points[i] += pointsround[i]

        ranking = [[0 for x in range(3)] for y in range(len(party))]

        for y in range(len(party)):
            ranking[y][0] = party[y].display_name
            ranking[y][1] = points[y]
            ranking[y][2] = pointsround[y]


        ranking.sort(key=lambda x: x[1], reverse=True)


        msg = 'Points: \n ```\n'
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
            msg = 'The game has ended.'
            await client.send_message(mainchannel, msg)
        else:
            gamestage = 'roundend'
            msg = 'Round {} done. Starting next round...'.format(round)
            await client.send_message(mainchannel,msg)





    # script for judging
    if gamestage == 'judging' and message.author == client.user:
        timer = judgetime
        gamestage = 'judge'
        desc = 'Judge the answers of the other participants.'
        em = discord.Embed(title='Scattergories', description=desc)
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

        msg = 'Finished with judging? React to this message.'

        donemsg = await client.send_message(mainchannel,msg)
        await client.add_reaction(donemsg,'✅')
        print(donemsg)



    # script for the game
    if gamestage == 'playing':
        print('playing')
        print(leavers)

        if message.author in leavers:
            return

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
                msg = 'You havent entered a word for all categories yet.'
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
            msg = 'You have entered a word for every category, stop the round prematurely with $stop'
            await client.send_message(message.author, msg)

        msg = 'Round {}: **{}** \n'.format(round, letter)
        msg2 = ''
        for i in range(len(categories)):
            m = i + 1
            msg2 = msg2 + (str(m) + '. ' + categories[i] + ': ' + answers[userindex][i] + '\n')
        msg3 = '\n please answer like the following: *1 Africa*'
        msg4 = '\n \n ``Time remaining: ' + str(timer) + '``'

        if timer > 0:
            await client.edit_message(answermsg[userindex], msg + msg2 + msg3 + msg4)
        else:
            await client.edit_message(answermsg[userindex], msg + msg2 + msg3)


    # script for joining
    if msgsplit[0] != 'Spiel' and msgsplit[0] != 'React' and message.author == client.user and gamestage == 'joinstart':
        gamestage = 'join'
        reactmsg = await client.send_message(message.channel, 'React to this message to join!')

        global joinid
        joinid = reactmsg.id

        await client.add_reaction(reactmsg,'✅') #add the first reaction

        global reactors
        i = 0

        while i != jointime: #wait "timer" seconds
            await asyncio.sleep(1)
            msg = 'React to this message to join! \n'
            msg3 = ' ``{} seconds remaining`` \n'.format(jointime-1-i)
            if len(reactors) > 0:
                msg2 = '\n' + 'Participants: \n' + '```\n' + '\n'.join(reactors) + '```' #send the participants list
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
        desc = 'The game starts in 10 seconds, answers are written in DMs.'
        em = discord.Embed(title='Scattergories',description=desc)
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

        msg3 = '\n please answer like the following: *1 Africa*'

        for i in range(len(party)):
            if party[i] not in leavers:
                sent = await client.send_message(party[i],msg + msg2 + msg3)
                answermsg.append(sent)
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

        msg = 'Please enter the categories: (seperated by commas)'
        await client.send_message(message.channel, msg)

        categoriesraw = await client.wait_for_message(timeout = 300, author = message.author, channel = message.channel)

        if categoriesraw is None:
            await client.send_message(message.channel, 'Timed out, please start the setup again')
            gamestage = 'none'
            return

        if categoriesraw.content.startswith('$reset'):
            return
        if categoriesraw.content.startswith('$endgame'):
            return

        categoriesraw = categoriesraw.content

        categories = categoriesraw.split(', ')


        msg = 'Please enter the roundlenght (in seconds):'
        await client.send_message(message.channel, msg)

        roundtime = await client.wait_for_message(timeout = 10, author = message.author, channel = message.channel)



        if roundtime is None:
            roundtime = len(categories) * 10
            await client.send_message(message.channel, 'Timed out, set roundlength to {}.'.format(roundtime))
        elif not is_int(roundtime.content):
            if roundtime.content.startswith('$reset'):
                return
            if roundtime.content.startswith('$endgame'):
                return
            if gamestage == 'none':
                return
            roundtime = len(categories) * 10
            await client.send_message(message.channel, 'Not valid value, set roundlength to {}.'.format(roundtime))
        else:
            roundtime = int(roundtime.content)
            await client.send_message(message.channel, 'Set roundlenght to {} successfully.'.format(roundtime))


        if roundtime < 1:
            await client.send_message(message.channel, 'Because the value you entered was negative, rounds will only finish when someone enters $stop')
            roundtime = -1



        msg = 'Please enter the amount of rounds:'
        await client.send_message(message.channel, msg)

        roundmax = await client.wait_for_message(timeout=10, author=message.author, channel=message.channel)



        if roundmax is None:
            roundmax = 5
            await client.send_message(message.channel, 'Timed out, set amount of rounds to {}.'.format(roundmax))
        elif not is_int(roundmax.content):
            if roundmax.content.startswith('$reset'):
                return
            if roundmax.content.startswith('$endgame'):
                return
            if gamestage == 'none':
                return
            roundmax = 5
            await client.send_message(message.channel, 'Not valid value, set amount of rounds to {}.'.format(roundmax))
        else:
            roundmax = int(roundmax.content)
            await client.send_message(message.channel, 'Set amount of rounds to {} successfully.'.format(roundmax))


        if roundmax < 1:
            await client.send_message(message.channel, 'Because the value you entered was negative, the game can only end with $endgame')
            roundmax = -1


        if advanced:
            msg = 'Please enter how long players have to join the game:'
            await client.send_message(message.channel, msg)

            jointime = await client.wait_for_message(timeout=10, author=message.author, channel=message.channel)


            if jointime is None:
                jointime = 20
                await client.send_message(message.channel,'Timed out, set jointime to {}.'.format(jointime))
            elif not is_int(jointime.content):
                if jointime.content.startswith('$reset'):
                    return
                if jointime.content.startswith('$endgame'):
                    return
                jointime = 20
                await client.send_message(message.channel,'Not valid value, set jointime to {}.'.format(jointime))
            else:
                jointime = int(jointime.content)
                await client.send_message(message.channel, 'Set jointime to {} successfully.'.format(jointime))

            if jointime < 1:
                await client.send_message(message.channel,'Because the value you entered was negative, the game can only start with $start')
                jointime = -1


            msg = 'Please enter how long players have to judge the answers:'
            await client.send_message(message.channel, msg)

            judgetime = await client.wait_for_message(timeout=10, author=message.author, channel=message.channel)


            if judgetime is None:
                judgetime = 180
                await client.send_message(message.channel,'Timed out, set judgetime to {}'.format(judgetime))
            elif not is_int(judgetime.content):
                if judgetime.content.startswith('$reset'):
                    return
                if judgetime.content.startswith('$endgame'):
                    return
                judgetime = 180
                await client.send_message(message.channel,'Not valid value, set judgetime to {}.'.format(judgetime))
            else:
                judgetime = int(judgetime.content)
                await client.send_message(message.channel, 'Set judgeime to {} successfully.'.format(judgetime))

            if judgetime < 1:
                await client.send_message(message.channel,'Because the value you entered was negative, the next round can only start with $continue')
                judgetime = -1



            msg = 'Please enter how long the breaks between rounds are:'
            await client.send_message(message.channel, msg)

            breaktime = await client.wait_for_message(timeout=10, author=message.author, channel=message.channel)


            if breaktime is None:
                breaktime = 15
                await client.send_message(message.channel,
                                          'Timed out, set breaklenght to {}.'.format(
                                              breaktime))
            elif not is_int(breaktime.content):
                if breaktime.content.startswith('$reset'):
                    return
                if breaktime.content.startswith('$endgame'):
                    return
                breaktime = 15
                await client.send_message(message.channel,
                                          'Not valid value, set breaklenght to {}.'.format(
                                              breaktime))
            else:
                breaktime = int(breaktime.content)
                await client.send_message(message.channel,
                                          'Successfully set breaklength to {}.'.format(breaktime))

            if breaktime < 1:
                await client.send_message(message.channel,
                                          'Because the value you entered was negative, the next round can only start with $continue')
                breaktime = -1




        gamestage = 'joinstart'


        if host == None:
            host = client.user
        em = discord.Embed(title='Scattergories', description='Setup complete', colour=0xDEADBF)
        em.set_author(name=host.display_name, icon_url=client.user.default_avatar_url)
        cats = '\n'.join(categories)
        em.add_field(name='categories', value=cats, inline=False)
        if roundtime < 1:
            em.add_field(name='roundlenght', value='manual', inline=False)
        else:
            em.add_field(name='roundlength', value=str(roundtime), inline=False)
        if roundmax < 1:
            em.add_field(name='amount of rounds', value='manual', inline=False)
        else:
            em.add_field(name='amounts of rounds', value=str(roundmax), inline=False)
        if advanced:
            if jointime < 1:
                em.add_field(name='jointime', value='manual', inline=False)
            else:
                em.add_field(name='jointime', value=str(jointime), inline=False)
            if judgetime < 1:
                em.add_field(name='judgetime', value='manual', inline=False)
            else:
                em.add_field(name='judgetime', value=str(judgetime), inline=False)
            if breaktime < 1:
                em.add_field(name='breaklenght', value='manual', inline=False)
            else:
                em.add_field(name='breaklength', value=str(breaktime), inline=False)
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


        if reaction.message.content.startswith('Finished') and reaction.message.author ==  client.user:
            if not user in party:
                return
            if user in leavers:
                return

            if reaction.emoji != '✅':
                return

            peopledone += 1

            if peopledone >= len(party) - len(leavers):
                gamestage = 'judgedone'
                desc = 'Judgephase finished'
                em = discord.Embed(title='Scattergories', description=desc)
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

        if reaction.message == donemsg:
            if not user in party:
                return
            if reaction.emoji != '✅':
                return

            peopledone -= 1

            if peopledone >= len(party):
                gamestage = 'judgedone'
                desc = 'Judgephase done'
                em = discord.Embed(title='Scattergories', description=desc)
                await client.send_message(mainchannel, embed=em)

        if reaction.message.id in judgeid:
            judgeindex = judgeid.index(reaction.message.id)

            if reaction.emoji == '✅':
                judgeyes[judgeindex] -= 1

            if reaction.emoji == '❌':
                judgeyes[judgeindex] += 1



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
