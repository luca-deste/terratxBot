# Terra Transaction Bot
A telegram bot to help you track your transactions on the terra blockchain.

## How to use it
If you want to use it you can search for it on telegram @terratxbot.
If you prefer to host it by yourself you just need to create a file named config.py where you should insert the token of your bot with the sintax provided here:
```
token = "YOUR_TOKEN"
```
In advance you should comment some parts that are marked for you (as you probably won't use the feature to make announcements).


TODO:
- [x] Create an announcement feature to send messages to users
- [ ] Give more informations about the transaction inside the messages
- [ ] Give to the users the possibility to monitor more than one address
- [ ] Change the current api's whit the python sdk to provide a more fast way to query the blockchain and to avoid server issues
