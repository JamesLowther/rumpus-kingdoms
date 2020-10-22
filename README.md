# Rumpus Kingdoms

## Description
Rumpus Kingdoms is a discord-driven attack-and-defend strategy game based around a medieval theme. Players can build a kingdom by settling villages. Attack and defence units could be purchased to attack other player's kingdoms. Complete with front-end scoreboard to track player status. Written with discord.py for the back-end and flask for the front-end website.

## Requirements
Requires discord.py, sqlite3, and flask

## How to Play

### How to Win
* Each person can create a kingdom made up of villages
* You can increase your population by buying villages or upgrading existing ones
* The kingdom with the highest population will be at the top of the leaderboard

### How to Make Money
* Doubloons can be made by saying 'RUMPUS', collecting taxes, and leveling up your rank
* Doubloons can be used to buy/upgrade villages
* Doubloons can also be used to purchase attack and defence units (see below)

### How War Works
* Each kingdom has a certain attack and defence level
* To attack another kingdom you send attack units. If you have more attack units than they have defence units, you win!
* If you send less attack units than they have defence units, you lose!
* Attack units are lost after each battle
* The winner of the battle gets the loser's lowest population village, so make sure you keep your defence level up!

### How Ranks Work
* Each player starts off as a peasant
* Each time you say 'RUMPUS' you gain a rumpus count
* After enough rumpus counts you will be able to level up, giving you a doubloon reward and price discount
