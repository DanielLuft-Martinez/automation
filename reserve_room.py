#!/usr/bin/env python
# coding: utf-8


import concurrent.futures
import os
import selenium
import datetime
import time
import sys
import imaplib
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys


if __name__ == '__main__':

	WEBSITE = 
	#'https://calendar.library.ucsc.edu/booking/seu'
	
	
	ROOM = 
	# '309 (9), '
	# '999 (99), '
	# room number and capacity shown on website
	
	EMAILS = []
	# cruzid1@ucsc.edu, cruzid2@ucsc.edu
	
	FNAMES = [] 
	# fname1, fname2
	
	LNAMES = [] 
	# lname1,lname2
	GROUP = ''
	# groupname
	

	driver_path = ''
	# 'C:/webdrivers/chromedriver.exe'
	
	linked_email = ''
	# email@gmail.com
	
	linked_email_app_pass = ''
	# abcdefghijkl



	start_time = time.perf_counter()


	times_8_12 = ['8:00am to 8:30am', '8:30am to 9:00am','9:00am to 9:30am', '9:30am to 10:00am','10:00am to 10:30am', '10:30am to 11:00am','11:00am to 11:30am', '11:30am to 12:00pm'] 
	times_12_4 = ['12:00pm to 12:30pm', '12:30pm to 1:00pm', '1:00pm to 1:30pm', '1:30pm to 2:00pm', '2:00pm to 2:30pm', '2:30pm to 3:00pm','3:00pm to 3:30pm', '3:30pm to 4:00pm' ]
	times_4_8 = ['4:00pm to 4:30pm', '4:30pm to 5:00pm', '5:00pm to 5:30pm', '5:30pm to 6:00pm', '6:00pm to 6:30pm', '6:30pm to 7:00pm','7:00pm to 7:30pm', '7:30pm to 8:00pm' ]
	times_8_11 = ['8:00pm to 8:30pm', '8:30pm to 9:00pm','9:00pm to 9:30pm', '9:30pm to 10:00pm','10:00pm to 10:30pm', '10:30pm to 11:00pm'] 
	times_sets = [times_8_12, times_12_4, times_4_8] # , times_8_11

	def attempt_room_reserve(i):
		try:
			
			driver = webdriver.Chrome(executable_path=driver_path)
			
			driver.get(WEBSITE)
			today = datetime.datetime.today()
			next_week = datetime.datetime.today() + datetime.timedelta(days=7)

			if today.month != next_week.month:
				nm_box = driver.find_element_by_xpath("//*[contains(@class, 'ui-datepicker-next ui-corner-all') and contains(@title, 'Next')]")
				nm_box.click()
				time.sleep(.5)
			cal_box = driver.find_element_by_link_text(str(next_week.day))

			cal_box.click()
			
			time.sleep(3)
			
			for rtime in times_sets[i]:
				try:
					res_box = driver.find_element_by_xpath("//*[contains(@title, '"+ROOM + rtime+ "')]")
					res_box.click()
					time.sleep(1)
				except:
					print('failure at ' + str(rtime))
			cont_box = driver.find_element_by_xpath("//*[contains(@name, 'Continue')]")
			cont_box.click()
			time.sleep(.5)
			fname_box = driver.find_element_by_xpath("//*[contains(@title, 'First Name')]")
			fname_box.send_keys(FNAMES[i])
			time.sleep(.5)
			lname_box = driver.find_element_by_xpath("//*[contains(@title, 'Last Name')]")
			lname_box.send_keys(LNAMES[i])
			time.sleep(.5)
			email_box = driver.find_element_by_xpath("//*[contains(@name, 'email') and contains(@id, 'email')]")
			email_box.send_keys(EMAILS[i])
			time.sleep(.5)
			gname_box = driver.find_element_by_xpath("//*[contains(@name, 'nick') and contains(@id, 'nick')]")
			gname_box.send_keys(GROUP)
			time.sleep(.5)
			select = Select(driver.find_element_by_xpath("//*[contains(@name, 'q1') and contains(@id, 'q1') and contains(@class, 'form-control')]"))
			
			select.select_by_visible_text("Undergraduate student")
			# could be changed for whattever - though this should match the credentials of the email accounts
			
			time.sleep(.5)
			select = Select(driver.find_element_by_xpath("//*[contains(@name, 'q2') and contains(@id, 'q2') and contains(@class, 'form-control')]"))
			
			select.select_by_visible_text("Group work (class)")
			# could be changed for whattever
			
			time.sleep(.5)
			sub_box = driver.find_element_by_xpath("//*[contains(@onclick, 'return do_booking();')]")
			sub_box.click()
			
			
			print("success on " + FNAMES[i])
			
		except:
			
			print("failure on " + FNAMES[i])

	def attempt_room_confirm(x=0, all=False):
		
			driver = webdriver.Chrome(executable_path=driver_path)
			
			imap_ssl_host = 'imap.gmail.com'
			imap_ssl_port = 993
			username = linked_email
			password = linked_email_app_pass
			server = imaplib.IMAP4_SSL(imap_ssl_host, imap_ssl_port)

			server.login(username, password)
			server.select('Library')
			email_date = (datetime.date.today() - datetime.timedelta(1)).strftime("%d-%b-%Y")
			if all:
				status, data = server.search(None, 'ALL')
			else:
				status, data = server.search(None, "(ON {0})".format(email_date))
			
			
			
			for num in data[0].split():
					
					try:
						status, data = server.fetch(num, '(RFC822)')
						email_msg = data[0][1]

						steamail = str(email_msg)
						link = steamail[steamail.find("2 hours, by visiting: "):]

						link = link[22:]
						link = link[:link.find(" ")]
						link = link[:link.find("\\")]
						

						driver.get(str(link)) 

						time.sleep(3)
						time.sleep(x)
						yes_box = driver.find_element_by_xpath("//*[contains(@id, 'rm_confirm_link')]")
						yes_box.click()
				
						print("checking email " + str(int(num)))
					except:
						print("something went wrong with email " + str(int(num)))


	threads = []
	with concurrent.futures.ThreadPoolExecutor() as executor:
		for i in range(0, len(times_sets)):
			
			t = executor.submit(attempt_room_reserve, i)
			a = executor.submit(attempt_room_confirm)
			
			threads.append(t)
			threads.append(a)
			
		for t in concurrent.futures.as_completed(threads):
			print("",end='')
		attempt_room_confirm(x=0,all=True)
		attempt_room_confirm(x=3)
		attempt_room_confirm(x=5)
		attempt_room_confirm(x=1,all=True)
		
				
	finish_time = time.perf_counter()
	print("finsished_running in " + str(finish_time-start_time))

		


