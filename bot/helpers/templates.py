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


def start_template(group_title): return f'''

Follow these simple steps to get started:

<i>Group: <b>{group_title}</b></i>

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
Use command /add_token then follow the prompt to complete

<b>Removing a token:</b>
Use command /remove_token and select the token to remove

<b>Run Contest:</b>
To run a Buy contest, use /stat_buy_contest and follow the prompt
For Raffle contests, use /raffle_on and follow the prompt

<i>Note: Only one contest (Buy or Raffle) can be active per group at anytime.</i>
    '''


help_template = '''
<i>Make sure you start bot from your special group link</i>

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
Use command /add_token then follow the prompt to complete

<b>Removing a token:</b>
Use command /remove_token and select the token to remove

<b>Run Contest:</b>
To run a Buy contest, use /stat_buy_contest and follow the prompt
For Raffle contests, use /raffle_on and follow the prompt

<i>Note: Only one contest (Buy or Raffle) can be active per period.</i>
'''

not_group_admin_template = '''
<i>❌ You are not an <b>admin</b> of this group.</>
'''

add_token_chain_select_template = '''
<b> Select your token's chain: </b>

<b>Note:</b> You can only add tokens from supported chains.
Run /chains to see a list of supported chains, Dex and pair.

<i>Group: <b>{group_title}</b></i>
'''

add_token_dex_select_template = '''
<b> Select your token's Dex: </b>

Use /chains to see a list of supported chains, Dex and pair.

<i>Group: <b>{group_title}</b></i>
'''

add_token_pair_select_template = '''
<b> Select your Pair: </b>

Run /chains to see a list of supported chains, Dex and pair.

<i>Group: <b>{group_title}</b></i>
'''

add_token_confirmation_template = '''
<b>Confirmation you setup</b>

<i>Add token for: <b>{group_title}</b></i>

Selected chain: <b>{chain}</b>
Selected dex: <b>{dex}</b>
Selected pair: <b>{pair}</b>
token address: <b>{token_address}</b>
'''

biggest_buy_winners_template = '''
<b>🎉Biggest Buy Competition Started</b>

🕓 Start 11:10:00 UTC
⏳ Ends in 1 hours 16 min 34 sec
⬇️ Minimum Buy 0.10 BNB

🥇 0x46b0…1974 ➖ 1.2 BNB
🥈 0xc351…4bf7 ➖ 0.75 BNB
🥉 0x7171…4ee6 ➖ 0.7 BNB
4️⃣ 0xdfd0…4815 ➖ 0.54 BNB
5️⃣ 0x3fa6…d50a ➖ 0.5 BNB

🎖 Biggest Buy 0x46b0…1974 ➖ 1.2 BNB

——

Buy Grimacecoin 🥰
'''
