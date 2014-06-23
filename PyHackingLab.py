#!/usr/bin/python
# -*- coding: utf-8 -*-

""" PyHLSolutionsDownloader.py:
    Class to download your hacking-lab.com solutions. 
"""

__author__ = "tunelko"
__version__ = 'PyHLSolutionsDownlaoder v1.0'

import sys, logging, os
import mechanize, re
import cookielib
import getpass
from BeautifulSoup import BeautifulSoup
from datetime import datetime

class HackingLabSolutions(object):

    def __init__(self):
        self.current_time = lambda: str(datetime.now()).split(' ')[1].split('.')[0]
        self.browser = mechanize.Browser()
        self.browser.set_handle_robots(False)
        self.cookies = mechanize.CookieJar()
        self.solutions_tmpfile = 'tmp.txt'
        self.login_url = 'https://www.hacking-lab.com/user/login/' # login 
        self.solved_url = "https://www.hacking-lab.com/user/administration/mySolutionPage.html" # browsing solutions 
        self.HL_url = 'https://www.hacking-lab.com'        
        # login data 
        self.username = raw_input("Enter your username: ") 
        # some email address validation
        if not re.search('([\w.-]+)@([\w.-]+)', self.username): 
            print '[!] You must provide a valid email address'
            exit(0)
        self.password = getpass.getpass("Enter your password: ")

    def login(self):
        self.browser.open(self.login_url)
        self.browser.select_form(name="loginForm")
        self.browser["userEmail"] = self.username
        self.browser["userPassword"] = self.password
        res = self.browser.submit()
        data = self.browser.response().read()
        if re.search('Don\'t have an account?', data):
            print '[!]', obj.current_time() ,' - Invalid login credentials' 
            exit(0)


    def find_solutions(self):
        cookies = cookielib.LWPCookieJar()
        opener = mechanize.build_opener(mechanize.HTTPCookieProcessor(cookies))
        r = opener.open(self.solved_url) 
        mechanize.install_opener(opener)
        br = mechanize.Browser()
        br.set_cookiejar(cookies)
        self.browser.open(self.solved_url)
               
        # write temp file with url solutions 
        with open(self.solutions_tmpfile,'w') as f:            
            for link in self.browser.links():
                # print link.text
                links = link.url + '\n'
                linksolutions = re.sub('/user/cases/sendsolution',self.HL_url + '/user/cases/showsolution',links)
                if re.search('https',linksolutions):
                    f.write(linksolutions)
                    f.close

    
    def save_solutions(self):
        index=[]
        with open(self.solutions_tmpfile) as f:
             for line in f:
                 line = re.sub('\n', '', line)
                 self.browser.open(line)
                 # body of the response    
                 data = self.browser.response().read()
                 # replace local css paths 
                 data = re.sub('/misc/css/style_global.css','../assets/css/bootstrap.css',data) 
                 # replace to allow download attachements from website. 
                 data = re.sub('filedownload.html',self.HL_url + 'filedownload.html',data)                  

                 if re.search('^https://www.',line): 
                    # prepare file name of each solution = name of the task
                    filename = self.get_taskname(data)
                    dirname = re.sub('.html','',filename)
                    self.make_dir(dirname)
                    index.append(filename)
                    # write solutions file 
                    with open(dirname +'/' + filename,'w') as tmp:
                         print '[+]' , obj.current_time() , ' Downloading solution as ' + filename
                         tmp.write(data) 
                         tmp.close 
                         
                    # Download attachments 
                    attachments_data=self.get_attachments(data)
                    for attach in attachments_data:
                        (tmp_filename, headers) = self.browser.retrieve(attach) 
                        downloaded_filename = re.findall("filename=(\S+)", str(headers))
                        self.browser.retrieve(attach,re.sub('"','',dirname+'/'+downloaded_filename[0]))
                        print '[@]' , obj.current_time() , ' Downloading attached file ' + downloaded_filename[0]
    
    def get_taskname(self,data):
        # need find the case name 
        soup = BeautifulSoup(data)
        table = soup.find('table',{'class':'content'})
        td = soup.find('td', text='Case:')
        # search inside solution's page to get the case title for friendly filename. 
        title = td.findNext('td')
        title = re.sub('<td>' ,'', str(title))
        title = re.sub('</td>', '', str(title))
        title = re.sub('"', '', str(title))
        title = re.sub('/', ' ', str(title))

        # print data from solution and assign a valid filename case. 
        filename = title.lstrip(' ') +'.html'
        return filename

    def get_attachments(self,data):
        links=[]
        # attachments  
        soup = BeautifulSoup(data)
        search_links = soup.findAll('div',{'id':'upDiv'})
        for div in search_links:
            hrefs = div.findAll('a')
            for a in hrefs:
                links.append(re.sub('filedownload','/user/cases/filedownload',a['href']))
        return links

    def make_dir(self,dirname):
        try:
            os.makedirs(dirname)
        except OSError:
            if os.path.exists(dirname):
                pass
            else:
                raise

    def logger(self):
        logger = logging.getLogger("mechanize")
        logger.addHandler(logging.FileHandler('log.txt','a','utf-8'))
        logger.setLevel(logging.DEBUG)


# Init object and start. 
obj = HackingLabSolutions()
print '[+]' , obj.current_time() , ' - Login as: ', obj.username
obj.login() 
print '[+]', obj.current_time() , ' - Writing solution urls in', obj.solutions_tmpfile
obj.find_solutions()
obj.save_solutions()
