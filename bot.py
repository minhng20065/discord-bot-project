# bot.py
'''
This module sets up the discord bot and contains all the commands 
and their logic needed to function.
'''
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import sheet
from sheet import Sheet
from errors import Error
from select1 import Select
import config

load_dotenv()
# enables all intents for the bot
intents = discord.Intents.all()
intents.message_content = True
# specifies that commands will begin with !, and allows all intents
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    '''This method executes as soon as the bot is activated, showing
    the bot's name and ID.'''
    print('logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('-----')

# initializes the objects for each file
sheet = Sheet()
error = Error()
select = Select()

@bot.command()
async def register(ctx, *args):
    '''This method defines a command to register a new character to the database. It
    takes the character's characteristics provided in a user submission, and passes
    them to an SQL function in the sheet.py file.'''

    # if there are less than 7 arguments, the command is invalid.
    if len(args) != 7:
        await ctx.send('Invalid amount of arguments! Try again.')
        return

    # roles and ages should be these values, or they are invalid.
    if args[3].lower() != 'transposed' and args[3].lower() != 'established':
        await ctx.send("Error, invalid role input.")
        return
    if (args[5].lower() != 'alive' and args[5].lower() != 'dead'):
        await ctx.send("Error, invalid status input.")
        return
    # if the age is not a numerical value, it is invalid.
    if error.verifyNumeric(args[1]):
        sheet.register_char(args)
    else:
        await ctx.send("Error, invalid age input.")
        return
    await ctx.send("stored!")
@bot.command()
async def get_id(ctx, name):
    '''This function retrieves the ID of a requested character from their name.'''
    id_char = sheet.get_id(name)
    # if the id exists, print it out
    if id_char != 'None':
        await ctx.send(name + "'s ID is " + id_char)
    else:
        await ctx.send("This character is not registered!")
@bot.command()
async def primary(ctx, *args):
    '''This method registers the primary stats for a character. It takes
    the primary stat values and passes them on to an SQL function in the sheet.py file'''
    if len(args) != 7:
        await ctx.send('Invalid amount of arguments! Try again.')
    if sheet.verify_id(args[6]) is False:
        await ctx.send("This character is not registered!")
    for i in range(0, 7):
        if error.verifyNumeric(args[i]) is False:
            await ctx.send("One of your arguments is invalid! Please try again.")
            return
    sheet.register_prim(args)
    await ctx.send("stored! Secondary stats have been calculated.")
@bot.command()
async def levelup(ctx, char_id):
    '''This function levels up a character given their id. It prompts the user to increment
    a primary stat by one, and executes a function that does that in the sheet file.'''
    if sheet.verify_id(char_id) is False:
        await ctx.send("This character is not registered!")
        return
    await ctx.send("Congratulations on leveling up! What stat would you like to increase?")
    # checks if the author sent that message and it's in the same channel
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    try:
        # recieves the user reply
        reply = await bot.wait_for('message', timeout=60.0, check=check)
    # if the user waits too long to reply, a timeout is issued
    except asyncio.TimeoutError:
        await ctx.send('Timeout occurred')
    else:
        if sheet.level_up(str(reply.content), char_id) is False:
            await ctx.send("Failed! Invalid stat name!")
        else:
            await ctx.send("Upgrade Successful!")
@bot.command()
async def editcharacter(ctx, char_id):
    '''Prompts the user to edit the character values of a given character, and calls another
    function to ask for value.'''
    if sheet.verify_id(char_id) is False:
        await ctx.send("This character is not registered!")
        return
    await ctx.send("Which characteristic would you like to change?")
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    try:
        reply = await bot.wait_for('message', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send('Timeout occurred')
    else:
        await edit_char_val(ctx, char_id, str(reply.content))

async def edit_char_val(ctx, char_id, column):
    '''This function is called by the previous editcharacter command, and prompts
    the user for the value they want the characteristic to be changed to. Then, it calls
    a method in the sheet file to edit the value in the database.'''
    await ctx.send("And what would you like the value to be?")
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    try:
        reply = await bot.wait_for('message', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send('Timeout occurred')
    else:
        if sheet.edit_char(column, char_id, reply.content) is False:
            await ctx.send("Update failed! Your values are invalid.")
        else:
            await ctx.send("Sucessfully edited the character's " + column)
@bot.command()
async def edit_primary(ctx, char_id):
    """This method prompts the user to choose a primary stat to change from a character's ID."""
    if sheet.verify_id(char_id) is False:
        await ctx.send("This character is not registered!")
        return
    await ctx.send("Which primary stat would you like to change?")
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    try:
        reply = await bot.wait_for('message', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send('Timeout occurred')
    else:
        await edit_primary_val(ctx, char_id, str(reply.content))

async def edit_primary_val(ctx, char_id, column):
    """This method prompts the user for the new value of their previously inputted primary stat.
    It takes in the stat recorded previously, and Then, it calls
    a method in the sheet file to edit the value in the database."""
    await ctx.send("And what would you like the value to be?")
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    try:
        reply = await bot.wait_for('message', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send('Timeout occurred')
    else:
        if sheet.edit_prim(column, char_id, reply.content) is False:
            await ctx.send("Update failed! Your values are invalid.")
        else:
            await ctx.send("Sucessfully edited the character's " + column)

@bot.command()
async def print_sheet(ctx, char_id):
    """"This method prints out the character sheet by calling print functions from the sheet file.
    It takes the character id corresponding to the sheet."""
    if sheet.verify_id(char_id) is False:
        await ctx.send("This character is not registered!")
        return
    await ctx.send("```" + select.print_char(char_id) + "\n\nPRIMARY STATS:\n"
                   + select.print_prim(char_id) +
                   "\n\nSECONDARY STATS:\n" + select.print_sec(char_id) + "\n\nABILITIES:\n" 
                   + str(select.calculate_abilities(char_id)) + "\n\nCURRENT WEAPON:\n"
                   + "\n\nCURRENT ARMOR:\n" +
                   "\n\nEQUIPPED ABILITY:\n" + str(select.print_ability(char_id)) 
                   + "\n\nREPUTATION:\n" + str(select.print_rep(char_id)) +  "\n\nSLOE:\n" +  "```")

@bot.command()
async def assign_ability(ctx, char_id):
    """This function displays the available abilities that a character can
    equip, and prompts user if they want to equip an ability for each slot.. It then passes the 
    reply to a function that prompts the user to assign an ability for each slot."""
    if sheet.verify_id(char_id) is False:
        await ctx.send("This character is not registered!")
        return
    slots = sheet.calculate_slots(char_id)
    await ctx.send("These are your available abilities!\n" +
                   str(select.calculate_abilities(char_id)))
    await ctx.send("Your available slots: " + str(slots))
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel\
    # iterates through each available slot for the character
    while slots != 0:
        await ctx.send("Would you like to assign an ability for slot " + str(slots) +
                       "? Answer with a Y or N.")
        try:
            reply = await bot.wait_for('message', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send('Timeout occurred')
        else:
            if str(reply.content) == "Y":
                await assign(ctx, slots, char_id)
                slots = slots - 1
            elif str(reply.content) == "N":
                break
            else:
                await ctx.send("Invalid answer, please try again.")

@bot.command()
async def edit_rep(ctx, col, row, char_id):
    """This method updates the reputation of a character, by passing their character id into
    a function in the sheet file that updates the database."""
    if sheet.verify_id(char_id) is False:
        await ctx.send("This character is not registered!")
        return
    sheet.find_rep(col, row, char_id)
    await ctx.send("Reputation updated!")

@bot.command()
async def delete_sheet(ctx, char_id):
    """This method prompts the user to delete a sheet based on the character ID provided.
    It then executes a method in the sheet file that deletes all the character's information
    from the database."""
    if sheet.verify_id(char_id) is False:
        await ctx.send("This character is not registered!")
        return
    await ctx.send("Are you sure you want to delete this sheet?")
    print_sheet(ctx, char_id)
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    try:
        reply = await bot.wait_for('message', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send('Timeout occurred')
    else:
        if str(reply.content) == "Y":
            sheet.delete_sheet(char_id)
        elif str(reply.content) == "N":
            await ctx.send("Oky")
        else:
            await ctx.send("Invalid answer, please try again.")

async def assign(ctx, slot, char_id):
    """This function prompts the user to assign an ability for their character, for
    each slot. It then calls a function from the sheet file to put it in the database."""
    if sheet.verify_id(char_id) is False:
        await ctx.send("This character is not registered!")
        return
    await ctx.send("Please choose an ability for slot " + str(slot) + ".")
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    try:
        reply = await bot.wait_for('message', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send('Timeout occurred')
    else:
        sheet.update_abilities(char_id, slot, reply.content)
        await ctx.send("Ability assigned!")

@bot.event
async def on_member_join(member):
    """This function recognizes when a new member joins a server, printing
    the appropriate welcome message."""
    print("Recognised that a member called " + member.name + " joined")
    channel = bot.get_channel(552942757358993470)
    await channel.send('Welcome, ' + member.name + ' to the Republic of Blackthorn!' +
    'Be sure to mind the laws, buy Voidrot products, and do your part to keep Blackthorn safe and' +
    'secure from criminals and the Overgrowth.')

@bot.event
async def on_member_remove(member):
    """This function recognizes when a new member leaves a server, printing
    the appropriate goodbye message."""
    print("Recognised that a member called " + member.name + " left")
    channel = bot.get_channel(552942757358993470)
    await channel.send('Goodbye ' + member.name + '. Your service to Blackthorn will' +
    'be sorely missed.')

@bot.event
async def on_member_ban(member):
    """This function recognizes when a new member is banned a server, printing
    the appropriate message."""
    print("Recognised that a member called " + member.name + " was banned")
    channel = bot.get_channel(552942757358993470)
    await channel.send(member.name + ' was expelled from the Republic of Blackthorn for rebellious'+
    'behavior and aiding and abetting Resistance members. The penalty for this crime is death.')

@bot.event
async def on_member_unban(user):
    """This function recognizes when a new member is unbanned from a server, printing
    the appropriate message."""
    channel = bot.get_channel(552942757358993470)
    await channel.send('Recognizing the service of ' + user.name + ', the Republic of Blackthorn' +
    'has decided to pardon this person.')

@bot.event
async def on_command_error(ctx, err):
    """This function checks if there is an invalid amount of arguments in a command,
    and prints out an error message."""
    if isinstance(err, commands.MissingRequiredArgument):
        await ctx.send('Invalid amount of arguments! Try again.')
bot.run(config.TOKEN)
