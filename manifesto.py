#! /usr/bin/env python

import os, re, urllib2, argparse, sys
			
class Manifesto:

	template 	= ''
	cache 		= []
	network 	= []
	fallback 	= []

	args 		= None
	crawler 	= None
	
	def __init__(self, task, args):
		self.args 		= args
		self.crawler 	= FileCrawler(args.ignore_remote)
		self.processTask(task)

		self.writeManifestToFile(
			task['output'], 
			task['comment'] if 'comment' in task else '', 
			'\n'.join(self.cache), 
			'\n'.join(self.network), 
			'\n'.join(self.fallback)
		)

	def processTask(self, task):

		self.cache 		= self.filterSection( self.processSection(task['cache']), task['filters']['cache'] )
		self.network 	= self.filterSection( self.processSection(task['network']), task['filters']['network'] ) 
		self.fallback 	= self.filterSection( self.processSection(task['fallback']), task['filters']['fallback'] )

	def processSection(self, assets):
		if assets == None:
			return []
		else:
			bag = []

			for asset in assets:
				bag += self.crawler.crawl(asset)

			return sorted( set(bag) )

	def filterSection(self, assets, filter):
		filtered = []

		for asset in assets:
			if self.matchesFilter(asset, filter) == False:
				asset = asset.replace('/./', '/')
				filtered.append(asset)

		return filtered		

	def matchesFilter(self, match, filters):
		if filters == None:
			return False

		for pattern in filters:
			if re.search(pattern, match) != None:
				return True

		return False		

	def writeManifestToFile(self, filepath, comments, cache, network, fallback):
		pathToTemplate = os.path.join( os.path.dirname( os.path.realpath(__file__) ), 'template.manifest')

		with open(pathToTemplate, 'r') as template:
			string = template.read() % { 'comments' : comments, 'cache' : cache, 'network' : network, 'fallback' : fallback }

		if self.args.printToCLI == False:
			with open(filepath, 'w') as manifest:
				manifest.write(string)
		else:
			print string
					

class FileCrawler:

	ignoreRemote 	= False
	patterns 		= {
		'css'  	: [['url\((\'|"|)(.+?)(\'|"|)\)', 1]],
		'html' 	: [['<link.+?href=(\'|")(.+?)(\'|")', 1], ['<script.+?src=(\'|")(.+?)(\'|")', 1]]
	}

	def __init__(self, ignoreRemote = False):
		self.ignoreRemote = ignoreRemote

	def isUrl(self, path):
		return path.startswith('www') or path.startswith('http') or path.startswith('//')

	def open(self, path):
		if self.isUrl(path):
			handle 	= urllib2.urlopen(path)
			ext 	= handle.info().getsubtype()
		else:
			handle 	= open(path, "r")
			ext 	= os.path.splitext(path)[1].replace('.', '')

		return (handle, ext)

	def abs(self, parent, path):
		parentIsUrl = self.isUrl(parent)
		pathIsUrl 	= self.isUrl(path)

		if pathIsUrl:
			path = path
		elif parentIsUrl:
			path = os.path.join(os.path.dirname(parent), path)
		elif not parentIsUrl:
			path = os.path.join(os.path.dirname(parent), path)	

		return path 

	def crawlDir(self, dir, recursive = True):
		paths = []

		for root, dirnames, filenames in os.walk(dir):
			for filename in filenames:
				paths.append(os.path.join(root, filename))

		if recursive == False:
			return paths		
		else:
			bag = []

			for path in paths:
				bag += self.crawl(path, recursive)

			return bag

	def crawlString(self, path, ext, string, recursive = True):
		if ext in self.patterns:
			patterns 	= self.patterns[ext]
			paths 		= [path]

			for pattern in patterns:
				regex 	= pattern[0]
				matches = re.findall(regex, string)
				for match in matches:
					position 	= pattern[1]
					match 		= self.abs(path, match[position])

					if recursive == True:
						paths += self.crawl(match, recursive)
					else:	
						paths.append(match)
			return paths
		else:
			return [path]

	def crawl(self, path, recursive = True):
		if os.path.isdir(path):
			return self.crawlDir(path, recursive)
		elif self.isUrl(path) and self.ignoreRemote == True:
			return [path]
		else:	
			handle, ext = self.open(path)

			if ext in self.patterns:
				return self.crawlString(path, ext, handle.read(), recursive)
			else:
				return [path]	

try: 
	import yaml
except:
	print 'PyYaml package missing, type "pip install pyyaml" to install it'

parser 	= argparse.ArgumentParser(description='Generate HTML5 manifest files.')
parser.add_argument('target', nargs='?', default=['.manifest.yaml'], help='yaml file with tasks')		
parser.add_argument('--print', '-p', action='store_true', dest='printToCLI', help='print output to terminal instead of file')
parser.add_argument('--ignore-remote', '-r', action='store_true', help='ignore remote files')
args 	= parser.parse_args()

target 	= args.target[0]

try:
	taskFile = open(target)
except:
	print 'Could not open file:', target
	sys.exit(1)

try:
	tasks = yaml.load(taskFile)
except:
	print 'Malformed yaml file.'
	sys.exit(1)

for key in tasks:
	Manifesto(tasks[key], args)	