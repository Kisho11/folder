from lib2to3.pgen2 import driver

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


class naukri:
    def __init__(self):
        # self.helper = Helper()
        self.driver = None
        self.wait = None
        self.page_count = 1
        self.post_count = 1
        self._main_url = "https://www.bdjobs.com/"
        self._all_jobs_url = "https://www.bdjobs.com/"
        self.platform = "https://www.bdjobs.com/"
        self.output = pd.DataFrame()
        self.chromedriver_path = os.environ.get("CHROME_DRIVER")
        self.S3_BUCKET_URL = os.environ.get("S3_BUCKET_URL")
        # self.current_page = None
        self.Job_Id_list = []
        self.Company_Name_list = []
        self.Company_Logo_list = []
        self.Job_Title_list = []
        self.Job_Location_list = []
        self.City_list = []
        self.Job_Posted_list = []
        self.Job_Expire_list = []
        self.Job_Type_list = []
        self.Job_education_list = []
        self.Job_Experence_list = []
        self.Role_Categories_list = []
        self.Functional_Area_list = []
        self.Industry_Type_list = []
        self.Role_list = []
        self.Job_Description_list = []
        self.About_company_list = []
        self.Key_Skills_list = []
        self.Company_Info_list = []
        self.Salary_des_list = []
        self.Links_list = []

        self.Links_list1 = []

        # self.db_model = BaseDBModel()

    def driver_load(self):
        # options = webdriver.ChromeOptions()
        # options.headless = True
        self.driver = webdriver.Chrome(executable_path="/home/ilabs/Desktop/AMD/chromedriver_linux64/chromedriver",
                                       keep_alive=True)
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

    def create_final_output(self, soup, link, c_url):
        # job_ad_url = link
        # Job_ID = link.split("/")[5]
        Job_Id = ''
        Company_Name = ''
        Company_Logo = ''
        Job_Title = ''
        Job_Location = ''
        City = ''
        Job_Posted = ''
        Job_Expire = ''
        Job_Type = ''
        Job_education = ''
        Job_Experence = ''
        Role_Categories = ''
        Functional_Area = ''
        Industry_Type = ''
        Role = ''
        Job_Description = ''
        About_company = ''
        Key_Skills = ''
        Company_Info = ''
        Salary_des = ''
        s3_url_company_logo = ''
        s3_url_job_poster = ''
        company_email = ''

        try:
            details = soup.find('script', attrs={'type': 'application/ld+json'})
            detail_json = json.loads(details.text)
            try:
                Job_Posted = detail_json["datePosted"]
                print(Job_Posted)
            except:
                Job_Posted = None
            try:
                Job_Expire = detail_json["validThrough"]
                print(Job_Expire)
            except:
                Job_Expire = None
        except:
            pass

        try:
            Job_Id = re.search(r"(?<=-years-).*?(?=src=)", link).group(0)
            try:
                Job_Id = Job_Id.replace("?", "")
            except:
                pass
            print("unique_ID*************" + Job_Id)
        except:
            Job_Id = None

        print(c_url)
        try:
            City = re.search(r"(?<=-in-)\w+", c_url).group(0)
            print("city*************" + City)
        except:
            City = None

        try:
            if soup.find('div', attrs={'id': 'root'}):
                Job_Title = soup.find('h1', attrs={'class': 'jd-header-title'}).text
                Job_Title = self.clean_soup(Job_Title)
                print(Job_Title)
        except:
            Job_Title = None

        try:
            if soup.find('div', attrs={'id': 'root'}):
                Company_Name = soup.find('div', attrs={'class': 'jd-header-comp-name'})
                Company_Name = Company_Name.find('a').text
                Company_Name = self.clean_soup(Company_Name)
                print(Company_Name)
        except:
            Company_Name = None

        try:
            if soup.find('div', attrs={'id': 'root'}):
                Company_Logo = soup.find('img', attrs={'class': 'comp-banner'})
                Company_Logo = Company_Logo['src']
                Company_Logo = self.clean_soup(Company_Logo)
                print(Company_Logo)
        except:
            Company_Logo = None

        try:
            if soup.find('div', attrs={'id': 'root'}):
                Job_Experence = soup.find('div', attrs={'class': 'exp'}).text
                Job_Experence = self.clean_soup(Job_Experence)
                print(Job_Experence)
        except:
            Job_Experence = None

        try:
            if soup.find('div', attrs={'id': 'root'}):
                Salary_des = soup.find('div', attrs={'class': 'salary'}).text
                Salary_des = self.clean_soup(Salary_des)
                print(Salary_des)
        except:
            Salary_des = None

        try:
            if soup.find('div', attrs={'id': 'root'}):
                Job_Location = soup.find('div', attrs={'class': 'loc'}).text
                try:
                    Job_Location = Job_Location.replace("View More", "")
                except:
                    pass
                Job_Location = self.clean_soup(Job_Location)
                print(Job_Location)
        except:
            Job_Location = None

        try:
            if soup.find('div', attrs={'id': 'root'}):
                Job_Description = soup.find('div', attrs={'class': 'dang-inner-html'}).text
                Job_Description = self.clean_soup(Job_Description)
                print(Job_Description)
        except:
            Job_Description = None

        try:
            set = soup.find('div', attrs={'id': "root"})
            set1 = set.find('div', attrs={'class': "other-details"})
            _dict_job_details = {}
            for set2 in set1.find_all('div', attrs={'class': "details"}):
                label = set2.find('label')
                label = (label.text).strip()

                span = set2.find('span')
                span = (span.text).strip()
                _dict_job_details[label] = span
            # print(_dict_job_details)
            try:
                Role = _dict_job_details["Role"]
                print(Role)
            except:
                Role = None
            try:
                Industry_Type = _dict_job_details["Industry Type"]
                print(Industry_Type)
            except:
                Industry_Type = None
            try:
                Job_Type = _dict_job_details["Employment Type"]
                print(Job_Type)
            except:
                Job_Type = None
            try:
                Functional_Area = _dict_job_details["Functional Area"]
                print(Functional_Area)
            except:
                Functional_Area = None
            try:
                Role_Categories = _dict_job_details["Role Category"]
                print(Role_Categories)
            except:
                Role_Categories = None
        except:
            pass

        try:
            if soup.find('div', attrs={'id': 'root'}):
                Job_education = ""
                for Job_education1 in soup.find_all('div', attrs={'class': 'education'}):
                    for Job_education1 in Job_education1.find_all('div', attrs={'class': 'details'}):
                        Job_education1 = self.clean_soup(Job_education1)
                        Job_education += Job_education1 + ", "
                print(Job_education)
        except:
            Job_education = None

        try:
            if soup.find('div', attrs={'id': 'root'}):
                Key_Skills = ""
                for Key_Skills1 in soup.find_all('div', attrs={'class': 'key-skill'}):
                    for Key_Skills1 in Key_Skills1.find_all('a'):
                        Key_Skills1 = self.clean_soup(Key_Skills1)
                        Key_Skills += Key_Skills1 + ", "
                print(Key_Skills[:-1])
        except:
            Key_Skills = None

        try:
            if soup.find('div', attrs={'id': 'root'}):
                About_company = soup.find('div', attrs={'class': 'detail dang-inner-html'}).text
                About_company = self.clean_soup(About_company)
                print(About_company)
        except:
            About_company = None

        try:
            if soup.find('div', attrs={'id': 'root'}):
                Company_Info = soup.find('div', attrs={'class': 'comp-info-detail'})
                try:
                    Company_Info = Company_Info.find('span').text
                    Company_Info = self.clean_soup(Company_Info)
                    print(Company_Info)
                except:
                    Company_Info = Company_Info.find('span')
                    Company_Info = Company_Info.find('a')
                    Company_Info = Company_Info['href']
                    print(Company_Info)
        except:
            Company_Info = None

        # csv_columns
        self.Job_Id_list.append(Job_Id)
        self.Company_Name_list.append(Company_Name)
        self.Company_Logo_list.append(Company_Logo)
        self.Job_Title_list.append(Job_Title)
        self.Job_Location_list.append(Job_Location)
        self.City_list.append(City)
        self.Job_Posted_list.append(Job_Posted)
        self.Job_Expire_list.append(Job_Expire)
        self.Job_Type_list.append(Job_Type)
        self.Job_education_list.append(Job_education)
        self.Job_Experence_list.append(Job_Experence)
        self.Role_Categories_list.append(Role_Categories)
        self.Functional_Area_list.append(Functional_Area)
        self.Industry_Type_list.append(Industry_Type)
        self.Role_list.append(Role)
        self.Job_Description_list.append(Job_Description)
        self.About_company_list.append(About_company)
        self.Key_Skills_list.append(Key_Skills)
        self.Company_Info_list.append(Company_Info)
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
            'about_company': self.About_company_list,
            'contect_info': self.Company_Info_list,
            # 'company_email': '',
            'job_type': self.Job_Type_list,
            'location': self.Job_Location_list,
            # 'city_location': self.City_location_list,
            'city': self.City_list,
            'job_link': self.Links_list,
            'start_at': self.Job_Posted_list,
            'closing_date': self.Job_Expire_list,
            'job_description': self.Job_Description_list,
            'educational_requirements': self.Job_education_list,
            'job_Experence': self.Job_Experence_list,
            'job_salary': self.Salary_des_list,
            # 'job_description': self.html_job_description_list,
            'role_categories': self.Role_Categories_list,
            'functional_area': self.Functional_Area_list,
            'industry_type': self.Industry_Type_list,
            'role': self.Role_list,
            'key_skills': self.Key_Skills_list

            # 's3_url_company_logo': s3_url_company_logo,
            # 's3_url_job_poster': s3_url_job_poster

        }
        df = pd.DataFrame(post_data)
        df.to_csv("Naukri.csv")

    def Post_request(self, post_urls, c_urls):
        print("next===> Post_request")
        self.driver_load()
        # df = pd.read_csv('Naukri_test.csv')
        # post_urls = df['post_url'].tolist()
        # c_urls = df['city_link'].tolist()

        for link, c_url in zip(post_urls, c_urls):
            # for link in post_urls:
            print(link + "********" + c_url)
            print("Job_Post_Count======", self.post_count)
            self.post_count += 1
            try:
                self.driver.get(link)
                sleep = random.randint(3, 5)
                time.sleep(sleep)
                # content1 = requests.get(self.current_page, headers=headers, timeout=30)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                # print(soup.prettify())
                # content = requests.get(link, timeout=30)
                # soup = BeautifulSoup(content.text, features="lxml")
                # self.driver.quit()
            except:
                pass
            self.create_final_output(soup, link, c_url)
            self.make_output()
        # self.driver.quit()

    def read_category_urls(self, cat_list):
        # df = pd.read_csv('file221.csv')
        # city_list = df['city_urls'].tolist()
        # print(state)
        # print("===============================================================")
        # print(city_list)
        self.driver_load()
        post_urls = []
        c_link_list = []
        for cat_list1 in cat_list:
            print("CATEGORY_REQUEST  ==> " + cat_list1)
            self.driver.get(cat_list1)
            page_count = 1
            while page_count <=  2:
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                # sleep = random.randint(5, 7)
                # time.sleep(sleep)

                print("pagination.............")
                pagination = soup.find('div', attrs={'id': "main"})
                pagination1 = pagination.find('div', attrs={'id': "topPagging"})
                pagination2 = pagination1.find('ul')
                for pagination3 in pagination2.find_all('li'):
                    # print(pagination3)
                    pagination4 = pagination3.find('a', attrs={'class': "currentpage"})
                    print(pagination4)
                    # pagination5 = pagination4.text
                    print("000000000")
                # print(pagination5)




                print("Pagination")
                # self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="jobList"]/div[1]/div[1]/div[27]/div/div/div[1]/div/ul/li[2]'))).click()
                # python_button = soup.find_elements_by_xpath('//*[@id="jobList"]/div[1]/div[1]/div[27]/div/div/div[1]/div/ul/li[2]')
                # python_button.click()

                    # sleep = random.randint(3, 5)
                    # time.sleep(sleep)
                    # cat_list1 = self.driver.current_url
                    # page = soup.find('div', attrs={'class': "pagination mt-64 mb-60"})
                    # page2 = page.find('a', attrs={'class': "fright fs14 btn-secondary br2"})
                    # page3 = page2["href"]
                    # c_link = self._main_url + page3
                    # print("Next URL ===>", c_link)



            # ------------------------------------------------------------
            # self.Post_request(post_urls, c_link_list)
            # -----------------------------------------------------------
            # post_csv = {
            #     'post_url': post_urls,
            #     'city_link': c_link_list,
            # }
            # df = pd.DataFrame(post_csv)
            # if os.path.isfile('1.csv'):
            #     df.to_csv("1.csv", mode='a', header=False)
            # else:
            #     df.to_csv("1.csv")

        #     print(post_urls)
        #     df = pd.DataFrame(post_urls)
        #     df.to_csv('post_urls.csv', index=False, header=False)
        #
        #     # self.driver.quit()
        # sys.exit()

    def get_all_jobs_urls(self, url):
        print(url)
        links = []
        try:
            content = requests.get(url, timeout=30)
            soup = BeautifulSoup(content.text, features="lxml")
            # print(soup.prettify())
            # sys.exit()
        except:
            print("Domain Not Availabe")
            pass

        job_cat = soup.find('div', attrs={'class': "category-list padding-mobile functional active"})
        job_cat1 = job_cat.find_all('li')
        # print(job_cat1)
        for job_cat2 in job_cat1:
            job_cat3 = job_cat2.find("a")
            job_cat4 = job_cat3["href"]
            job_cat5 = "https:"+job_cat4
            links.append(job_cat5)
            print("*************************************")

            # print(links)
            # state = links.pop(0)
            # print("capital "+state)
            # links.pop(0)
        # print(links)
        # df = pd.DataFrame(links)
        # df.to_csv('states.csv', index=False, header=False)
        #     print(links)
        self.read_category_urls(links)

    def input_url_download(self):
        url = self._all_jobs_url
        self.get_all_jobs_urls(url)
        print("one")

    def test(self):
        self.driver_load()
        link = 'https://www.naukri.com/job-listings-retail-agency-vacancy-telangana-sbi-life-insurance-co-ltd-adilabad-nizamabad-khammam-warangal-hyderabad-secunderabad-1-to-6-years-130121005924?src=jobsearchDesk&amp;sid=16116675462159710&amp;xp=1&amp;px=1'
        self.driver.get(link)
        # content = requests.get(link, timeout=30)
        soup = BeautifulSoup(self.driver.page_source, features="lxml")
        print(soup.prettify())


if __name__ == '__main__':
    scraper = naukri()
    scraper.input_url_download()
    # scraper.read_city_main_urls()
    # scraper.test()
    # scraper.Post_request()


