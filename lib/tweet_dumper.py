#!/usr/bin/env python
# encoding: utf-8

import tweepy #https://github.com/tweepy/tweepy

#Twitter API credentials
consumer_key = "bwqeAKwmrw78nX4zmTXzu4h9e"
consumer_secret = "4VeGEXCVceuAZGOMaU6OztIsNIp9FaAzm30JJZEgK5dyKOgJqb"
access_key = "1732960382-uANrdoaJfRxVAEbxewg1NNlhctjgCbi5jm8raYY"
access_secret = "sZ3koHkK49dg7f54h8xtuUcZo5moCD1l7mDl9oZryeR6l"


def get_all_tweets(screen_name):
	#Twitter only allows access to a users most recent 3240 tweets with this method
	
	#authorize twitter, initialize tweepy
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)
	api = tweepy.API(auth)
	
	#initialize a list to hold all the tweepy Tweets
	alltweets = []	
	
	#make initial request for most recent tweets (200 is the maximum allowed count)
	new_tweets = api.user_timeline(screen_name = screen_name,count=200)
	
	#save most recent tweets
	alltweets.extend(new_tweets)
	
	#save the id of the oldest tweet less one
	oldest = alltweets[-1].id - 1
	
	#keep grabbing tweets until there are no tweets left to grab
	while len(new_tweets) > 0:
		print ("getting tweets before %s" % (oldest))
		
		#all subsiquent requests use the max_id param to prevent duplicates
		new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)
		
		#save most recent tweets
		alltweets.extend(new_tweets)
		
		#update the id of the oldest tweet less one
		oldest = alltweets[-1].id - 1
		
		print ("...%s tweets downloaded so far" % (len(alltweets)))

	outtweets = [tweet.text.encode("utf-8") for tweet in alltweets]
	# outtweets = [tweet.text for tweet in alltweets]
	
	# write the txt file
	with open('%s_tweets.txt' % screen_name, 'wb') as f:
		for tweet in outtweets:
			f.write(tweet)
			f.write(bytes("\n", 'utf-8'))

if __name__ == '__main__':
	#pass in the username of the account you want to download
	get_all_tweets("officialjaden")
