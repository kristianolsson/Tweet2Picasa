#!/usr/bin/python2.7

import twitter
import re
import os
import urllib2
import gdata.photos.service
import gdata.media
import gdata.geo
import argparse



class PicasaUpload:
	def __init__(self, username, password, title):
		self.gd_client = gdata.photos.service.PhotosService()
		self.gd_client.email = username
		self.gd_client.password = password
		self.gd_client.source = 'tweet2picasa'
		self.gd_client.ProgrammaticLogin()
		album = self.gd_client.InsertAlbum(title=title, summary='')
		self.album_url = '/data/feed/api/user/%s/albumid/%s' % (username, album.gphoto_id.text)
		self.username = username
	
	def upload_image(self, filename, text):
		photo = self.gd_client.InsertPhotoSimple(self.album_url, 'photo', 
		    text, filename, content_type='image/jpeg')


class TweetFetcher:
	def get_tweets(self, user, tweets):
		api = twitter.Api()
		return api.GetUserTimeline(user, tweets)


def main():
	parser = argparse.ArgumentParser(description='Post all twitpic tweets to Picasa')
	parser.add_argument('user_twitter', metavar='username_twitter', help='Username for Twitter')
	parser.add_argument('tweets', metavar='tweets', type=int, help='Number of tweets to get')
	parser.add_argument('user_picasa', metavar='username_picasa', help='Username for Picasa')
	parser.add_argument('pwd_picasa', metavar='password_picasa', help='Password for Picasa')
	parser.add_argument('album_name', metavar='album_name', help='Albumname for Picasa')

	args = parser.parse_args()
	#print args.user_twitter

	statuses = TweetFetcher().get_tweets(args.user_twitter, args.tweets)
	
	#pu = PicasaUpload(args.user_picasa, args.pwd_picasa, args.album_name)
	
	for s in statuses:
		m = re.match("(.*)http://twitpic.com/([\d\w]+).*", s.text)
		if m != None:
			url = "http://twitpic.com/show/large/" + m.group(2)
			opener1 = urllib2.build_opener()
			page1 = opener1.open(url)
			my_picture = page1.read()
			filename = ".tweet2picasa_" + m.group(2) + ".jpg"
			fout = open(filename, "wb")
			fout.write(my_picture)
			fout.close()
			
			print s.text

			#pu.upload_image(filename, m.group(1))
			os.remove(filename)

if __name__ == '__main__': main()