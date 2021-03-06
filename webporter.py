#!/usr/bin/env python
# encoding: utf-8

import web
import urllib2
import cookielib
import urlparse
import sqlite3
urls = ("/.*","proxy")
app = web.application(urls, globals())
class Crawler:
    def __init__(self):
        self.cookie = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        user_agent ='Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0'
        self.http_header =  {'User-Agent':user_agent}

    def get_page_html(self, target_url):
        try:
            req = urllib2.Request(target_url, headers = self.http_header)
            return self.opener.open(req).read()
        except urllib2.HTTPError, err:
            print "==================\n",err
            print "==================\n",target_url
            print "==================\n"
            return ""

class proxy:
    crawler = Crawler()
    proxy_target_url = "http://www.zillow.com"
    def __init__(self):
        print "started"
        self.create_db_table()

    def GET(self):
        target_url = urlparse.urljoin(self.proxy_target_url, web.ctx['path'])
        target_url = urlparse.urljoin(target_url, web.ctx['query'])
        new_page = self.get_from_db(target_url)
        if(new_page == None):
            page = self.crawler.get_page_html(target_url)
            new_page = page.replace(self.proxy_target_url, "")
            self.save_to_db(target_url, new_page)
        return new_page

    def save_to_db(self, target_url, page):
        conn = sqlite3.connect('zillow.db')
        conn.text_factory = str
        conn.execute("INSERT INTO zillow VALUES (?,?) ", (target_url, page))
        conn.commit()
        conn.close()

    def get_from_db(self, target_url):
        conn = sqlite3.connect('zillow.db')
        conn.text_factory = str
        cursor = conn.execute("SELECT content FROM zillow WHERE url=?", (target_url,))
        content = cursor.fetchone()
        if content != None:
            content = content[0]
        conn.close()
        return content

    def create_db_table(self):
        conn = sqlite3.connect('zillow.db')
        conn.execute('''CREATE TABLE IF NOT EXISTS zillow
                    (url TEXT PRIMARY KEY NOT NULL,
                    content TEXT NOT NULL );''')
        conn.commit()
        conn.close()



if __name__ == "__main__":
    app.run()
