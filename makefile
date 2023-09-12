.PHONY:run
run:
	nohup python3.10 -u onbot.py >> ./bot.out 2>&1 &

.PHONY:ps
ps:
	ps jax | grep onbot.py