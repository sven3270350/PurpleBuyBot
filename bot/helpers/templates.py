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

<b>Adding a token:</b>
Use command /add_token then follow the prompt to complete

<b>Removing a token:</b>
Use command /remove_token and select the token to remove

<b>Run Contest:</b>
To run a Buy contest, use /start_buy_contest and follow the prompt
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
To run a Buy contest, use /start_buy_contest and follow the prompt
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
<b>Confirm your setup</b>

<i>Add token for: <b>{group_title}</b></i>

Selected chain: <b>{chain}</b>
Selected dex: <b>{dex}</b>
Selected pair: <b>{pair}</b>
token address: <b>{token_address}</b>

use /cancel to restart
'''

remove_token_confirmation_template = '''
<b>Confirm your setup</b>

<i>Remove token for: <b>{group_title}</b></i>

Selected token: <b>{token_name}</b>
Token address: <b>{token_address}</b>
Chain: <b>{chain_name}</b>

Click Confirm to remove token

use /cancel to restart
'''


active_subscription_template = '''
<b> Active Premium Subscription ({group_title}</b>

You are currently subscribed to {package}

<i>Started: <b>{start_date}</b></i>
<i>Ends: <b>{end_date}</b></i>
'''

no_active_subscription_template = '''
<b> Subscribe ({group_title}) </>

Get our ads-free experience by subscribing to our premium package.

<i>Select a package below:</i>
'''


weekly_subscription_template = '''
<b> Weekly Subscription</b>

Type the number of weeks you want to subscribe to.

<i>Leave blank for 1 week</i>
'''

subscription_confirmation_template = '''
<b>Confirm ({group_title})</b>

You have selected the {package} package.

Total cost: {total_cost}

<i>Select payment Chain to proceed</i>
'''


check_payment_template = '''
<b>Check Payment</b>

Select your payment chain and enter transaction hash.
'''

payment_status_template = '''
<b>Payment Status</b>

Transaction hash: <b>{transaction_hash}</b>
Chain: <b>{chain_name}</b>

<i>{status_message}</i>
'''

has_pending_subscription_template = '''
<b>You have a pending subscription</b>

<i>Waiting Payment for: <b>{subscription} package</b></i>

Chain: <b>{chain_name}</b>

Complete your subscription by paying {total_cost} to: 
{payment_address}.

<i>Use /subscribe to check payment status</i>
'''

final_subscription_review_template = '''
<b>Confirm ({group_title})</b>

You have selected the {package} package.

Total cost: {total_cost}

Chain: {chain_name}

<i>pay {total_cost} to {wallet} to complete!</i>
'''

no_trackecd_tokens_template = '''
<b>No tracked tokens</b>

<i>You have no tracked tokens</i>
use `/add_token` to add a token
'''

start_biggest_buy_contest_template = '''
<b>Start {competition_name} Contest Settings</b>

<i>Group: <b>{group_title}</b></i>

Select <b>Start Competition</b> to start the contest with the following settings:

<b>Token:</b> {token_name}

<b>Start's :</b> {start_date}
<b>Ends:</b> {end_date}

<b>Minimum Buy:</b> ${minimum_buy}
<b>Winner's Reward:</b> {winner_reward}

<i>Note: You can only have one contest at a time</i>
'''

set_start_time_template = '''
<b>Set Start Time: </b>

Time to start the contest.
<i> Example: </i>
  <code> 15/09/2022 04:17:08</code>

'''

set_end_time_template = '''
<b> Set End Time: </b>

Time to end the contest.
<i> Example: </i>
  <code> 15/09/2022 04:17:08</code>

'''

invalid_time_template = '''
<b> ❌ Invalid date.</b>

<i> Please use DD/MM/YYYY HH:MM:SS </i> 
<i> Example: </i>
  <code>01/01/2020 12:00:00</code> 

<b> OR </b>

<i> Make sure date is in the future </i>
  
<i> Please try again </i>
'''

not_valid_value_template = '''
<b> ❌ Invalid value.</b>

<i> Please enter a valid value </i>

<i> Example: </i>
    <code> 100 </code> for $100
'''


set_min_buy_template = '''
<b>Set Minimum Buy value: </b>

Min USD value to buy to be eligible for the contest.
eg 100, 200, 1000 etc

'''

set_winner_reward_template = '''
<b>Set Winner Reward: </b>

Set the reward for the winner in USD. 
eg 100, double, Testa etc

'''

start_competition_confirmation_template = '''
<b>Confirm </b>

<b>Token:</b> {token_name}
    
<b>Start's :</b> {start_date}
<b>Ends:</b> {end_date}

<b>Minimum Buy:</b> ${minimum_buy}
<b>Winner's Reward:</b> {winner_reward}

<i>Click Confirm to start the contest</i>

'''

biggest_buy_competition_alert_template = '''
📢 📢 📢 📢 📢 📢 📢
<b>New {competition_name} Competition Alert</b>

<i>Group: <b>{group_title}</b></i>

<i>Token: <b>{token_name}</b></i>

<b>Start's :</b> {start_date}
<b>Ends:</b> {end_date}

<b>Minimum Buy:</b> ${minimum_buy}
<b>Winner's Reward:</b> {winner_reward}

——

<i>{ad}</i>
'''


regular_buy_template = '''
🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢

New <b>{token_name} </b> Buy!

<b>Paid</b>: <i>{amount_in} ${usd_price}</i>
<b>For</b>: <i>{amount_out}</i>

<b>On</b>: <i>{chain_name}</i>

Buyer: <i>{buyer}</i>

——

<i>{ad}</i>
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
