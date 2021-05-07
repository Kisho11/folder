from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import traceback
import pandas as pd
import re
import bs4
import requests
import time
import random
import datetime
# from app import get_base_path
# from helpers.Helper import Helper
# from helpers.BaseDBModel import BaseDBModel
import sys
import json

isNavigable = lambda s: isinstance(s, bs4.NavigableString)
load_dotenv()


class hubstuff:
    def __init__(self):
        # self.helper = Helper()
        self.driver = None
        self.wait = None
        self.page_link = None
        self.page_count = 1
        self.post_count = 1
        self.link_count = 1
        self.source_id = '11'
        self.country = 'remote'
        self._main_url= "https://talent.hubstaff.com"
        self.job_cat_url = "https://talent.hubstaff.com/search/jobs?search%5Bkeywords%5D=&page=1&search%5Btype%5D=&search%5Blast_slider%5D=&search%5Bnewer_than%5D=&search%5Bnewer_than%5D=&search%5Bpayrate_start%5D=1&search%5Bpayrate_end%5D=100&search%5Bpayrate_null%5D=0&search%5Bpayrate_null%5D=1&search%5Bbudget_start%5D=1&search%5Bbudget_end%5D=100000&search%5Bbudget_null%5D=0&search%5Bbudget_null%5D=1&search%5Bexperience_level%5D=-1&search%5Bcountries%5D%5B%5D=&search%5Blanguages%5D%5B%5D="
        self._all_com_url = "https://talent.hubstaff.com"
        self.platform = "https://talent.hubstaff.com"
        self.output = pd.DataFrame()
        self.chromedriver_path = os.environ.get("CHROME_DRIVER")
        self.S3_BUCKET_URL = os.environ.get("S3_BUCKET_URL")
        # self.current_page = None


        # self.db_model = BaseDBModel()
    def driver_load(self):
        options = webdriver.ChromeOptions()
        options.headless = True
        # options.add_argument("--headless")
        self.driver = webdriver.Chrome(executable_path="/home/ilabs/Desktop/AMD/chromedriver_linux64/chromedriver",
                                       keep_alive=True, options=options)
        # options = options
        self.wait = WebDriverWait(self.driver, 20, poll_frequency=1)
        return True


    def clean_soup(self, soup):
        # Convert HTML into text
        re_display_none = re.compile(r"display\s*:\s*none")

        def _clean(s):
            if isNavigable(s) or isinstance(s, str):
                pass
            elif re_display_none.search(s.get('style') or ''):
                # Invisible stuff is removed.
                return ''
            elif s.find(style=re_display_none):
                s = " ".join(filter(None, map(_clean, s.contents)))
            elif s.name in ["br", "hr"]:
                # Breaks turn into spaces.
                return u' '
            else:
                s = u"".join(map(_clean, s.contents))
            '''if isinstance(s, str):
            s = s.decode('utf8')'''
            return re.sub(r"[\s\xa0]+", " ", s)

        # We should only strip at the top level.
        return _clean(soup).strip()

    def create_final_output(self, soup, link):
        # print(soup)
        # job_ad_url = link
        # Job_ID = link.split("/")[5]
        Job_Id = ''
        Job_Title = ''
        Job_Type = ''
        Company_Name = ''
        Company_Carrer_Page = ''
        Job_Location = ''
        Remote_type = ''
        Job_Posted_detail = ''
        Job_Posted = ''
        Job_Description = ''
        Job_Skills = ''
        Availability = ''
        Experence = ''
        Language = ''

        s3_url_company_logo = ''
        s3_url_job_poster = ''
        company_email = ''


        Job_Id_list = []
        Job_Title_list = []
        Job_Type_list = []
        Company_Name_list = []
        Company_Carrer_Page_list = []
        Job_Location_list = []
        Remote_type_list = []
        Job_Posted_detail_list = []
        Job_Posted_list = []
        Job_Description_list = []
        Job_Skills_list = []
        Availability_list = []
        Experence_list = []
        Language_list = []

        Links_list = []


        print("JOB_POST_COUNT========>>>>>>>>>------",self.post_count)
        self.post_count += 1

        # for Job in soup.find_all('script', attrs={"type": re.compile("text/javascript")}):
        #     # print(Job)
        for Job_ID1 in soup.find_all('script', attrs={"src": re.compile("//dev.visualwebsiteoptimizer.com/")}):
            Job_ID2 = Job_ID1["src"]
            Job_Id = re.search(r"(?<=r=0.)\w+", Job_ID2).group(0)
            print("----------UNIQUE_ID----------------", Job_Id)
        # Job_ID = Job_ID1["src"]



        #=====source_from_page_elements=========
        set = soup.find('div', attrs={'class': "container job-page"})
        # print(set)
        print("============================================")

        #========================================================================================
        try:
            Job_Title1 = set.find('h1', attrs={'class': 'h3 name no-margin'})
            Job_Title2 = Job_Title1.find('span', attrs={'class': re.compile("valign-middle margin-right")})
            Job_Title = self.clean_soup(Job_Title2)
            print(Job_Title)
        except:
            Job_Title = None
        #========================================================================================
        try:
            Job_Type1 = set.find('h1', attrs={'class': 'h3 name no-margin'})
            Job_Type2 = Job_Type1.find('span', attrs={'class': re.compile("label")})
            Job_Type = self.clean_soup(Job_Type2)
            print(Job_Type)
        except:
            Job_Type = None
        #==============================================================================
        try:
            Company_Name1 = set.find('div', attrs={'class': re.compile('job-company push-bottom')})
            Company_Name2 = Company_Name1.find('a', attrs={'class': re.compile("job-agency margin-right")})
            try:
                Company_Carrer_Page = Company_Name2["href"]
            except:
                Company_Carrer_Page = None
            try:
                Company_Name = self.clean_soup(Company_Name2)
                print(Company_Carrer_Page)
                print(Company_Name)
            except:
                Company_Name = None
        except:
            Company_Name1 = None
        #========================================================================================
        try:
            Job_Location1 = set.find('div', attrs={'class': re.compile('job-company push-bottom')})
            Job_Location2 = Job_Location1.find('span', attrs={'class': re.compile('location text-success margin-right')})
            Job_Location = self.clean_soup(Job_Location2)
            print(Job_Location)
        except:
            Job_Location = None
        #========================================================================================
        try:
            Remote_type1 = set.find('div', attrs={'class': re.compile('job-company push-bottom')})
            Remote_type2 = Remote_type1.find('span', attrs={'class': re.compile('text-purple margin-right')})
            Remote_type = self.clean_soup(Remote_type2)
            print(Remote_type)
        except:
            Remote_type = None
        print("Date_Change************************************************************************************")
        #========================================================================================
        try:
            Job_Posted_detail1 = set.find('div', attrs={'class': re.compile('job-company push-bottom')})
            Job_Posted_detail2 = Job_Posted_detail1.find('span', attrs={'class': re.compile('text-light-grey nowrap')})
            Job_Posted_detail3 = Job_Posted_detail2.find('span', attrs={'class': re.compile(('a-tooltip'))})
            Job_Posted_detail = Job_Posted_detail3["data-original-title"]
            Job_Posted_detail0 = re.search(r"(?<=at)\w+", Job_Posted_detail).group(0)
            print(Job_Posted_detail0)
            format_closing_date = '%B %d, %Y'
            datetime_obj = datetime.datetime.strptime(Job_Posted_detail, format_closing_date)
            Job_Posted_detail = datetime_obj.date()
            print(Job_Posted_detail)
        except:
            Job_Posted_detail = None
        #========================================================================================
        try:
            Job_Posted1 = set.find('div', attrs={'class': re.compile('job-company push-bottom')})
            Job_Posted2 = Job_Posted1.find('span', attrs={'class': re.compile('text-light-grey nowrap')})
            Job_Posted = self.clean_soup(Job_Posted2)
            print(Job_Posted)
        except:
            Job_Posted = None
        #========================================================================================
        try:
            Job_Description = set.find('div', attrs={'class': re.compile('job-description push-bottom')})
            # Job_Description = self.clean_soup(Job_Description1)
            print(Job_Description)
            is_html_description = '1'
        except:
            Job_Description = None
            is_html_description = '0'
        #========================================================================================
        Job_Skills0 = ''
        try:
            Job_Skills1 = set.find('div', attrs={'id': re.compile('skills')})
            for Job_Skills2 in Job_Skills1.find('ul', attrs={'class': re.compile('list-inline')}):
                Job_Skills = self.clean_soup(Job_Skills2)
                Job_Skills0 += Job_Skills+"\n"
                # print(Job_Skills)
            print(Job_Skills0)
        except:
            Job_Skills = None
        #========================================================================================
        Requirment_dict = {}
        try:
            for Requirments1 in set.find('div', attrs={'class': re.compile('profile-header-info no-padding ')}):
                Key11 = Requirments1.find('dt')
                Key1 = self.clean_soup(Key11)

                Key22 = Requirments1.find(('dd'))
                Key2 = self.clean_soup(Key22)
                Requirment_dict[Key1] = Key2
            print(Requirment_dict)
        except:
            Requirments = None
        try:
            Availability = Requirment_dict["Availability:"]
            print(Availability)
        except:
            Availability = None
        try:
            Experence = Requirment_dict["Experience levels:"]
            print(Experence)
        except:
            Experence = None
        try:
            Language = Requirment_dict["Languages:"]
            print(Language)
        except:
            Language = None
        #========================================================================================



        #<<<<<<<<<<<<<csv_columns>>>>>>>>>>>>>>>>>>
        Job_Id_list.append(Job_Id)
        Job_Title_list.append(Job_Title)
        Job_Type_list.append(Job_Type)
        Company_Name_list.append(Company_Name)
        Company_Carrer_Page_list.append(Company_Carrer_Page)
        Job_Location_list.append(Job_Location)
        Remote_type_list.append(Remote_type)
        Job_Posted_detail_list.append(Job_Posted_detail)
        Job_Posted_list.append(Job_Posted)
        Job_Description_list.append(Job_Description)
        Job_Skills_list.append(Job_Skills0)
        Availability_list.append(Availability)
        Experence_list.append(Experence)
        Language_list.append(Language)

        Links_list.append(link)


    # def make_output(self):
        post_data = {
            'platform': self.platform,
            'unique_id': Job_Id_list,
            'source_id': self.source_id,
            'country': self.country,
            'job_title': Job_Title_list,
            'job_type': Job_Type_list,
            'company_name': Company_Name_list,
            'career_page_url': Company_Carrer_Page_list,
            'company_address': Job_Location,
            'work_location_type': Remote_type_list,
            'job_start_date': Job_Posted_detail_list,
            'extra_start_details': Job_Posted_list,
            'job_raw_description': Job_Description_list,
            'is_html_description': is_html_description,
            'extra_job_requirement_details': Job_Skills,
            'extra_job_details': Availability_list,
            'working_experience': Experence_list,
            'extra_job_description_details': Language_list,
            'job_link': Links_list

            # 'job_description': self.html_job_description_list,
            # 's3_url_company_logo': s3_url_company_logo,
            # 's3_url_job_poster': s3_url_job_poster

        }
        df = pd.DataFrame(post_data)
        if os.path.isfile('hubstuff.csv'):
            df.to_csv("hubstuff.csv", mode='a', header=False)
        else:
            df.to_csv("hubstuff.csv")


        print("<<<<<<<<<<<<<<<<<<<Updated>>>>>>>>>>>>>>>>>>>>>>")



    def get_job_post_url(self, Job_cat0):
        print(">>>>>>>>>>>>>>>>>>>>>>REQUESTING<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        self.driver_load()
        post_urls = []
        for cat in Job_cat0:
            print("TELENT.HUBSTUFF  ==> " + cat)
            self.driver.get(cat)
            sleep = random.randint(5, 7)
            time.sleep(sleep)
            print("REQUEST DONE")
            # content1 = requests.get(cat)
            # soup = BeautifulSoup(content1.text, features="lxml")
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            # print(soup.prettify())
            # ------------------------------------------------------------
            self.create_final_output(soup, cat)





    def get_job_cat(self):
        url = self.job_cat_url
        print("INITIATED==> ", url)
        self.driver_load()


        while self.page_count < 150:
            try:
                page_link = url
                self.driver.get(page_link)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                # content = requests.get(url, timeout=60)
                # soup = BeautifulSoup(content.text, features="lxml")
                # print(soup.prettify())
                print("******PAGE_COUNT***||||>>>>>",self.page_count,"<<<<<||||")

                print("||||||||||||SCRAPED|||||||||||||||||")
            except:
                print("Domain Not Availabe")
                pass
            Job_cat0 = []
            try:
                job_cat11 = soup.find('div', attrs={'class': "page-wrapper"})
                job_cat1 = job_cat11.find('div', attrs={'class': "container"})
                for job_cat2 in job_cat1.find_all('form', attrs={'id': 'filter_search'}):
                    job_cat4 = job_cat2.find('div', attrs={'class': "col-sm-8 col-md-9 bg-body"})
                    job_cat5 = job_cat4.find('div', attrs={'class': "job-results"})
                    for job_cat6 in job_cat5.find_all('div', attrs={'class': 'content-section'}):
                        for job_cat7 in job_cat6.find_all('div', attrs={'class': 'search-result'}):
                            job_cat8 = job_cat7.find('div', attrs={'class': 'main-details'})
                            job_cat9 = job_cat8.find('a')['href']
                            job_cat10 = self._main_url+job_cat9
                            print(job_cat10)
                            Job_cat0.append(job_cat10)
                # print(Job_cat0)
            except:
                pass
            print(Job_cat0)
            #=====================================================================================================
            self.get_job_post_url(Job_cat0)
            #=====================================================================================================

            #=====================pagination===============
            try:
                print("---------Pagination-------->>>>>")
                Page1 = soup.find('div', attrs={'class': 'page-wrapper'})
                Page2 = Page1.find('div', attrs={'class': 'container'})
                Page3 = Page2.find('div', attrs={'class': 'pagination-container'})
                Page4 = Page3.find('a', attrs={'rel': 'next'})
                Page5 = Page4['href']
                Page6 = self._main_url+Page5
                print(Page6)
                sleep = random.randint(3, 5)
                time.sleep(sleep)
                url = Page6
                self.driver.close()
                self.page_count += 1
            except:
                pass


    def test(self):
        self.driver_load()
        link = 'https://talent.hubstaff.com/jobs/google-sheet-specialist-6'
        self.driver.get(link)
        # content = requests.get(link, timeout=30)
        # soup = BeautifulSoup(content.text, features="lxml")
        soup = BeautifulSoup(self.driver.page_source, features="lxml")
        print(soup.prettify())



if __name__ == '__main__':
    scraper = hubstuff()
    # scraper.get_all_company_links()
    scraper.get_job_cat()
    # scraper.read_city_main_urls()
    # scraper.test()
    # scraper.Post_request()


