# DiscordChatBackupper
A Discord bot, which has useful commands for creating backups of server as MarkDown files.

___

Features:
 - creates a one-command backup of all the messages that were ever sent on that specific server
   - including images, links and all other files, that are supported for linking in Discord chat
 - anonymization of your nicknames (if you want to be private)
 - generating MarkDown (`.md`) files for each channel separately
 - packs all the files in one `.zip`
 - uploads zipped package to Discord chat, where the command was sent (if it's size is appropriate)
 - if any problems during uploading to Discord occur, program uploads the package to [www.file.io](https://www.file.io/), thus generating one-time download link, which is then sent in Discord chat
 
 ___
 
 In order to use this bot, you must first, create you own instance of a bot from [Discord Developer Portal](https://discord.com/developers/applications). Then you need to copy `bot token` to the file `token.txt`. 
 
 Also from that same site you need to copy `client id`, which you can pass to this link: "https://discord.com/oauth2/authorize?client_id=XXXXXXXXXXXXXXXXXXX&scope=bot" in place of those Xs. You will use this link in order to invite the bot to the server of your liking.