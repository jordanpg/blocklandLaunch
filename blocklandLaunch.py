import socket, argparse, os, hashlib, os.path, urllib

def recv(sock, size):
	buffer = []
	curr = 0
	while curr < size:
		print curr, sock, size
		add = sock.recv(min(size - curr, 1024))
		print 
		if add == b'':
			print "empty", add, curr, sock, size
			break
		buffer.append(add)
		print buffer
		curr += len(add)
		print curr
	print "exit recv"
	return b''.join(buffer)

def getSHA1(file):
	if not os.path.isfile(file):
		return 0

	with open(file, 'rb') as f:
		return hashlib.sha1(f.read()).hexdigest()

class Launcher:
	def __init__(self, path):
		self.files = []
		self.update = []
		self.download = ''
		self.dir = path
		self.grabbed = False

	def grabFileList(self):
		print "Retrieving latest version listings..."

		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		sock.connect(("update.blockland.us", 80))

		sock.send("GET /latestVersion.php HTTP/1.0\r\n")
		sock.send("Host: update.blockland.us\r\n")
		sock.send("User-Agent: blocklandWIN/2.0\r\n\r\n")

		buff = ''
		while True:
			d = sock.recv(1024)

			if d == b'':
				break

			buff += d

		# print buff

		if not 'DOWNLOADURL' in buff:
			buff = ''

		pos = buff.find('DOWNLOADURL')
		buff = buff[pos:]
		lines = buff.split('\n')

		self.download = lines[0].split('\t')[1]
		self.files = lines[1:]

		self.grabbed = True

	def generateUpdateList(self):
		print "Generating list of files to update..."
		if not self.grabbed:
			self.grabFileList()

		for i in self.files:
			l = i.split('\t')
			if len(l) < 2:
				continue
			name = l[0]
			hash = l[1]

			path = self.dir + name
			if not os.path.isfile(path):
				self.update.append(i)
			else:
				h = getSHA1(path)
				if h != hash:
					self.update.append(i)

	def grabFiles(self):
		if len(self.update) == 0:
			return

		print "Downloading update list..."
		for i in self.update:
			l = i.split('\t')
			if len(l) < 2:
				continue
			name = l[0]
			hash = l[1]

			print "RETRIEVING FILE: " + name + " ..."
			path = self.dir + name
			dirname = os.path.dirname(path)
			if not os.path.exists(dirname):
				os.makedirs(dirname)
			urllib.urlretrieve(self.download + '/' + hash, path)


def launcher(argv):
	path = argv.p
	ignore = argv.i

	if path == None:
		path = os.getcwd() + '/Blockland'

	# print path

	launch = Launcher(path)
	launch.generateUpdateList()

	if len(launch.update) > 0:
		if not ignore:
			r = raw_input("Are you sure you want to update " + str(len(launch.update)) + " files? (y/n)\t")

			if r != 'y' and r != 'Y':
				return

		launch.grabFiles()
		print "Updated " + str(len(launch.update)) + " files."
	else:
		print "All files are already up-to-date."


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Blockland Custom Launcher")
	parser.add_argument('-p', metavar='P', help='Blockland install directory', required=False)
	parser.add_argument('-i', help='Don\'t ask to update', required=False, action="store_true")

	argv = parser.parse_args()
	launcher(argv)