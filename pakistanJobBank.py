from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
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


class jobz:
    def __init__(self):
        # self.helper = Helper()
        self._main_url = "http://www.pakistanjobsbank.com"
        self._all_jobs_url = "http://www.pakistanjobsbank.com/"
        self.platform = "App\CompanyIndeed"
        self.output = pd.DataFrame()
        self.chromedriver_path = os.environ.get("CHROME_DRIVER")
        self.prefix = ['ltd', 'plc', 'pvt', 'private', 'ceylon']
        self.XPRESS_JOBS_SCRAPER = os.environ.get("XPRESS_JOBS_SCRAPER")
        self.S3_BUCKET_URL = os.environ.get("S3_BUCKET_URL")
        self.list_remove_words = ['Please click the APPLY button to upload your CV via XpressJobs', 'XpressJobs',
                                  'XpressJobs', 'xpress jobs', 'xpress job', 'express jobs', 'express jobs']
        self.current_page = None
        self.Job_Id_list = []
        self.Company_Name_list = []
        self.Company_Logo_list = []
        self.Job_Title_list = []
        self.Job_Location_list = []
        self.City_location_list = []
        self.City_list = []
        self.Job_Posted_list = []
        self.Job_Expire_list = []
        self.Job_Type_list = []
        self.Job_education_list = []
        self.Job_Experence_list= []
        self.Job_Categories_list = []
        self.Job_Description_list = []
        self.html_job_description_list = []
        self.Job_Overview_list = []
        self.Job_poster_list = []
        self.Salary_des_list = []
        self.Links_list =[]





        # self.db_model = BaseDBModel()

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
        # job_ad_url = link
        # Job_ID = link.split("/")[5]
        Job_Id = ''
        Company_Name = ''
        Company_Logo = ''
        Job_Title = ''
        Job_Location = ''
        City_location = ''
        City = ''
        Job_Posted = ''
        Job_Expire = ''
        Job_Type = ''
        Job_education = ''
        Job_Experence = ''
        Job_Categories = ''
        Job_Description = ''
        html_job_description = ''
        Job_Overview = ''
        Job_poster = ''
        Salary_des = ''
        s3_url_company_logo = ''
        s3_url_job_poster = ''
        company_email = ''

        try:
            Job_Id = re.search(r"(?<=_jobs-).*?(?=.html)", link).group(0)
            print("unique_ID*************"+Job_Id)
        except:
            Job_Id = None

        try:
            City = re.search(r"(?<=_in_).*?(?=/)", c_link).group(0)
            print("city*************" + City)
        except:
            City = None


        try:
            details = soup.find('script', attrs={'type': 'application/ld+json'})
            detail_json = json.loads(details.text)

            # Job_Id = detail_json["identifier"]["value"]
            Company_Name = detail_json["hiringOrganization"]["name"]
            Company_Logo = detail_json["hiringOrganization"]["logo"]
            Job_Title = detail_json["title"]
            Job_Location = detail_json["jobLocation"]["address"]["streetAddress"]
            Job_Posted = detail_json["datePosted"]
            format_closing_date = '%d %B, %Y'
            datetime_obj = datetime.datetime.strptime(Job_Posted, format_closing_date)
            Job_Posted = datetime_obj.date()
            Job_Expire = detail_json["validThrough"]
            format_closing_date = '%d %B, %Y'
            datetime_obj = datetime.datetime.strptime(Job_Expire, format_closing_date)
            Job_Expire = datetime_obj.date()
            # Job_Type = detail_json["employmentType"]
            Job_education = detail_json["educationRequirements"]
            Job_Experence = detail_json["experienceRequirements"]
            Job_Categories = detail_json["occupationalCategory"]
            Job_Description = detail_json["description"]
            print("Details_from============>JSON")

            set = soup.find('div', attrs={'class': "job_detail"})
            # set1 = set.findAll('div', attrs={'class': "job_detail_cell2"})
            set1 = set.find_all('div', attrs={'class': "row_job_detail"})
            _dict_job_details = {}
            for set_obj in set1:
                cell1_div = set_obj.find('div', attrs={'class': "job_detail_cell1"})
                cel1_text = (cell1_div.text).strip()

                cell2_div = set_obj.find('div', attrs={'class': "job_detail_cell2"})
                cel2_text = (cell2_div.text).strip()
                _dict_job_details[cel1_text] = cel2_text

            # try:
            #     City_location = _dict_job_details["Vacancy Location:"]
            # except:
            #     City_location = None
            try:
                Job_Type = _dict_job_details["Job Type:"]
            except:
                Job_Type = None


        #next __fetching__method==================================================================================================================
        except:
            set = soup.find('div', attrs={'class': "job_detail"})
            # set1 = set.findAll('div', attrs={'class': "job_detail_cell2"})
            set1 = set.find_all('div', attrs={'class': "row_job_detail"})
            _dict_job_details = {}
            for set_obj in set1:
                cell1_div = set_obj.find('div', attrs={'class': "job_detail_cell1"})
                cel1_text = (cell1_div.text).strip()

                cell2_div = set_obj.find('div', attrs={'class': "job_detail_cell2"})
                cel2_text = (cell2_div.text).strip()
                _dict_job_details[cel1_text] = cel2_text
            print("Page_details**********************")
            print(_dict_job_details)


            try:
                Job_Posted = _dict_job_details["Date Posted:"]
                format_closing_date = '%d %B, %Y'
                datetime_obj = datetime.datetime.strptime(Job_Posted, format_closing_date)
                Job_Posted = datetime_obj.date()
            except:
                Job_Posted = None
            # try:
            #     Job_Categories = _dict_job_details["Category / Sector:"]
            # except:
            #     Job_Categories = None
            try:
                Job_education = _dict_job_details["Education:"]
            except:
                Job_education = None
            try:
                Company_Name = _dict_job_details["Organization:"]
            except:
                Company_Name = None
            try:
                Job_Location = _dict_job_details["Vacancy Location:"]
            except:
                Job_Location = None
            try:
                Job_Categories = _dict_job_details["Job Industry:"]
                Job_Categories = Job_Categories.replace(' Jobs', '')
                print(Job_Categories)
            except:
                Job_Categories = None
            try:
                Job_Type = _dict_job_details["Job Type:"]
            except:
                Job_Type = None
            try:
                Job_Experence = _dict_job_details["Job Experience:"]
            except:
                Job_Experence = None
            try:
                Job_Expire = _dict_job_details["Last Date:"]
                format_closing_date = '%d %B, %Y'
                datetime_obj = datetime.datetime.strptime(Job_Expire, format_closing_date)
                Job_Expire = datetime_obj.date()
            except:
                Job_Expire = None

            print(Job_Id)
            print(Job_Categories)
            print(Job_Location)
            print(Company_Name)
            print(Job_education)




        try:
            if soup.find('h1', attrs={'id': 'head1'}):
                Job_Title = soup.find('h1', attrs={'id': 'head1'}).text
                Job_Title = self.clean_soup(Job_Title)
                print(Job_Title)
        except:
            Job_Title = None
        try:
            if soup.find('div', attrs={'id': 'ad-desc-cont'}):
                html_job_description = soup.find('div', attrs={'id': 'ad-desc-cont'}).text
                html_job_description = self.clean_soup(html_job_description)
                print(html_job_description)
        except:
            html_job_description = None

        try:
            image_url = soup.find('div', attrs={'id': 'ad-pic-cont'})
            image_url1 = image_url.find('img', attrs={'src': re.compile('^https')})
            # image_url = self.clean_soup(image_url)
            Job_poster = image_url1['src']
            print(Job_poster)
        except:
            Job_poster = None

        #csv_columns
        self.Job_Id_list.append(Job_Id)
        self.Company_Name_list.append(Company_Name)
        self.Company_Logo_list.append(Company_Logo)
        self.Job_Title_list.append(Job_Title)
        self.Job_Location_list.append(Job_Location)
        self.City_location_list.append(City_location)
        self.City_list.append(City)
        self.Job_Posted_list.append(Job_Posted)
        self.Job_Expire_list.append(Job_Expire)
        self.Job_Type_list.append(Job_Type)
        self.Job_education_list.append(Job_education)
        self.Job_Experence_list.append(Job_Experence)
        self.Job_Categories_list.append(Job_Categories)
        self.Job_Description_list.append(Job_Description)
        self.html_job_description_list.append(html_job_description)
        self.Job_Overview_list.append(Job_Overview)
        self.Job_poster_list.append(Job_poster)
        self.Salary_des_list.append(Salary_des)
        self.Links_list.append(link)


        # print("Job is available...")
        # # UPDATE CURRENT DATA
        # table_name = 'jobs'
        # update_columns = "description= '%s'" % Job_Description
        # search_key = 'id'
        # update_ids = [check_job_available["id"]]
        # self.db_model.update_multiple_records(table_name, update_columns, search_key, update_ids)
        # print("Job ID %s is updated..." % check_job_available["id"])

    def make_output(self):
        post_data = {
            'platform': self.platform,
            'unique_key': self.Job_Id_list,
            'job_title': self.Job_Title_list,
            'company_name': self.Company_Name_list,
            'company_logo': self.Company_Logo_list,
            # 'company_email': '',
            # 'job_salary': Salary_des,
            'job_type': self.Job_Type_list,
            'location': self.Job_Location_list,
            # 'city_location': self.City_location_list,
            'city': self.City_list,
            'job_link': self.Links_list,
            'Job_poster': self.Job_poster_list,
            'start_at': self.Job_Posted_list,
            'closing_date': self.Job_Expire_list,
            # 'job_description': self.Job_Description_list,
            'educational_requirements': self.Job_education_list,
            'job_Experence': self.Job_Experence_list,
            'job_description': self.html_job_description_list,
            'category': self.Job_Categories_list,
            # 's3_url_company_logo': s3_url_company_logo,
            # 's3_url_job_poster': s3_url_job_poster

        }
        df = pd.DataFrame(post_data)
        df.to_csv("Testjobzpk_final_final.csv")


    def get_all_jobs_urls(self, url):
        print(url)
        links = []
        try:
            content = requests.get(url, timeout=30)
            soup = BeautifulSoup(content.text, features="lxml")
            # print(soup.prettify())
        except:
            print("Domain Not Availabe")
            pass
        try:
            job_cities = soup.find('nav', attrs={'id': "footer-nav"})
            # print(job_cities)
            job_cities1 = job_cities.find('div', attrs={'class': "category"})
            # print(job_cities1)
            job_cities2 = job_cities1.findAll('ul', attrs={'class': "mobile-hidden"})
            # print(job_cities2)
            # for job_cities2 in job_cities2:
            #     print(job_cities2)
        except:
            pass
        # sys.exit()
        for job_cities2 in job_cities2:
            for job_city in job_cities2:
                try:
                    one = job_city.find('a', attrs={'href': re.compile('^/Loc/')})
                    one = (one['href'])
                    one = self._main_url +one
                    links.append(one)
                    print(one)

                except:
                    pass
        print(links)
        self.read_city_main_urls(links)


    def read_city_main_urls(self, city_list):
        post_urls = []
        for c_link in city_list:
            print("pakistan_Job_Bank == ==> " + c_link)
            next_page_url = c_link
            next_page = True
            count = 1
            self.current_page = c_link
            while next_page:
                print("--------------------", self.current_page)
                sleep = random.randint(2, 5)
                time.sleep(sleep)
                try:
                    content1 = requests.get(self.current_page, timeout=30)
                    soup = BeautifulSoup(content1.text, features="lxml")
                    # print(soup.prettify())
                except:
                    print("Page_not_working")
                    print(self.current_page)
                    pass
                try:
                    post = soup.find('div', attrs={'class': "job-ads-list-container clearfix"})
                    post1 = post.findAll('tr', attrs={'class': "job-ad"})
                    # post1 = post1.findAll('tr')
                    print(post1)
                    # post1 = post.findAll('div', attrs={'itemprop': "itemListElement"})
                except:
                    pass
                sys.exit()
                for post_url in post1:
                    try:
                        one = post_url.find('tr', attrs={'class': "job-ad"})
                        print(one)
                        # two = one.find('a', attrs={'href': re.compile(('^https'))})
                        # two = two['href']
                        # post_urls.append(two)
                    except:
                        pass

            #         print(two)
            #     self.current_page = next_page_url+str(count)
            #     count += 1
            #     if count >= 3:
            #         break
            # # self.Post_request(post_urls, c_link)


    def Post_request(self,post_urls, c_link):
        print("next===> Post_request")
        for link in post_urls:
            print("========scrap_link=============="+link)
            try:
                content = requests.get(link, timeout=30)
                soup = BeautifulSoup(content.text, features="lxml")
                sleep = random.randint(1, 3)
                time.sleep(sleep)
            except:
                pass
            self.create_final_output(soup, link, c_link)
            self.make_output()


    def input_url_download(self):
        url = self._all_jobs_url
        self.get_all_jobs_urls(url)
        print("one")

if __name__ == '__main__':
    scraper = jobz()
    scraper.input_url_download()


