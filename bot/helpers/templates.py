def start_template_private(bot_name): return f'''
<b>Welcome to Biggest Buy Bot!</b>

Follow these simple steps to get started:

1. Add the bot to your group
2. run /start@{bot_name or 'botname'} in the group to get started
3. Open the special link provided to get your group's unique link
4. Follow the new instructions to get started
    '''


def start_added_to_group(bot_name): return f'''
<b>You have added {bot_name}!</b>

Follow these simple steps

1) Click the link below (Admins only).
2) Click the "Start" button at the bottom of the screen.
3) Follow the new instructions

<i>This link connects you to this group's bot settings, save it for easy access</i>
'''


def start_template(bot_name): return f'''

Follow these simple steps to get started:

<i>Group: @{bot_name}</i>

<b>Supported Commands:</b>
/help - Show supported commands
/add_token - Add the token to be monitored requires token address
/remove_token - Remove monitored token
/tracked_tokens - List tracked tokens
/start_buy_contest - Initiate a biggest buy contest
/raffle_on - Start raffle buy contest
/subscribe - Subscribe to premium to remove ads
/chains - Show a list of supported chains

<b>Adding a token:</b>
Use command /add_token [token_address] or just /add_token then follow the prompt to complete

<b>Removing a token:</b>
Use command /remove_token [token_address] or just /remove_token

<b>Run Contest:</b>
To run a Buy contest, use /stat_buy_contest and follow the prompt
For Raffle contests, use /raffle_on and follow the prompt

<i>Note: Only one contest (Buy or Raffle) can be active per group at anytime.</i>
    '''


help_template = '''
Follow these simple steps to get started:

<b>Supported Commands:</b>
1) /help - Show supported commands
2) /add_token - Add the token to be monitored requires token address
3) /remove_token - Remove monitored token
4) /tracked_tokens - List tracked tokens
5) /start_buy_contest - Initiate a biggest buy contest
6) /raffle_on - Start raffle buy contest
7) /subscribe - Subscribe to premium to remove ads
8) /chains - Show a list of supported chains

<b>Adding a token:</b>
Use command /add_token [token_address] or just /add_token then follow the prompt to complete

<b>Removing a token:</b>
Use command /remove_token [token_address] or just /remove_token

<b>Run Contest:</b>
To run a Buy contest, use /stat_buy_contest and follow the prompt
For Raffle contests, use /raffle_on and follow the prompt

<i>Note: Only one contest (Buy or Raffle) can be active per period.</i>
'''
