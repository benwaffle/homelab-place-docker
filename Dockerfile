FROM python

RUN pip install requests image

ADD bot.py template.png /bot/
WORKDIR /bot

CMD python3 bot.py template.png 31 37 $USERNAME $PASSWORD
