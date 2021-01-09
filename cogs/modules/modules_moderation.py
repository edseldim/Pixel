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


def check_role_existance(role_check, roles_stored):

    """Verifies if the rol is already stored in the database"""

    if role_check in roles_stored:

        return 1

    else:

        return 0

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

        categories_id = [] #Makes a list that receives the IDs of the categories of a server
        for category_stored in category_db: #retrieves the categories saved by pixel
            categories_id.append(category_stored['id']) #Saves each category id in categories_id
        for category in guild_categories: #retrieves the categories of a server
            if category.id in categories_id: #Checks whether the category of a server is contained in pixel's db 
                return 1 #Category found
        else:
            return 0 #Category not found


def get_channel_name(channel_id, bot):

    """returns the name of a channel using its ID"""

    for channel in bot.get_all_channels():

        if channel.id == int(channel_id):

            return channel.name


def category_verifier(category_sent, database):
    
    """Verifies if a category exists"""

    for category_db in database:
        if category_db.lower() == category_sent.lower():
            return 1
    else:
        return 0


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

        else: 

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

    categories_id = [] #Makes a list for all the categories saved
    for category_stored in category_db: #Retrieves all the categories saved
        categories_id.append(category_stored['id']) #Saves all the categories id in categories_id
    for category in categories: #Retrieves all the server categories
            if category.id in categories_id: #Checks what server is the one that needs to be returned
                return category #returns the target category

async def member_count_update(member, misc_settings):

    """Updates the member count"""

    guild = member.guild #Retrieves the object for the server that the user joined
    if category_existance(misc_settings['countMembersChannel'], guild.categories) == 1: #Checks whether the server is contained in pixel's db
        print("uwu1")
        category = get_category(misc_settings['countMembersChannel'], guild.categories) #Retrieves the category where the member count is
        print("uwu2")
        for category_db in misc_settings['countMembersChannel']: #Retrieves all the categories saved to find the one pixel will update
            print("uwu3")
            if category.id == category_db['id']: #Locates the category id in pixel's db for updating purposes
                print("uwu4")
                try:
                    await category.edit(name = f"{category_db['name']} ({guild.member_count} MEMBERS)") #updates the category name
                    print("uwu5")
                except Forbidden:
                    print(f"**I don't have enough permissions to change {category.name}'s name'") #Error message
    else:
        print('It doesnt exist!')