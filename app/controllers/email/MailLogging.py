import os
import json
import shutil

dir = os.getcwd()+'/logs'

class Debug:

	def createLog(self, dir=dir):
		if os.path.isdir(dir):
			shutil.rmtree(dir)
		os.mkdir(dir)

	def writeLog(self, name, content, directory='', extension='json',
				cwd=None):
		contentType = type(content)
		if cwd:
			dir = cwd
		directory = '{}/{}{}.{}'.format(dir, directory, name, extension)
		file = open(directory, 'w')
		if contentType == dict or contentType == list:
			json.dump(content, file)
		else:
			file.write(content)

debug = Debug()