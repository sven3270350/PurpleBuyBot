import datetime

def start_template_private(bot_name): return f'''
<b>Welcome to PurpleBuyBot!</b>

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

Quick help:

<i>Group: <b>{group_title}</b></i>

<b>Managin Tokens:</b>
Add, use /add_token
Remove, use /remove_token
List tracked tokens, use /tracked_tokens

<b>Run Contest:</b>
Biggest Buy contest, use /start_buy_contest
Raffle contests, use /raffle_on
Last Buy contests, use /start_lastbuy_contest
End Contest, use /active_contest

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
/start_lastbuy_contest - Start last buy contest
/active_contest - Show active contest and cancel if needed
/contest_winners - Show winners of last 5 contests
/subscribe - Subscribe to premium to remove ads
/chains - Show a list of supported chains
/active_tracking - Toggle active buy tracking
/set_buy_icon - Set buy icon
/set_buy_media - Set a gif or image to show with buys
/set_group_link - Create and set a new invite link for the group
/delete_group_link - Delete the group link

<b>Managin Tokens:</b>
Add, use /add_token
Remove, use /remove_token
List tracked tokens, use /tracked_tokens
Set minimum buy, use /set_min_usd_amount

<b>Run Contest:</b>
Biggest Buy contest, use /start_buy_contest
Raffle contests, use /raffle_on
Last Buy contests, use /start_lastbuy_contest
End Contest, use /active_contest to proceed

<b>Toggle Tracking:</b>
Use /active_tracking to toggle tracking of buys

<b>Subscriptions:</b>
Use /subscribe to subscribe to premium to remove ads

<b>Other Settings:</b>
Set Icon, use /set_buy_icon
Set Banner, /set_buy_media

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


def start_biggest_buy_contest_template(competition_name, group_title, token_name, start_date, end_date, countdown, minimum_buy, winner_reward):
    return f'''
<b>Start {competition_name} Contest Settings</b>

<i>Group: <b>{group_title}</b></i>

Select <b>Start Competition</b> to start the contest with the following settings:

<b>Token:</b> {token_name}

<b>Starts :</b> <code>{start_date}</code> UTC
<b>Ends:</b> <code>{end_date}</code> UTC
{('<b>Countdown:</b> ' + countdown + 's') if countdown else ''}

<b>Minimum Buy:</b> ${minimum_buy}
<b>Winner's Reward:</b> {winner_reward}

<i>Note: You can only have one contest at a time</i>
'''


set_start_time_template = '''
<b>Set Start Time: </b>

Time to start the contest (UTC)
<i> Example: </i>
  <code>{date}</code>

'''

set_end_time_template = '''
<b> Set End Time: </b>

Time to end the contest. (UTC)
<i> Example: </i>
  <code>{date}</code>

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

invalid_countdown_template = '''
<b> ❌ Invalid countdown.</b>

<i> Please enter a valid countdown in seconds</i>

<i> Example: </i>
    <code>100</code> for 100 seconds
'''


set_min_buy_template = '''
<b>Set Minimum Buy value: </b>

Min USD value to buy to be eligible for the contest.
eg 100, 200, 1000 etc

'''

set_winner_reward_template = '''
<b>Set Winner Reward: </b>

Set the reward for the winner. 
eg 100, double, Testa etc

'''

set_countdown_template = '''
<b>Set Countdown: </b>

Set the countdown for the contest in seconds.
eg 100, 200, 1000 etc

'''


def start_competition_confirmation_template(token_name, start_date, end_date, minimum_buy, winner_reward, countdown):
    return f'''
<b>Confirm </b>

<b>Token:</b> {token_name}
    
<b>Starts :</b> <code>{start_date}</code>
<b>Ends:</b> <code>{end_date}</code>

<b>Minimum Buy:</b> ${minimum_buy}
<b>Winner's Reward:</b> {winner_reward}
{('<b>Countdown:</b> ' + countdown + 's') if countdown else ''}

<i>Click Confirm to start the contest</i>

'''


def biggest_buy_competition_alert_template(competition_name, group_title, token_name, start_date, end_date, minimum_buy, winner_reward, countdown, ad):
    return f'''
  📢 📢 📢 📢 📢 📢 📢
  <b>New {competition_name} Competition Alert</b>

  <i>Group: <b>{group_title}</b></i>

  <i>Token: <b>{token_name}</b></i>

  <b>⏱ Starts: </b> {start_date}
  <b>🕣 Ends: </b> {end_date}
  {('<b>🕣 Countdown:</b> ' + countdown + 's') if countdown else ''}


  <b>⬇️ Minimum Buy:</b> ${minimum_buy}
  <b>🏆 Winner's Reward:</b> {winner_reward}

  ——

  <i>{ad}</i>
  '''


def active_contest_template(competition_name, group_title, start_date, end_date, minimum_buy, winner_reward, countdown):
    return f'''
🎮 <b>{competition_name} Contest</b>

👥 <i>Group: <b>{group_title}</b></i>

⏱ <b>Start :</b> {start_date}
🕣 <b>End:</b> {end_date}
{('<b>🕣 Countdown:</b> ' + countdown + 's') if countdown else ''}

⬇️ <b>Minimum Buy:</b> ${minimum_buy}
🏆 <b>Winner's Reward:</b> {winner_reward}
'''


def contest_winner_template(start: datetime, end: datetime, winner: str, contest: str, prize: str):
    return f'''
🎮 <b>Contest: {contest}</b>

🕣 <i>Duration: {start} - {end}</i>
🎉 <code>{winner}</code> won <b>{prize}</b>
--------
    '''


regular_buy_template = '''
🟢🟢🟢🟢🟢🟢🟢🟢🟢

New <b>{token_name} </b> Buy!

<b>Paid</b>: <i>{amount_in} ${usd_price}</i>
<b>For</b>: <i>{amount_out}</i>

<b>On</b>: <i>{chain_name}</i>

Buyer: <i>{buyer}</i>

——

<i>{ad}</i>
'''
