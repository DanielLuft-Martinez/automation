#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from bs4 import BeautifulSoup
import argparse
import re
from IPython.utils.shimmodule import ShimWarning
import warnings; warnings.simplefilter('ignore', ShimWarning)
from IPython.nbformat import v3, v4 # using old versions give warnings
import os
import shutil



# make sure to 'right-click save' the page



# In[ ]:

try:

	# handle args, get the html file
	parser = argparse.ArgumentParser(prog='domyhw.py', 
		description = 'Turn the canvas html page of my cse 20 assignment into convienient formats.\n\rHandy and less tedious',
		usage='%(prog)s hwX.html [options]')

	parser.add_argument('filename', help='the html file')
	parser.add_argument('-d','--dir', action='store_true', help='make a seperate dir for the resulting files')
	parser.add_argument('-a','--all', action='store_true', help='produce all formats of output')
	parser.add_argument('-p','--python', action='store_true', help='produce only the python version of the output')
	parser.add_argument('-i','--idle', action='store_true', help='produce only the idle enhanced python version of the output, ANSI encoding')
	parser.add_argument('-j','--jupyter', action='store_true', help='produce only the ipython notebook version of the output')



	args = parser.parse_args()

	file = open(args.filename, encoding="utf8", errors='ignore')

	contents = file.read()

	soup = BeautifulSoup(contents, 'lxml')


	# In[ ]:


	ques = soup.find_all("div", attrs={"aria-label":"Question","class":"quiz_sortable question_holder"})


	# In[ ]:


	questions = []
	statements = []

	len(ques)


	# In[ ]:


	def comment_red_text(raw):
		# comment red text
		# clean and prep otherwise
		red = raw.find_all("span", attrs={"style":"color: #ff0000;"})
		red += raw.find_all("span", attrs={"style":"font-weight: 400; color: #ff0000;"})
		for r in red:
			r.string = '# '+r.string

			
	def statement_text(raw):
		statement = raw.find('div', attrs={'class':"question_text user_content enhanced"})
		text = question.getText()
		return text

	def question_text(reded):
		# essay vs short answer
		question = reded.find('div', attrs={'class':"question_text user_content enhanced"})
		text = question.getText()
		lines = text.split('\n')
		ntext = ""
		code_start = False 
		for line in lines:
			nline = (line+"\n").replace('“', '\'').replace('”', '\'').replace(u'\xa0', u' ')
			if ("record " in nline or "your code" in nline or "code starts here" in nline) and 'Based' not in nline:
				ntext+='# '+nline+'\n'
			else:
				if re.match(r'\S+\s{5,}', nline) is not None:
					e1 = re.search(r'\S+\s{5,}', nline).start()
					e2 = nline[e1:].find(' ')
					nline = nline[:e1+e2] + ' # ' +nline[e1+e2:]
				else:
					nline = nline #remnant
				if '>>>' in nline:
					nline = nline.replace('>>>','').lstrip()
					code_start = True
				nline = nline.replace('>>>','')
				if code_start:
					ntext+=nline+'\n'
				else:
					ntext+='# '+nline+'\n'
		return ntext


	def code_to_py(pfile, text, num):        
		pfile.write('# <codecell>') # speceial comment for later conversion to ipynb

		# putting each question in a try block 
		# and spacing them with null input()
		# add printing of each question before running it
		pfile.write('\n# question {}\n'.format(num))
		for line in text.split('\n'):
			pfile.write(line+'\n')
		pfile.write('\n')
		
		
	def code_to_idle_py(ifile, text, num):

		# putting each question in a try block 
		# and spacing them with null input()
		# add printing of each question before running it
		ifile.write('# question {}\n\n'.format(num))
		ifile.write('print(\'\\nquestion {}\\n\')\n'.format(num))

		ifile.write('print(\"\"\"{}\"\"\")\n'.format(text))

		# writing each python code question within try block
		ifile.write('try:\n')
		for line in text.split('\n'):
			ifile.write('\t'+line+'\n')
		#ifile.write('\t'+'input()\n') # pause for idle
		ifile.write('except:\n')
		ifile.write('\t'+'e = sys.exc_info()[0]\n')
		ifile.write('\t'+'print(e)\n')
		ifile.write('\t'+'input()\n') # pause for idle
		
		
		# now we're adding the enhancement
		ifile.write('try:\n')
		for line in """confirmed = False
while not confirmed:
	print('')
	new_code = input('please enter the next part of the program: (nothing to skip)')
	if(len(new_code) < 2):
		break
	print(f'this is what you entered:{new_code}')
	confirm = input('are you happy with what you entered? [y/n]: '  )
	if confirm[0].lower() == 'y':
		print('your code will now be executed')
		exec(new_code)
		confirm = input('are you happy with how it ran? [y/n]: '  )
		if confirm[0].lower() == 'y':
			confirmed = True""".split('\n'):
			ifile.write('\t'+line+'\n')
#		ifile.write('\t'+'input()\n') # pause for idle
		ifile.write('except:\n')
		ifile.write('\t'+'e = sys.exc_info()[0]\n')
		ifile.write('\t'+'print(e)\n')
		ifile.write('\t'+'input()\n') # pause for idle



	def text_to_py(pfile, text):
		
		pfile.write('# <markdowncell>') # speceial comment for later conversion to ipynb
		
		for line in text.split('\n'):
			pfile.write('# ' + line+'\n')
			
	def text_to_idle_py(ifile, text):
		
		ifile.write('# <markdowncell>') # speceial comment for later conversion to ipynb
		
		for line in text.split('\n'):
			ifile.write('# ' + line+'\n')


	def py_to_ipynb(filname):
		
		
		
		with open(filname+".py",encoding="utf8", errors='ignore') as fpin:
			text = fpin.read()
		text += """
		<markdowncell>

		If you can read this, reads_py() is no longer broken! 
		"""
		nbook = v3.reads_py(text)
		nbook = v4.upgrade(nbook)  # Upgrade v3 to v4

		jsonform = v4.writes(nbook) + "\n"
		with open(filname+".ipynb", "w") as fpout:
			fpout.write(jsonform)
		
	
	def idle_enhancement():
		confirmed = False
		while not confirmed:
			print()
			new_code = input('please enter the next part of the program: (nothing to skip)')
			if(len(new_code) < 1):
				break
			print(f'this is what you entered:\n{new_code}')
			confirm = input('are you happy with what you entered? [y/n]: '  )
			if confirm[0].lower() == 'y':
				print('your code will now be executed')
				exec(new_code)
				confirm = input('are you happy with how it ran? [y/n]: '  )
				if confirm[0].lower() == 'y':
					confirmed = True
	# In[ ]:


	filename = args.filename
	filename =filename[:-5].replace(' ','_')
	filename


	# In[ ]:


	pfile = open(filename+'.py', 'w')
	ifile = open(filename+'.idle.py', 'w')

	ifile.write('import sys\n')
	ifile.write('# if asked, use ANSI encoding\n')
	ifile.write('# this will not work out right, please be sure to try running and fix for errors\n')
	ifile.write('# you will learn more by debugging\n')

	# In[ ]:





	# In[ ]:


	qnum = 0
	for q in ques:
		if "Spacer" in str(q.find_all("span",{"role":"heading"})):
			stext = question_text(q)
			text_to_py(pfile, stext)
			text_to_idle_py(ifile, stext)
		else:
			qnum+=1
			comment_red_text(q)
			qtext = question_text(q)
			code_to_py(pfile,qtext,qnum)
			code_to_idle_py(ifile,qtext,qnum)


	# In[ ]:


	ifile.close()
	pfile.close()


	# In[ ]:



	py_to_ipynb(filename)

	# this could really be much more elegant
	if args.dir:
		
		dirname = 'processed_'+filename
		os.mkdir(dirname)
		
		if args.all:
			shutil.move(filename+'.py', dirname)
			shutil.move(filename+'.idle.py', dirname)
			shutil.move(filename+'.ipynb', dirname)
		elif args.python:
			shutil.move(filename+'.py', dirname)
			os.remove(filename+'.idle.py')
			os.remove(filename+'.ipynb')
		elif args.idle:
			shutil.move(filename+'.idle.py', dirname)
			os.remove(filename+'.py')
			os.remove(filename+'.ipynb')
		elif args.jupyter:
			shutil.move(filename+'.ipynb', dirname)
			os.remove(filename+'.py')
			os.remove(filename+'.idle.py')
		else:
			shutil.move(filename+'.py', dirname)
			shutil.move(filename+'.idle.py', dirname)
			shutil.move(filename+'.ipynb', dirname)
	
	else:
	
		if args.all:
			print("",end="") # dumb
		elif args.python:
			os.remove(filename+'.idle.py')
			os.remove(filename+'.ipynb')
		elif args.idle:
			os.remove(filename+'.py')
			os.remove(filename+'.ipynb')
		elif args.jupyter:
			os.remove(filename+'.py')
			os.remove(filename+'.idle.py')

	
	
	# In[ ]:
except Exception as e:
	print(e)

	
