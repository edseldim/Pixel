import time, os, json, re

dir_path = os.path.dirname(os.path.realpath('python_bot.py'))


def check_user_existance(ctx, user_id, bot):

    user = bot.get_guild(ctx.message.guild.id.real).get_member(user_id)

    if user != None:

        return 1

    else: 

        return 0
    

    

def check_roles(user_roles, roles_allowed):

    """Verifies if the user has a rol that is allowed to use the bot"""

    for role in user_roles:

            if role.id in roles_allowed:

                return 1

    else:

        return 0

def check_item_attribute(category,item_key, value, settings):

    """Checks the current value inside an item stored in the list of any attribute"""

    for item in settings[category]:

        for key in item:

            if item_key == key:

                if item[key] == value:

                    return 1

    else:

        return 0

def check_role_existance(role_check, roles_stored):

    """Verifies if the rol is already stored in the database"""

    if role_check in roles_stored:

        return 1

    else:

        return 0



async def alert_admins(settings, censured_channel, author, bot):

        """Sends a message to every channel in admin_alert_channels when a user
        has broken the rule 3 or more times"""

        list_of_words_deleted = "Words deleted: "

        for user in settings['censored_people']:

            if user['author'] == author:

                for word in user['words_deleted']:

                    list_of_words_deleted += f' {word},'
                    

        for channel in settings['admin_alert_channels']:

            if channel['language'] == 'ES':

                await bot.get_channel(channel['channel_id']).send(f"<@{author}> acaba de escribir 3 o mas veces una palabra"
                                            +f" prohibida en {censured_channel}\n\n {list_of_words_deleted}")

                

            else:

                await bot.get_channel(channel['channel_id']).send(f"<@{author}> just wrote 3 times or more times a forbidden word"
                                            +f" in {censured_channel}\n\n {list_of_words_deleted}")
                                

def word_avaliability_checker(banned_word, settings):

        """Checks whether the banned word is already stored or not"""

        valid_words = []

        if len(banned_word) == 0:

            if banned_word[0] in settings['banned_words']:

                return False

            else:

                return valid_words.append(banned_word[0])

        else:

            for word in banned_word:

                if not word in settings['banned_words']:

                    valid_words.append(word)


            if len(valid_words) > 0:

                return valid_words

            else:

                return False

def censoring_in_channel(channel_id,feature_checking, settings):

    """Checks whether delete_messages feature is on or off and so do with the alert_users feature"""

    for censored_channel in settings['channels_to_censor']:

        if censored_channel['channel_id'] == channel_id:

            for key in censored_channel:

                if key == feature_checking:

                    if feature_checking == 'delete_messages':

                        if censored_channel[key].upper() == 'TRUE':

                            return 1

                        else:

                            return 0

                    elif feature_checking == 'alert_users':

                        if censored_channel[key].upper() == 'PM':

                            return 1

                        elif censored_channel[key].upper() == 'CC':

                            return 2

                        elif censored_channel[key].upper() == 'RC':

                            return 3

                        elif censored_channel[key].upper() == 'BOTH':

                            return 4

                        else:

                            return 0

                    else:

                        if censored_channel[key].upper() == 'TRUE':

                            return 1

                        else:

                            return 0

            
def channel_avaliability_checker(channel_id, category, settings):

        """Checks whether the channel is already stored or not"""

        channels_stored = []

        for channel in settings[category]:

            channels_stored.append(channel['channel_id'])

        if int(channel_id) in channels_stored:

            return False

        else:

            return True

def channel_existance_name(ctx, channel_name):

    """checks if the channel name exists"""

    channels = ctx.bot.get_guild(ctx.message.guild.id.real).channels

    for channel in channels:

        if channel_name.lower() == channel.name.lower():

            return 1

    else:

        return 0

def channel_existance(channel_id, bot):

        """Checks if the channel does exist"""

        channels_stored = []

        for channel in bot.get_all_channels():

            channels_stored.append(channel.id)

        if not (int(channel_id) in channels_stored):

            return False

        else:

            return True

def category_existance(category_db, guild_categories):
        """checks whether a category exists or not"""
        """the id provided should be an integer"""

        categories_id = []

        for category_stored in category_db:

            categories_id.append(category_stored['id'])

        for category in guild_categories:

            if category.id in categories_id:

                return 1 #exists

        else:

            return 0 #doesn't exist




async def send_message_privetly( forbidden_word, message_content, channel_name, author, channel_language, bot):

        """This function sends a private message to someone"""

        if channel_language.upper() == 'EN':

            await bot.get_user(author).send('You just sent this'
            +f' message in #{channel_name}:\n\n{message_content}\n\n and we wanted to let you know'
            +f' that the word **{forbidden_word}** is prohibited in both #beginner_english'
            +f' and #español_principiante')

        else:

            await bot.get_user(author).send('Acabas de mandar este'
            +f' mensaje en #{channel_name}:\n\n{message_content}\n\n y te queriamos hacer saber'
            +f' que la palabra **{forbidden_word}** está prohibida tanto en #beginner_english'
            +f' y #español_principiante')



def get_channel_name(channel_id, bot):

    """returns the name of a channel using its ID"""

    for channel in bot.get_all_channels():

        if channel.id == int(channel_id):

            return channel.name


def banned_words_logger(author_id, author_nickname, banned_word, channel, jump_url , path):

    """writes in a file all the users who has written a banned word"""

    with open(f'{path}/banned_words_logger.txt','a') as f:

        f.write(f"\n[{time.asctime()}] by:{author_id}({author_nickname}) channel: {channel} banned_word: {banned_word} url: {jump_url}")


def print_info_attribute(category_name, category_info, bot, server_id):

    """returns the info of an attribute"""

    if category_name == 'channels_to_censor' or category_name == 'admin_alert_channels':

        content_iterable = []

        for key in category_info:

            content_iterable.append(f"{key['channel_id']}({bot.get_channel(key['channel_id']).name} language:{key['language']}"
            +f" delete messages:{key['delete_messages']} alert users:{key['alert_users']} admin alert:{key['admin_alert']}),\n ")

        return message_maker(content_iterable, category_name)

    elif category_name == 'censored_people':

        content_iterable = []

        for key in category_info:

            content_iterable.append(f"{key['author']}({bot.get_guild(server_id).get_member(int(key['author'])).nick} infractions:{key['n_infractions']}), ")
                
        return message_maker(content_iterable, category_name)

    
    elif category_name == 'roles_allowed':

        content_iterable = []

        for role_id in category_info:

            content_iterable.append(f"{role_id}({bot.get_guild(server_id).get_role(role_id).name}), ")
                
        return message_maker(content_iterable, category_name)

    elif category_name == 'banned_words':

        content_iterable = []

        for word in category_info:

            content_iterable.append(f'{word}, ')
                
        return message_maker(content_iterable, category_name)



def message_maker(content, title):

    """Creates a message using iterable content"""

    message = f'```{title}:\n\n'
    for string in content:

                message += string
    message += '```'
    return message

def category_verifier(category_sent, database):
    
    """Verifies if a category exists"""

    for category_db in database:
        if category_db.lower() == category_sent.lower():
            return 1
    else:
        return 0



async def censor_listener(message, banned_word, settings, bot):

    """Manages user message depending on the word (if it's banned or not) and depending
    channel censorship's settings"""

    for channel in settings['channels_to_censor']:

        if message.channel == bot.get_channel(channel['channel_id']):

            for word in settings['banned_words']:

                if f' {word.lower()} ' in banned_word.lower():

                    if censoring_in_channel(message.channel.id, 'delete_messages', settings):

                        await message.delete()

                    if censoring_in_channel(message.channel.id, 'alert_users', settings) == 1:

                        await send_message_privetly(word, message.content, message.channel.name, message.author.id, channel['language'], bot)

                    if censoring_in_channel(message.channel.id, 'alert_users', settings) == 2:

                        if check_item_attribute('channels_to_censor', 'language', 'ES', settings):

                            await message.channel.send(f"**{word} está baneada! no la uses por favor!**")

                        else:

                            await message.channel.send(f"**{word} is banned! please don't use it**")

                    if censoring_in_channel(message.channel.id, 'alert_users', settings) == 3:

                        await message.add_reaction('❌')

                    if censoring_in_channel(message.channel.id, 'alert_users', settings) == 4:

                        await send_message_privetly(word, message.content, message.channel.name, message.author.id, channel['language'], bot)

                        await message.channel.send(f"**{word} is banned! please don't use it**")

                    if censoring_in_channel(message.channel.id,'admin_alert', settings) == 1:

                        for person in settings['censored_people']:

                                if person['author'] == message.author.id:

                                    person['n_infractions'] += 1
                                    person['words_deleted'].append(word)

                                    if person['n_infractions'] % 3 == 0:

                                        await alert_admins(settings, message.channel.name, person['author'], bot)

                                    save(settings)

                                    break

                        else:

                            settings['censored_people'].append({
                                'author':message.author.id,
                                'n_infractions': 1,
                                'words_deleted':[word]
                            })


                        banned_words_logger(message.author, message.author.id ,word, message.channel.name, message.jump_url , dir_path)

                        save(settings)


async def message_correction_checker(bot, message, chat_language):

    """Checks that the user who is reacting to the message is a native, if so
    it will change the reaction to ✅, instead it will remain as 
    
    Note:
    
    it waits 1 hour for the native to check the correction"""


    def check(reaction, user):

        if user.id != 595011002215563303:

            if chat_language == 'spanish':

                if check_roles(user.roles, [243854128424550401, 267368304333553664]) == 1:

                    if str(reaction.emoji) == '✅':

                        return reaction.message == message and str(reaction.emoji) == '✅'
                    
                    elif str(reaction.emoji) == '❌':

                        return reaction.message == message and str(reaction.emoji) == '❌'


            elif chat_language == 'english': 

                if check_roles(user.roles, [243853718758359040, 430708264037253120]) == 1:

                    if str(reaction.emoji) == '✅':

                        return reaction.message == message and str(reaction.emoji) == '✅'

                    
                    elif str(reaction.emoji) == '❌':


                        return reaction.message == message and str(reaction.emoji) == '❌'

                           

    try:
        
        reaction = None
        reaction = await bot.wait_for('reaction_add', timeout=3600, check=check)

    except:

        pass

    else:

        if str(reaction[0].emoji) == '✅':

            await reaction_in_correction(bot, 3, message)

        if str(reaction[0].emoji) == '❌':

            await reaction_in_correction(bot, 4, message)


def get_guild(bot, guild_id):

    """Returns the guild of the member provided"""

    guild_object =  bot.get_guild(int(guild_id))

    return guild_object

def get_member(guild, member_id):

    """Returns the object of the member provided"""

    member_object = guild.get_member(int(member_id))

    return member_object


async def reaction_in_correction(bot, option, message):

    """Let us choose three different options of reactions depending on our needs"""

    if option == 1:

        await message.add_reaction('✏')

    elif option == 2:

        await message.add_reaction('✅')
        await message.add_reaction('❌')

    elif option == 3:
        

        await message.remove_reaction('✅', get_member(get_guild(bot, 243838819743432704), 595011002215563303))
        await message.remove_reaction('❌', get_member(get_guild(bot, 243838819743432704), 595011002215563303))


    elif option == 4:

        await message.remove_reaction('✅', get_member(get_guild(bot, 243838819743432704), 595011002215563303))
        await message.remove_reaction('❌', get_member(get_guild(bot, 243838819743432704), 595011002215563303))


async def channels_correction_settings(bot,message,user_roles,roles_allowed, channel_language):

    """Checks if the user is a native speaker in the channel of their native language"""

    #If the user is a native speaker or fluent and the correction was made is the channel of their native language
    #reaction_in_correction function will receive a one and that means that Pixel will react to the message
    # with a pencil  ✏

    if check_roles(user_roles, roles_allowed) == 1:

                await reaction_in_correction(bot, 1, message)

    else:

        #If the user is neither a native speaker nor a fluent speaker of the language where the correction 
        # was made reaction_in_correction function will receive a two and that means that Pixel will react to the message
        # with a ✅ or a ❌ depending on the opinion of a native speaker/fluent speaker 

                await reaction_in_correction(bot, 2, message)

                await message_correction_checker(bot, message,channel_language)

    


async def react_corrections(bot, message):

    """Manages the channels where the correction will be either ✅ or ❌
    depending on user's roles
    
    This is a ENG-ESP Discord server Functionnality"""

    if message.content.strip(' ').strip('**').strip('``').strip('```').strip('*').strip('||').strip('~~').strip('__').strip('_').startswith('!>'):

        #The bot will check if the correct was made the beginner or advanced channels

        if str(message.channel.id) == '243858509123289089':

            #español_principiante 243858509123289089

            await channels_correction_settings(bot,message,message.author.roles, [243854128424550401, 267368304333553664], 'spanish')

        
        elif str(message.channel.id) == '243858546746327050':

            #beginner_english 243858546746327050

            await channels_correction_settings(bot,message,message.author.roles, [243853718758359040,267367044037476362], 'english')

        elif str(message.channel.id) == '388539967053496322':

            #español_avanzado 388539967053496322

            await channels_correction_settings(bot,message,message.author.roles, [243854128424550401, 267368304333553664], 'spanish')


        elif str(message.channel.id) == '529780137126789123': 

            #advanced_english 529780137126789123

            await channels_correction_settings(bot,message,message.author.roles, [243853718758359040, 267367044037476362], 'english')

        elif str(message.channel.id) == '284045742652260352': 

            #literally_anything_is_fine 529780137126789123

            await channels_correction_settings(bot,message,message.author.roles, [243853718758359040, 267368304333553664], 'spanish')

        elif str(message.channel.id) == '739127911650557993': 
            
            #language exchange chat 739127911650557993

             await message.add_reaction('✏')



def save(settings):

    """Saves the settings in a json file"""

    with open(f"{dir_path}/db.json",'w') as write_file:

        json.dump(settings, write_file)

def saveSpecific(settings, name):

    """Saves the settings of a specific cog in a json file"""

    with open(f"{dir_path}/{name}",'w') as write_file:

        json.dump(settings, write_file)


async def member_converter(ctx, user_in):

    """Credits https://github.com/ryry013/Rai/blob/master/cogs/utils/helper_functions.py"""

    # check for an ID
    user_id = re.findall("(^<@!?\d{17,22}>$|^\d{17,22}$)", str(user_in))
    if user_id:
        user_id = user_id[0].replace('<@', '').replace('>', '').replace('!', '')
        member = ctx.guild.get_member(int(user_id))
        return member

    # check for an exact name
    member = ctx.guild.get_member_named(user_in)
    if member:
        return member

    # try the beginning of the name
    member_list = [(member.name.casefold(), member.nick.casefold() if member.nick else '', member)
                   for member in ctx.guild.members]
    user_in = user_in.casefold()
    for member in member_list:
        if member[0].startswith(user_in):
            return member[2]
        if member[1].startswith(user_in):
            return member[2]

    # is it anywhere in the name
    for member in member_list:
        if user_in in member[0]:
            return member[2]
        if user_in in member[1]:
            return member[2]

    if ctx.author != ctx.bot.user:
        await ctx.send('User not found')
    return None

def get_category(category_db, categories):

    """returns a category object"""

    categories_id = []

    for category_stored in category_db:

        categories_id.append(category_stored['id'])

    if category_existance(category_db, categories) == 1:

        for category in categories:

            if category.id in categories_id:

                return category


#move it

async def member_count_update(member, misc_settings):

    guild = member.guild

    if category_existance(misc_settings['countMembersChannel'], guild.categories) == 1:

        category = get_category(misc_settings['countMembersChannel'], guild.categories)

        for category_db in misc_settings['countMembersChannel']:

            if category.id == category_db['id']:

                try:

                    await category.edit(name = f"{category_db['name']}({guild.member_count} MEMBERS)")

                except Forbidden:

                    print(f"**I don't have enough permissions to change {category.name}'s name'")

    else:

        print('It doesnt exist!')