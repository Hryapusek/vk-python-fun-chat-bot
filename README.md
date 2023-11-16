## vk-python-stats
### Description
Bot works from your **vk persnal page**.
On start it will collect information about chat with given CHAT_ID.  
CHAT_ID usually not so big. For example 120. You can get it from address line in browser.

Bot algorithm is as follows:
1. Process messages not older than 3 month and create `vk_common/stats.txt` file.
2. Start listening to new messages and searching commands in these.

Commands are:
- `/my_stats`
- `/chat_stats`
- `/cock`

### Quick start
You can obtain the token on [vkhost.github.io](https://vkhost.github.io)
Start with
```python
pyhton3 main.py token CHAT_ID
```
or if you put token in vk_common/token.txt.
```python
pyhton3 main.py CHAT_ID
```
