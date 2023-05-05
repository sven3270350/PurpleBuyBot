const { startMainJobs, startChildJobs } = require("./schedule");
const TelegramBot = require('node-telegram-bot-api');
const WebSocket = require('ws');

const allBuysListener = require("./listeners/allBuys");
const countdownListener = require("./listeners/countdown");
const campaignBuyListener = require("./listeners/campaingBuys");
const winnerAnnouncer = require("./listeners/winnerAnnouncer");

const https = require("https");
const http = require("http");

https.globalAgent.maxSockets = 100;
http.globalAgent.maxSockets = 100;

const botToken = '5749218942:AAHScJvWi3GuLfGv-UvKumedwz-9wRcgJgM';
const bot = new TelegramBot(botToken, { polling: false });

const wsEndpoint = 'wss://api.telegram.org/bot' + botToken;
const ws = new WebSocket(wsEndpoint);

ws.on('open', () => {
  console.log('WebSocket connection established');
});

ws.on('message', (data) => {
  const update = JSON.parse(data);
  console.log('Received update:', update);
  // Process the update as needed
});

const main = async () => {
  try {
    // start main jobs
    startMainJobs();

    await Promise.all([
      allBuysListener.main(bot),
      campaignBuyListener.main(bot),
      countdownListener.main(bot),
      winnerAnnouncer.main(bot),
    ]).catch((err) => console.log("[All::PromiseError] : ", err));

    // start child jobs
    startChildJobs();
  } catch (error) {
    console.log("[_app::main]", error);
  }
};

main();
