#!/usr/bin/python


import SocketServer
import BaseHTTPServer
import os
import time


# GLOBAL CONSTANTS
PORT = 8080
TEMPLATE_FOLDER = "template"
MEDIA_FOLDER = "media_repo"
NO_AUTHOR = "N/A"
METADATA_FILENAME = "play.txt"
SPLIT_TOKEN = "`|"
EMPTY_TEXT = "&nbsp;"


# Helper functions
def read_folder_metadata(path):
	result = []
	try:
		metafile = open(path + "/" + METADATA_FILENAME, "r")
		filecontent = metafile.read()
		if not(filecontent is None):
			metarows = filecontent.split("\n")
			for metarow in metarows:
				metarow_cols = metarow.split(SPLIT_TOKEN)
				metarow_url = EMPTY_TEXT
				try:
					metarow_url = metarow_cols[0][2:]
				except:
					pass
                                metarow_name = metarow_url
                                try:
                                        metarow_name = metarow_cols[1]
                                except:
                                        pass
                                metarow_author = NO_AUTHOR
                                try:
                                        metarow_author = metarow_cols[2]
                                except:
                                        pass
				if len(metarow_url) > 1:
					result += [[metarow_url, metarow_name, metarow_author]]
	except:
		pass
	return result

def list_folder(url_context, path, is_list_file):
	result = ""
	file_names = os.listdir(path)
	folders = [file_name for file_name in file_names if (is_list_file == os.path.isfile(path + "/" + file_name))]
	folders_meta = read_folder_metadata(path)
	if len(folders_meta) < 1:
		for folder in folders:
			result += "<tr><td><a href='%s%s'>%s</a></td><td>%s</td></tr>\n" % (url_context, folder, folder, NO_AUTHOR)
	else:
                for folder_meta in folders_meta:
			result += "<tr><td><a href='%s%s'>%s</a></td><td>%s</td></tr>\n" % (url_context, folder_meta[0], folder_meta[1], folder_meta[2])
	return result

# Engine class
class RemoteMusicBoxHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	request_played_song = None

	def write_album_page(self, contextpath):
                try:
			# Validate
			# Send header
                        self.send_response(200)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
			# parse context path
			context_params = contextpath.split("/")
			album = context_params[0]
			if (len(context_params) > 1):
				template_file = open(TEMPLATE_FOLDER + "/playsong.txt" , "r")
				htmltxt = template_file.read()
				htmltxt = htmltxt.replace("`|PLAYING_ALBUM|`", album)
				htmltxt = htmltxt.replace("`|PLAYING_SONG|`", context_params[1])
				self.request_played_song = context_params[1]
			else:
				#print str(list_folder(album, MEDIA_FOLDER + "/" + album, True))
				album_songs = list_folder(album + "/", MEDIA_FOLDER + "/" + album, True)
				template_file = open(TEMPLATE_FOLDER + "/album.txt" , "r")
				htmltxt = template_file.read()
				htmltxt = htmltxt.replace("`|ALBUM_SONGS|`", album_songs)
			# Send content
                        self.wfile.write(htmltxt)
                except:
                        pass
	def write_album_enum_page(self):
		try:
			# Validate
			# Send header
                        self.send_response(200)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
			#
			template_file = open(TEMPLATE_FOLDER + "/album_enum.txt" , "r")
			htmltxt = template_file.read()
			htmltxt = htmltxt.replace("`|ALBUM_LIST|`", list_folder("/", MEDIA_FOLDER, False))
			# Send content
                	self.wfile.write(htmltxt)
		except:
			pass
	def do_HEAD(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
	def do_GET(self):
		if self.path == "/":
			self.write_album_enum_page()
		else:
			if (not(self.request_played_song is None)):
				print "Play... %s " % self.request_played_song
				self.request_played_song = None
				time.sleep(10)
			self.write_album_page(self.path[1:])



# Main/Entry procedure
httpd = SocketServer.TCPServer(("", PORT), RemoteMusicBoxHandler)

print "serving at port", PORT
try:
	httpd.serve_forever()
except KeyboardInterrupt:
	print "\nExit...\n"
	httpd.server_close()
