# RaffleBot

This is a python dgg chat bot using [fritz/dgg-bot](https://github.com/Fritz-02/dgg-bot/tree/master)

It is intended to connect to a [RaffleDashboard](https://github.com/NickMarcha/RaffleDashboard)
mainly the Socket.io is serves.

//note, I don't generally write python code, so keep in mind if reading it ¯\\ _(ツ)_/¯

## Config

you can use `rafflebot/config.json` to get started
| Property | Description | Example |
| -------- | ------- | ------- |
| botOwner | Your DGG Username | Barret |
| botPrefix | Command prefix for dgg-bot | !rb
| botSecret | Your Bots dgg login key, see [dgg/developer](https://www.destiny.gg/profile/developer) | 0imfnc8mVLWwsArandomrandomc8mVLWwsAawjYr4Rx |
| raffleSocketURL | socket.io endpoint | raffledashboard.example.com/socket.io |
| whiteListedUsers | users who can use commands and partake in private message broadcasts in dgg chat| [ "randomUserOne", "Barrett"] |
| notifyUserList | users who are notified of things like raffle rolls in dgg chat | ["randomAdminUserOne", "randomAdminUserTwo"] |
| statsURL | used for command | https://docs.google.com/spreadsheets/d/e/[spreadsheetID] |
| againstMalariaURL| used for command | https://www.againstmalaria.com/[fundraiserID] |
|watchedURL | used for command | https://docs.google.com/spreadsheets/d/e/[spreadsheetID] |

## Commands

### General Chat

| command       | description                      | aliases |
| ------------- | -------------------------------- | ------- |
| `!rb stats`   | replies with `statsURL`          | `s`     |
| `!rb donate`  | replies with `againstMalariaURL` | `d`     |
| `!rb watched` | replies with `againstMalariaURL` | `w`     |

### Whisper Chat

Whisper RaffleBot to use these
| command | description |
| -------- | ------- |
| `!bc <msg>`| sends a whisper from RaffleBot to all whitelisted users with your username prefixed |
