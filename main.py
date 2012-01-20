#!/usr/bin/python
from gi.repository import Gtk
from gi.repository import GdkPixbuf
import xml.dom.minidom
import sys
import tweepy
import urllib2

#Currently hardcoded keys. TO_DO: Store them in XML and read before launching
cons_key='qLrZk3rJw86PztLalnb6g'
cons_secret='g1jCYMlhBZcYlFsg3ecBnCNm5zcrQMbGTBfIycvbRcc'
#access_token='76611638-TSnLa31lRXEp3qBNpxKmi2gyiW0jCLpOKeEsK5i6A'
#access_token_secret='wgC9xwGpCMOQQtDazOZF7wtvCA5MrtcaLT6gLv1vdE'


config_file=xml.dom.minidom.parse('/home/gaurav/output.xml')

def write_to_file(at,ats):
	doc=xml.dom.minidom.Document()
	credentials=doc.createElementNS('Access Credentials','credentials')
	doc.appendChild(credentials)
	access_token_element=doc.createElementNS('Access Token','access_token')
	credentials.appendChild(access_token_element)
	access_token_desc=doc.createTextNode(at.strip())
	access_token_element.appendChild(access_token_desc)
	access_token_secret_element=doc.createElementNS('Access Token Secret','access_token_secret')
	credentials.appendChild(access_token_secret_element)
	access_token_secret_desc=doc.createTextNode(ats.strip())
	access_token_secret_element.appendChild(access_token_secret_desc)
	f=open('/home/gaurav/output.xml','wb')
	try:
		f.write(doc.toprettyxml(indent=' '))
	finally:
		f.close()

#Class of the main window
class MainWindow():
	def read_from_file(self):
		self.status=0
		self.access_token=config_file.getElementsByTagName('access_token')[0].firstChild.data
		self.access_token_secret=config_file.getElementsByTagName('access_token_secret')[0].firstChild.data
		self.auth=tweepy.OAuthHandler(cons_key,cons_secret)
		if self.access_token.strip()=='' and self.access_token_secret.strip()=='':
			self.status=0
			print 'Configuration not set'
		else:
			self.status=1
			print self.access_token,self.access_token_secret
			self.auth.set_access_token(self.access_token.strip(),self.access_token_secret.strip())
			self.api=tweepy.API(self.auth)
		return self.status
	def tweet(self,str):
		self.api.update_status(str)	
	def stream(self):
			self.message=['','','','','','','','','','']
			self.statuses=['','','','','','','','','','']
			self.statuses=self.api.home_timeline()
			for i in range(0,10):
				self.message[i]=self.statuses[i].text
			return self.message
	def get_users(self):
		self.users=['','','','','','','','','','']
		self.statuses=['','','','','','','','','','']
		self.statuses=self.api.home_timeline()
		for i in range(0,10):
			self.users[i]=self.statuses[i].user.screen_name
		return self.users
	
	#Main Window constructor
	def __init__(self):
		self.message=['','','','','','','','','','']
		self.users=['','','','','','','','','','']
		self.image_url=['','','','','','','','','','']
		self.loaders=['','','','','','','','','','']
		self.status=self.read_from_file()
		self.gbuilder=Gtk.Builder()
		self.gbuilder.add_from_file('main_ui.glade')
		dic={'on_Quit_activate':self.test1,
		'on_ButtonSend_clicked':self.send_message,
		'on_Settings_activate':self.settings,
		'on_Reply_clicked':self.reply,
		'on_Refresh_clicked':self.refresh,
		'on_Refresh_2_activate':self.refresh,
		'on_Retweet_clicked':self.retweet,
		'on_Favourite_clicked':self.favourite,
		'on_ButtonAuthorize_clicked':self.get_auth_url,
		'on_ButtonAuth_clicked':self.authorize}
		self.gbuilder.connect_signals(dic)
		self.auth_dialog=self.gbuilder.get_object('AuthDialog')

		#Creating various lists of widgets
		self.user_list=[self.gbuilder.get_object('User_{0}'.format(i)) for i in range(0,10)]
		self.message_list=[self.gbuilder.get_object('Message_{0}'.format(i)) for i in range(0,10)]
		self.tweet_button_list=[self.gbuilder.get_object('Tweet_{0}'.format(i)) for i in range(0,10)]
		self.reply_list=[self.gbuilder.get_object('Reply_{0}'.format(i)) for i in range(0,10)]
		self.retweet_list=[self.gbuilder.get_object('Retweet_{0}'.format(i)) for i in range(0,10)]
		self.favourite_list=[self.gbuilder.get_object('Favourite_{0}'.format(i)) for i in range(0,10)]
		self.image_list=[self.gbuilder.get_object('Image_{0}'.format(i)) for i in range(0,10)]
		
		self.MainWin=self.gbuilder.get_object('MainWin')
		self.Quit=self.gbuilder.get_object('Quit')
		self.ButtonSend=self.gbuilder.get_object('ButtonSend')
		self.MainWin.show()
		if self.status==0:
			self.auth_dialog.show_all()
		else:
			print self.api.auth.access_token
		
			statuses=self.api.home_timeline()
			for i in range(0,10):
				self.loaders[i]=GdkPixbuf.PixbufLoader()
				self.loaders[i].set_size(40,40)
				self.image_url[i]=urllib2.urlopen(statuses[i].user.profile_image_url)
				self.loaders[i].write(self.image_url[i].read())
				self.loaders[i].close()
		
			for j in range(0,10):
				self.image_list[j].set_from_pixbuf(self.loaders[j].get_pixbuf())

			self.message=self.stream()
			self.users=self.get_users()
		
			for j in range(0,10):
				self.message_list[j].set_text(self.message[j])
		
			for j in range(0,10):
				self.user_list[j].set_text(self.users[j])
		
	def test1(self,widget):
		Gtk.main_quit()
	def send_message(self,widget):
		text_entry=self.gbuilder.get_object('EntryMessage')
		str=text_entry.get_text()
		self.tweet(str)
		text_entry.set_text("")
	def settings(self,widget):
		dialog=self.gbuilder.get_object('AuthDialog')
		dialog.show_all()
	def reply(self,button):
		text_entry=self.gbuilder.get_object('EntryMessage')
		index=self.reply_list.index(button)
		text_entry.set_text('@'+self.user_list[index].get_text()+' ')
	def refresh(self,widget):
		message=['','','','','','','','','','']
		users=['','','','','','','','','','']
		message=self.stream()
		users=self.get_users()
		for j in range(0,10):
			self.message_list[j].set_text(message[j])
		for j in range(0,10):
			self.user_list[j].set_text(users[j])
		
	def retweet(self,button):
		index=self.retweet_list.index(button)
		rt=self.api.home_timeline()[index].id
		self.api.retweet(rt)
		
	def favourite(self,button):
		index=self.favourite_list.index(button)
		fav=self.api.home_timeline()[index].id
		self.api.create_favorite(fav)
		
	def get_auth_url(self,widget):
		auth_url=self.auth.get_authorization_url()
		LabelAuthUrl=self.gbuilder.get_object('LabelAuthUrl')
		LabelAuthUrl.set_text(auth_url)
	
	def authorize(self,widget):
		EntryPIN=self.gbuilder.get_object('EntryPIN')
		pin=EntryPIN.get_text().strip()
		self.auth.get_access_token(pin)
		access_token=self.auth.access_token.key
		access_token_secret=self.auth.access_token.secret
		self.api=tweepy.API(self.auth)
		write_to_file(access_token,access_token_secret)
		statuses=self.api.home_timeline()
		for i in range(0,10):
			self.loaders[i]=GdkPixbuf.PixbufLoader()
			self.loaders[i].set_size(40,40)
			self.image_url[i]=urllib2.urlopen(statuses[i].user.profile_image_url)
			self.loaders[i].write(self.image_url[i].read())
			self.loaders[i].close()
		
		for j in range(0,10):
			self.image_list[j].set_from_pixbuf(self.loaders[j].get_pixbuf())

		self.message=self.stream()
		self.users=self.get_users()
		
		for j in range(0,10):
			self.message_list[j].set_text(self.message[j])
		
		for j in range(0,10):
			self.user_list[j].set_text(self.users[j])

win=MainWindow()
Gtk.main()
		
