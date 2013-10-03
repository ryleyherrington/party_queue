import cgi
import wsgiref.handlers

import gdata.urlfetch
import gdata.service
import gdata.youtube
import gdata.youtube.service

from google.appengine.ext import webapp
from google.appengine.ext import db
from datetime import datetime, timedelta

gdata.service.http_request_handler = gdata.urlfetch
		
class Songs(db.Model):
	author = db.StringProperty()
	song = db.StringProperty()	
	date = db.DateTimeProperty(auto_now_add=True)

class GetQueue(webapp.RequestHandler):
	def get(self):
		songs = db.GqlQuery("SELECT * FROM Songs") 

		self.response.out.write("-----------<br/>")
		for s in songs:
			self.response.out.write("<b>"+s.song+ "</b> by " + s.author)
			self.response.out.write("<br/>-----------<br/>")
					
		

class InsertSong(webapp.RequestHandler):
	def post(self):
		S = Songs()	
		S.song=self.request.get('song')
		S.author=self.request.get('author')
		S.put()

		self.redirect('/')
	
class MainPage(webapp.RequestHandler):

	def post(self):
		songbook_name='ryley'
		S = Song(parent=songbook_key(songbook_name))	
		S.song= self.request.get('song')
		S.put()

		self.redirect('/')

	def get(self):
		
		search_term = cgi.escape("Holy Grail".encode('UTF-8'))
		songs = db.GqlQuery("SELECT * FROM Songs") 

		for s in songs:
			if s.song == None:
				search_term = cgi.escape("Holy Grail".encode('UTF-8'))
			elif s.song is not None:
				search_term = cgi.escape(s.song.encode('UTF-8'))

	
		if not search_term:
			self.redirect('/')
			return
			
		self.response.out.write("""<html><head><title>
				Party Queue</title>
				<meta name="viewport" content="width=device-width/>
				<link type="text/css" rel="stylesheet" href="/stylesheets/main.css" />
				</head><body><div id="video_listing">""")
		
		self.response.out.write('<table border="0" cellpadding="2" '
				'cellspacing="0">')

		client = gdata.youtube.service.YouTubeService()
		query = gdata.youtube.service.YouTubeVideoQuery()
		
		query.vq = search_term 
		query.max_results = '1'
		feed = client.YouTubeQuery(query)
		
		for entry in feed.entry:
			if entry.GetSwfUrl():
				swf_url = entry.GetSwfUrl()+ "&autoplay=1"
				#self.response.out.write("""<object width="425" height="355">
				#self.response.out.write("%s" % swf_url)
				self.response.out.write("""<object>
					<param name="movie" value="%s"></param>
					<iframe src="%s" wmode="transparent" autoplay="1" 
					width="640" height="500"></iframe></object>
					<br />""" % (swf_url, swf_url))
				self.response.out.write('<tr><td height="20"><hr class="slight"/></tr>')
		self.response.out.write('</table><br />')
		self.response.out.write('</body></html>')

def main():
	application = webapp.WSGIApplication([
						('/insert', InsertSong),
						('/queue', GetQueue),
						('/', MainPage)],
						debug=True)
	wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
	main()
