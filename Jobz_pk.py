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
        self._main_url = "https://www.jobz.pk/"
        self._all_jobs_url = "https://www.jobz.pk/"
        self.platform = "App\CompanyIndeed"
        self.output = pd.DataFrame()
        self.post_count = 1
        self.chromedriver_path = os.environ.get("CHROME_DRIVER")
        self.prefix = ['ltd', 'plc', 'pvt', 'private', 'ceylon']
        self.XPRESS_JOBS_SCRAPER = os.environ.get("XPRESS_JOBS_SCRAPER")
        self.S3_BUCKET_URL = os.environ.get("S3_BUCKET_URL")
        self.list_remove_words = ['Please click the APPLY button to upload your CV via XpressJobs', 'XpressJobs',
                                  'XpressJobs', 'xpress jobs', 'xpress job', 'express jobs', 'express jobs']
        self.current_page = None

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

    def create_final_output(self, soup, link, c_link):
        # job_ad_url = link
        # Job_ID = link.split("/")[5]
        Job_Id = ''
        Job_Title = ''
        Company_Name = ''
        Company_Logo = ''
        Company_address = ''
        Job_Location = ''
        Company_State = ''
        Postel_code = ''
        City = ''
        Job_Posted = ''
        Job_Expire = ''
        Job_Categories = ''
        Job_Type = ''
        Job_education = ''
        Job_Experence = ''
        Salary_des = ''
        Currency = ''
        Job_Description = ''
        is_html_description = ''
        Job_poster = ''
        s3_url_company_logo = ''
        s3_url_job_poster = ''

        Job_Id_list = []
        Job_Title_list = []
        Company_Name_list = []
        Company_Logo_list = []
        Company_address_list = []
        Job_Location_list = []
        Company_State_list = []
        Postel_code_list = []
        City_list = []
        Job_Posted_list = []
        Job_Expire_list = []
        Job_Categories_list = []
        Job_Type_list = []
        Job_education_list = []
        Job_Experence_list= []
        Salary_des_list = []
        Job_Description_list = []
        is_html_description_list = []
        Job_poster_list = []

        Links_list =[]

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

        #=============SOURCE_FROM_HEADER_JSON==============SOURCE_NO..>>>>01<<<======================================
        try:
            details1 = soup.find('div', attrs={'id': 'wrapper'})
            # details2 = details1.find('div', attrs={'id': 'main-contents'})
            details3 = details1.find('script', attrs={'type': 'application/ld+json'})
            details = self.clean_soup(details3)
            detail_json = json.loads(details)
        except:
            pass


        #=============SOURCE_FROM_WEB_PAGE=================SOURCE_NO..>>>>02<<<======================================
        try:
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
            # print(_dict_job_details)
        except:
            pass

        # ======================================FILTERING=============================================================
        try:
            try:
                Job_Title = soup.find('h1', attrs={'id': 'head1'}).text
                Job_Title = self.clean_soup(Job_Title)
                print(Job_Title)
            except:
                Job_Title = detail_json["title"]
                print(Job_Title)
        except:
            Job_Title = None
        # ===================================================================================================
        try:
            try:
                Company_Name = detail_json["hiringOrganization"]["name"]
            except:
                Company_Name = _dict_job_details["Organization:"]
            print(Company_Name)
        except:
            Company_Name = None
        # ===================================================================================================
        try:
            Company_Logo = detail_json["hiringOrganization"]["logo"]
            print(Company_Logo)
        except:
            Company_Logo = None

        # ===================================================================================================
        try:
            Company_address = detail_json["jobLocation"]["address"]["streetAddress"]
            print(Company_address)
        except:
            Company_address = None
        # ===================================================================================================
        try:
            try:
                Job_Location = _dict_job_details["Vacancy Location:"]
            except:
                Job_Location = detail_json["jobLocation"]["address"]["addressLocality"]
            print(Job_Location)
        except:
            Job_Location = None
        # ===================================================================================================
        try:
            Company_State = detail_json["jobLocation"]["address"]["addressRegion"]
            print(Company_State)
        except:
            Company_State = None
        # ===================================================================================================
        try:
            Postel_code = detail_json["jobLocation"]["address"]["postalCode"]
            print(Postel_code)
        except:
            Postel_code = None
        # ===================================================================================================
        try:
            try:
                Job_Posted = detail_json["datePosted"]
                format_closing_date = '%d %B, %Y'
                datetime_obj = datetime.datetime.strptime(Job_Posted, format_closing_date)
                Job_Posted = datetime_obj.date()
            except:
                Job_Posted = _dict_job_details["Date Posted:"]
                format_closing_date = '%d %B, %Y'
                datetime_obj = datetime.datetime.strptime(Job_Posted, format_closing_date)
                Job_Posted = datetime_obj.date()
            print(Job_Posted)
        except:
            Job_Posted = None
        # ===================================================================================================
        try:
            try:
                Job_Expire = detail_json["validThrough"]
                format_closing_date = '%d %B, %Y'
                datetime_obj = datetime.datetime.strptime(Job_Expire, format_closing_date)
                Job_Expire = datetime_obj.date()
            except:
                Job_Expire1 = _dict_job_details["Expected Last Date:"]
                Job_Expire2 = Job_Expire1.replace("or see Paper Advert", "")
                format_closing_date = '%d %B, %Y'
                datetime_obj = datetime.datetime.strptime(Job_Expire2, format_closing_date)
                Job_Expire = datetime_obj.date()
            print(Job_Expire)
        except:
            Job_Expire = None
        # ===================================================================================================
        try:
            try:
                Job_Categories = detail_json["industry"]
            except:
                Job_Categories = _dict_job_details["Job Industry:"]
                Job_Categories = Job_Categories.replace(' Jobs', '')
            print(Job_Categories)
        except:
            Job_Categories = None
        # ===================================================================================================
        try:
            try:
                Job_Type = _dict_job_details["Job Type:"]
            except:
                Job_Type = detail_json["employmentType"]
            print(Job_Type)
        except:
            Job_Type = None
        # ===================================================================================================
        try:
            try:
                Job_education = detail_json["educationRequirements"]
            except:
                Job_education = _dict_job_details["Education:"]
            print(Job_education)
        except:
            Job_education = None
        # ===================================================================================================
        try:
            try:
                Job_Experence = detail_json["experienceRequirements"]
            except:
                Job_Experence = _dict_job_details["Job Experience:"]
            print(Job_Experence)
        except:
            Job_Experence = None
        # ===================================================================================================
        try:
            Salary_des = detail_json["baseSalary"]["@type"]
            print(Salary_des)
        except:
            Salary_des = None
        # ===================================================================================================
        try:
            Currency = detail_json["baseSalary"]["currency"]
            print(Currency)
        except:
            Currency = None
        # ===================================================================================================
        try:
            try:
                Job_Description = detail_json["description"]
            except:
                is_html_description = soup.find('div', attrs={'id': 'ad-desc-cont'})
                Job_Description = self.clean_soup(is_html_description)
            print(Job_Description)
        except:
            Job_Description = None
        # ===================================================================================================
        try:
            is_html_description = soup.find('div', attrs={'id': 'ad-desc-cont'})
            print(is_html_description)
        except:
            is_html_description = None
        # ===================================================================================================
        try:
            image_url = soup.find('div', attrs={'id': 'ad-pic-cont'})
            image_url1 = image_url.find('img', attrs={'src': re.compile('^https')})
            # image_url = self.clean_soup(image_url)
            Job_poster = image_url1['src']
            print(Job_poster)
        except:
            Job_poster = None



        #csv_columns
        Job_Id_list.append(Job_Id)
        Job_Title_list.append(Job_Title)
        Company_Name_list.append(Company_Name)
        Company_Logo_list.append(Company_Logo)
        Company_address_list.append(Company_address)
        Job_Location_list.append(Job_Location)
        Company_State_list.append(Company_State)
        Postel_code_list.append(Postel_code)
        City_list.append(City)
        Job_Posted_list.append(Job_Posted)
        Job_Expire_list.append(Job_Expire)
        Job_Categories_list.append(Job_Categories)
        Job_Type_list.append(Job_Type)
        Job_education_list.append(Job_education)
        Job_Experence_list.append(Job_Experence)
        Salary_des_list.append(Salary_des)
        Job_Description_list.append(Job_Description)
        is_html_description_list.append(is_html_description)
        Job_poster_list.append(Job_poster)

        Links_list.append(link)


        # print("Job is available...")
        # # UPDATE CURRENT DATA
        # table_name = 'jobs'
        # update_columns = "description= '%s'" % Job_Description
        # search_key = 'id'
        # update_ids = [check_job_available["id"]]
        # self.db_model.update_multiple_records(table_name, update_columns, search_key, update_ids)
        # print("Job ID %s is updated..." % check_job_available["id"])
    #
    # def make_output(self):
        post_data = {
            'platform': self.platform,
            'unique_id': Job_Id_list,
            'job_title': Job_Title_list,
            'company_name': Company_Name_list,
            'company_logo': Company_Logo_list,
            'company_address': Company_address_list,
            'company_city': Job_Location_list,
            'company_state': Company_State_list,
            'company_postal_code': Postel_code_list,
            'extra_company_location_details': City_list,
            'job_start_date': Job_Posted_list,
            'job_closing_date': Job_Expire_list,
            'job_category': Job_Categories_list,
            'job_type': Job_Type_list,
            'educational_requirements': Job_education_list,
            'job_Experence': Job_Experence_list,
            'job_salary_desc': Salary_des_list,
            'job_raw_description': Job_Description_list,
            'is_html_description': is_html_description_list,
            'job_link': Links_list,
            'Job_poster': Job_poster_list,
            's3_url_company_logo': s3_url_company_logo,
            's3_url_job_poster': s3_url_job_poster

        }
        df = pd.DataFrame(post_data)
        if os.path.isfile('Jobz_test.csv'):
            df.to_csv("Jobz_test.csv", mode='a', header=False)
        else:
            df.to_csv("Jobz_test.csv")
        # df.to_csv("Jobz_test.csv")



    def Post_request(self,post_urls, c_link):
        print("next===> Post_request")
        for link in post_urls:
            print("========scrap_link=============="+link)
            print("===<<<Post_Count>>>===", self.post_count)
            try:
                content = requests.get(link, timeout=30)
                soup = BeautifulSoup(content.text, features="lxml")
                sleep = random.randint(3, 5)
                time.sleep(sleep)
            except:
                pass
            self.create_final_output(soup, link, c_link)
            self.post_count += 1
            # self.make_output()


    def read_city_main_urls(self, city_list):
        post_urls = []
        for c_link in city_list:
            print("JOBZ  ==> " + c_link)
            next_page_url = c_link[:-1]
            next_page = True
            count = 1
            self.current_page = c_link
            while next_page:
                print("--------------------", self.current_page)
                sleep = random.randint(3, 5)
                time.sleep(sleep)
                try:
                    content1 = requests.get(self.current_page, timeout=30)
                    soup = BeautifulSoup(content1.text, features="lxml")
                except:
                    print("Page_not_working")
                    print(self.current_page)
                    pass
                try:
                    post = soup.find('div', attrs={'class': "first_big_4col"})
                    post1 = post.findAll('div', attrs={'itemprop': "itemListElement"})
                except:
                    pass
                for post_url in post1:
                    try:
                        one = post_url.find('div', attrs={'class': "cell1"})
                        two = one.find('a', attrs={'href': re.compile(('^https'))})
                        two = two['href']
                        post_urls.append(two)
                    except:
                        pass
                    print(two)
                self.current_page = next_page_url+"-"+str(count)+"/"
                count += 1
                if count >= 3:
                    break
            self.Post_request(post_urls, c_link)


    def get_all_jobs_urls(self, url):
        print(url)
        links = []
        try:
            content = requests.get(url, timeout=60)
            soup = BeautifulSoup(content.text, features="lxml")
        except:
            print("Domain Not Availabe")
            pass
        try:
            job_cities = soup.find('div', attrs={'id': "right-container-temp2"})
            job_cities1 = job_cities.find('div', attrs={'class': "table_contents"})
            job_cities2 = job_cities1.findAll('div', attrs={'class': "table_cell"})
        except:
            pass
        for job_city in job_cities2:
            try:
                one = job_city.find('a', attrs={'href': re.compile('^https')})
                one = (one['href'])
                links.append(one)
                print(one)

            except:
                pass
        self.read_city_main_urls(links)


    def input_url_download(self):
        url = self._all_jobs_url
        self.get_all_jobs_urls(url)
        print("one")

if __name__ == '__main__':
    scraper = jobz()
    scraper.input_url_download()


