#!/usr/bin/python2.7

''' Takes tweets with Twitpic images and posts them to Picasa '''

__author__ = 'tweet2picasa@kasa.nu'

import twitter
import re
import os
import urllib2
import gdata.photos.service
import gdata.media
import gdata.geo
import argparse
import time, datetime
import email.utils

class PicasaUploader:
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

def main():
   parser = argparse.ArgumentParser(description='Post all Twitpic tweets to Picasa. Only supports public timelines and\
       can only handle max 200 tweets back in time.')
   parser.add_argument('user_twitter', metavar='username_twitter', help='Username for Twitter')
   parser.add_argument('start_time', metavar='start_time', help='Starttime of tweets (inclusive) in format YYYYmmdd')
   parser.add_argument('end_time', metavar='end_time', help='Endtime of tweets (exclusive) in format YYYYmmdd')
   parser.add_argument('user_picasa', metavar='username_picasa', help='Username for Picasa')
   parser.add_argument('pwd_picasa', metavar='password_picasa', help='Password for Picasa')
   parser.add_argument('album_name', metavar='album_name', help='Albumname for Picasa')

   args = parser.parse_args()
   
   time_format = "%Y%m%d"
   startdate = datetime.datetime.fromtimestamp(time.mktime(time.strptime(args.start_time, time_format)))
   enddate = datetime.datetime.fromtimestamp(time.mktime(time.strptime(args.end_time, time_format)))
   
   statuses = twitter.Api().GetUserTimeline(user=args.user_twitter, count=200)
   
   pu = PicasaUploader(args.user_picasa, args.pwd_picasa, args.album_name)
   
   for s in statuses:
      tweetdate = datetime.datetime.fromtimestamp(time.mktime(email.utils.parsedate(s.created_at)))
      if (startdate < tweetdate and tweetdate < enddate):
         m = re.match("(.*)http://twitpic.com/([\d\w]+)(.*)", s.text)
         if m != None:
            picname = m.group(2)
            url = "http://twitpic.com/show/large/" + picname
            my_picture = urllib2.build_opener().open(url).read()
            filename = ".tweet2picasa_" + picname + ".jpg"
            fout = open(filename, "wb")
            fout.write(my_picture)
            fout.close()
            text = m.group(1) + m.group(3)
            pu.upload_image(filename, text)
            os.remove(filename)
            print "Uploaded '" + picname + "' from " + s.created_at + " with text: " + text

if __name__ == '__main__': main()