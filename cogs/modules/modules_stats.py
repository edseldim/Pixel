import matplotlib.pyplot as plt 
import io, time, datetime


def giveChannel(ctx, channelName):

    """Returns the object of the channel provided"""

    channels = ctx.bot.get_guild(ctx.message.guild.id.real).channels

    for channel in channels:

        if channel.name.lower() == channelName.lower():

            return channel

def dateVerificator(dateLists):

    """Checks if the provided date is okay
    
    the position number zero is the month
    the position number 1 is the day
    the position number 2 is the year"""

    #this for loops through dateLists until it finds an error, if it doesn't find any error then it returns 1 that means okay
    #0 means that there's some error with the date provided

    for date in dateLists:

        if int(date[0]) in [2,4,6,9,11,13]: #these months don't have a 31

            if int(date[1]) > 0 and int(date[1]) <= 30: #checks if the user entered a day between 1 and 30

                if int(date[2]) >= 2014 and int(date[2]) <= time.localtime()[0]: #checks if the year is between 2014 and the current year

                    pass

        elif int(date[0]) in [1,3,5,7,8,10,12,14]: #these months have a 31 

            if int(date[1]) > 0 and int(date[1]) <=31: #checks if the user entered a day between 1 and 31

                if int(date[2]) >= 2014 and int(date[2]) <= time.localtime()[0]: #checks if the year is between 2014 and the current year

                    pass

        else:

            return 0

    else:

        return 1

def channelVerificator(ctx, channel_name): 

    """Checks if channel_name exists"""

    channels = ctx.bot.get_guild(ctx.message.guild.id.real).channels

    for channel in channels:

        if channel_name.lower() == channel.name.lower():

            return 1

    else:

        return 0

def verificator(ctx, dateList):

    """this function checks if the date provided is okay to use
    dateList can be in three different formats
    
    1) channel (if the user only provides the channel then they want a graph of the actual day)
    2) channel/month1/day1/year1 (if the user provides a channel and a date is because they want a graph of that date)
    3) channel/month1/day1/year1/month2/day2/year2 (if the user provides a channel and two dates is because they want a graph between those dates)"""

    if len(dateList) > 1:

        #if the length is greater than one it means that the user provided 
        #a channel and a date

        if len(dateList) == 7:

            #if the length is equal to 7 it means that the user provided
            #a channel, an initial date and an ending date

            date1 = dateList[:4]
            date2 = dateList[4:]

            dateCheck = dateVerificator([date1[1:],date2]) #checks if the date is okay
            
            channelCheck = channelVerificator(ctx, date1[0]) #checks if the channel exists

            if dateCheck == 1 and channelCheck == 1:

                return 5

            else:

                if dateCheck == 0:

                    return 0

                else:

                    return 1

        elif len(dateList) == 4:

            #If the length is equal to 4 it means that the user provided 
            #a channel and a date

            date1 = dateList[:]
            print(date1[1:])
            
            dateCheck = dateVerificator([date1[1:]])
            channelCheck = channelVerificator(ctx, date1[0])

            print(dateCheck)

            if dateCheck == 1 and channelCheck == 1:

                return 4

            else:

                if dateCheck == 0:

                        return 0

                else:

                        return 1

        else:

            return 2

    else:

        #if the list length is not equal to one it means that the user only provided
        #a channel

        date1 = dateList[:]

        channelCheck = channelVerificator(ctx, date1[0])

        if channelCheck == 1:

            return 3

        else:

            return 1


async def graph(date1, date2, channel, option, ctx, discord):

    """"This function generates a graph
    
    date1(list) => the day when the bot will start counting
    
    date2(list) => the day when the bot will stop counting
    
    channel => the channel which will be used to count
    
    option => it can be either 0 or 1, if it is 1 then when one graph is generated my bot won't 
    erase it from memory because this will be used to generate more graphs and compare every of them 
    in just one graph, but if option is 0 then my bot erases the graph from memory, this is necessary
    when the user just want one individual graph."""

    #Firstly, we need to convert all the info inside date1 and date2 to integer since they are stored in string format

    year1 = int(date1[-1])
    month1 = int(date1[0])
    day1 = int(date1[1])

    year2 = int(date2[-1])
    month2 = int(date2[0])
    day2 = int(date2[1])+1

    # if month2 < 10:

    #     dateLimit = f'{year2}-0{month2}'

    #     if day2 < 10:

    #         dateLimit += f'-0{day2}'

    #     else:

    #         dateLimit = f'{year2}-0{month2}-{day2}'
    
    # else:

    #     if day2 < 10:

    #         dateLimit = f'{year2}-{month2}-0{day2}'

    #     else:

    #         dateLimit = f'{year2}-{month2}-{day2}'


    #This Y axis list is necessary because we need a list of 24 empty slots that we are going to use to increase in 1 the corresponding position
    #every time a message of the same hour gets counted

    y_axis = [i-i for i in range(24)]

    try:

        #We use try because if there any error we want to let the user know

        async for messages in channel.history(limit = 10000000000000, after = datetime.datetime(year1,month1,day1,0,0), before = datetime.datetime(year2,month2,day2,0,0).utcnow()):

            value = y_axis[int(messages.created_at.hour.__int__())] #We get the number of messages counted of a certain hour 

            value = value + 1 #we increase the value we just got

            y_axis[int(messages.created_at.hour.__int__())] = value #we store again the value we just increased

    
    except Forbidden:

        await ctx.send("**I don't have permissions to read that channel**")

    except HTTPException:

        await ctx.send("**Network Error**")

    else:

        #This x axis list has the same lenght of the y axis list, it starts with 5
        #and ends with 4 because this list is arranged like the GMT timezone

        x_axis = [5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,0,1,2,3,4] 

        fig, ax = plt.subplots()

        ax.bar(x = x_axis, height = y_axis, linewidth = 0.5)

         #this two following lines formats the date like this Year/Month/Day

        date1 = datetime.datetime(year1,month1,day1).strftime("%Y/%m/%d") 
        date2 = datetime.datetime(year2,month2,day2).strftime("%Y/%m/%d")

        ax.set_xlabel('Hours (GMT)')
        ax.set_ylabel('Number of messages')
        ax.set_title(f'Number of messages per Hour in #{channel} \nduring {date1}-{date2}')
        plt.xticks(x_axis)
        plt.axis(option = 'equal')

        with io.BytesIO() as barIm:
            fig.savefig(barIm, format='png')
            barIm.seek(0)
            await ctx.send(file=discord.File(barIm, 'plot.png'))

        # if option == 0:

        #     # with io.BytesIO() as barIm:
        #     #     fig.savefig(barIm, format='png')
        #     #     barIm.seek(0)
        #     #     await ctx.send(file=discord.File(barIm, 'plot.png'))

        fig.clf() 
        plt.close(fig=fig)

