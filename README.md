# RaffleBot

This is a python dgg chat bot using [fritz/dgg-bot](https://github.com/Fritz-02/dgg-bot/tree/master)

It is intended to connect to a [RaffleDashboard](https://github.com/NickMarcha/RaffleDashboard)
mainly the Socket.io is serves.

//note, I don't generally write python code, so keep in mind if reading it ¯\\ _(ツ)_/¯

## Config

should be at `config/config.json`
You can use `config/copy.config.json` to get started
| Property | Description | Example |
| -------- | ------- | ------- |
| `botOwner` | Your DGG Username | `Barret` |
| `botPrefix` | Command prefix for dgg-bot | `#`
| `botSecret` | Your Bots dgg login key, see [dgg/developer](https://www.destiny.gg/profile/developer) | `0imfnc8mVLWwsArandomrandomc8mVLWwsAawjYr4Rx` |
| `raffleSocketURL` | socket.io endpoint | `raffledashboard.example.com/socket.io` |
| `raffleAPIURL` | API endpoint | `raffledashboard.example.com/api` |
| `whiteListedUsers` | users who can use commands and partake in private message broadcasts in dgg chat| `["randomUserOne", "Barrett"]` |
| `notifyUserList` | users who are notified of things like raffle rolls in dgg chat | `["randomAdminUserOne", "randomAdminUserTwo"]` |
| `statsURL` | used for command | `https://docs.google.com/spreadsheets/d/e/[spreadsheetID]` |
| `againstMalariaURL` | used for command | `https://www.againstmalaria.com/[fundraiserID]` |
| `watchedURL` | used for command | `https://docs.google.com/spreadsheets/d/e/[spreadsheetID]` |
| `messageThrottleTime` | time between regular chat messages in seconds | `60` |

## Commands

### General Chat

| command           | description                        | aliases |
| ----------------- | ---------------------------------- | ------- |
| `#amstats`        | replies with `statsURL`            | `#ams`  |
| `#amdonate`       | replies with `againstMalariaURL`   | `#amd`  |
| `#amwatched`      | replies with `againstMalariaURL`   | `#amw`  |
| `#amtodaystotal`  | replies with todays totals         | `#amtt` |
| `#amoveralltotal` | replies with overall totals        | `#amot` |
| `#amraffletotal`  | replies with current raffle totals | `#amrt` |

### Whisper Chat

Note: **Whisper disabled atm**
Whisper RaffleBot to use these
| command | description |
| -------- | ------- |
| `#bc <msg>`| sends a whisper from RaffleBot to all whitelisted users with your username prefixed |

## Developer

use this section in `main.py` to connect to developer environment

```python
########################### Version ###########################    #[11]
DEVELOPMENT = False                                                #[12]
#DEVELOPMENT = True                                                #[13]
versionNumber = "0.0.2"                                            #[14]
```

### Developer Config

should be at `config/dev.config.json`
You can use `config/copy.dev.config.json` to get started
