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


class in_indeed:
    def __init__(self):
        # self.helper = Helper()
        self.driver = None
        self.wait = None
        self.page_count = 1
        self.post_count = 1
        self._main_url = "https://in.indeed.com"
        self._all_jobs_cat_url = "https://in.indeed.com/browsejobs"
        self.platform = "App\\in.indeed"
        self.source_id = "9"
        self.output = pd.DataFrame()
        self.chromedriver_path = os.environ.get("CHROME_DRIVER")
        self.S3_BUCKET_URL = os.environ.get("S3_BUCKET_URL")
        # self.current_page = None

        # self.Job_Id_list = []
        # self.Company_Name_list = []
        # self.Company_Logo_list = []
        # self.Job_Title_list = []
        # self.Job_Location_list = []
        # self.City_list = []
        # self.Job_Posted_list = []
        # self.Job_Expire_list = []
        # self.Job_Type_list = []
        # self.Job_education_list = []
        # self.Job_Experence_list= []
        # self.Role_Categories_list = []
        # self.Functional_Area_list = []
        # self.Industry_Type_list = []
        # self.Role_list = []
        # self.Job_Description_list = []
        # self.About_company_list = []
        # self.Key_Skills_list = []
        # self.Company_Info_list = []
        # self.Salary_des_list = []
        # self.Links_list = []

        # self.Links_list1 = []


        # self.db_model = BaseDBModel()
    def driver_load(self):
        options = webdriver.ChromeOptions()
        options.headless = True
        # options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options, executable_path="/home/ilabs/Desktop/AMD/chromedriver_linux64/chromedriver",
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

    def create_final_output(self, soup, link, job_sub):
        # job_ad_url = link
        # Job_ID = link.split("/")[5]
        Job_Id = ''
        Job_Caregory = ''
        Company_Name = ''

        Company_Logo = ''
        Job_Title = ''
        Job_Location = ''
        City = ''
        Company_Address = ''
        Carrer_page_url = ''
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

        Job_Id_list = []
        Job_Caregory_list = []
        Company_Name_list = []
        Company_Logo_list = []
        Job_Title_list = []
        Job_Location_list = []
        City_list = []
        Company_Address_list = []
        Carrer_page_url_list = []
        Job_Posted_list = []
        Job_Expire_list = []
        Job_Type_list = []
        Job_education_list = []
        Job_Experence_list= []
        Role_Categories_list = []
        Functional_Area_list = []
        Industry_Type_list = []
        Role_list = []
        Job_Description_list = []
        About_company_list = []
        Key_Skills_list = []
        Company_Info_list = []
        Salary_des_list = []
        Links_list = []

        try:
            Job_Id1 = re.search(r"(?<=jk=).*?(?=&)", link).group(0)
        except:
            Job_Id1 = None
        unique_key_pre = self.platform.replace("\\", "-").lower()
        Job_Id = unique_key_pre + "_" + Job_Id1
        print("unique_ID*************" + Job_Id)
        #=============================================================================================
        try:
            Job_Caregory = re.search(r"(?<=/browsejobs/)\w+", job_sub).group(0)
            print("Category*************" + Job_Caregory)
        except:
            Job_Caregory = None
        #=============================================================================================
        try:
            Job_Title1 = soup.find('div', attrs={"role": "main"})
            Job_Title = Job_Title1.find('h1').text
            print(Job_Title)
        except:
            Job_Title = None
        #=============================================================================================
        try:
            Company_Name1 = soup.find('div', attrs={'role': "main"})
            Company_Name2 = Company_Name1.find('div', attrs={'class': re.compile('CompanyInfoWithReview')})
            Company_Name3 = Company_Name2.find('div', attrs={'class': re.compile('icl-u-xs-mr--xs')})
            Company_Name = Company_Name3.find('a', attrs={'target': '_blank'}).text
            print(Company_Name)
            Company_Review_link = Company_Name3.find('a', attrs={'target': '_blank'})["href"]
            print(Company_Review_link)
        except:
            Company_Name = None
        #=============================================================================================


        #=============================================================================================
        try:
            try:
                Company_Name = detail_json['hiringOrganization']['name']
                print(Company_Name)
            except:
                Company_Name1 = soup.find('div', attrs={'id': 'root'})
                Company_Name2 = Company_Name1.find('div', attrs={'class': 'jd-header-comp-name'})
                Company_Name3 = Company_Name2.find('a').text
                Company_Name = self.clean_soup(Company_Name3)
                print(Company_Name)
        except:
            Company_Name = None
        #=============================================================================================
        try:
            try:
                Company_Logo = detail_json['hiringOrganization']['logo']
                print(Company_Logo)
            except:
                Company_Logo1 = soup.find('div', attrs={'id': 'root'})
                Company_Logo2 = Company_Logo1.find('img', attrs={'class': 'comp-banner'})
                Company_Logo3 = Company_Logo2['src']
                Company_Logo = self.clean_soup(Company_Logo3)
                print(Company_Logo)
        except:
            Company_Logo = None
        #=============================================================================================
        try:
            try:
                Job_Experence = detail_json['experienceRequirements']
                print(Job_Experence)
            except:
                Job_Experence1 = soup.find('div', attrs={'id': 'root'})
                Job_Experence2 = Job_Experence1.find('div', attrs={'class': 'exp'}).text
                Job_Experence = self.clean_soup(Job_Experence2)
                print(Job_Experence)
        except:
            Job_Experence = None
        #=============================================================================================
        try:
            try:
                Salary_des = detail_json['baseSalary']['value']['value']
                print(Salary_des)
            except:
                Salary_des1 = soup.find('div', attrs={'id': 'root'})
                Salary_des2 = Salary_des1.find('div', attrs={'class': 'salary'}).text
                Salary_des = self.clean_soup(Salary_des2)
                print(Salary_des)
        except:
            Salary_des = None
        #=============================================================================================
        try:
            try:
                Job_Location1 = detail_json['jobLocation']['address']['addressLocality']
                Job_Location = Job_Location1[1:-1].text
                print(Job_Location)
            except:
                Job_Location1 = soup.find('div', attrs={'id': 'root'})
                Job_Location = Job_Location1.find('div', attrs={'class': 'loc'}).text
                try:
                    Job_Location = Job_Location.replace("View More", "")
                except:
                    pass
                Job_Location = self.clean_soup(Job_Location)
                print(Job_Location)
        except:
            Job_Location = None
        #=============================================================================================
        try:
            try:
                Job_Description = detail_json['description']
                print(Job_Description)
            except:
                Job_Description1 = soup.find('div', attrs={'id': 'root'})
                Job_Description = Job_Description1.find('div', attrs={'class': 'dang-inner-html'})
                # Job_Description = self.clean_soup(Job_Description2)
                print(Job_Description)
        except:
            Job_Description = None
        #=============================================================================================
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
        except:
            pass

        try:
            try:
                Role = detail_json['responsibilities']
                print(Role)
            except:
                Role = _dict_job_details["Role"]
                print(Role)
        except:
            Role = None
        try:
            try:
                Industry_Type = detail_json['industry'][1:-1].text
                print(Industry_Type)
            except:
                Industry_Type = _dict_job_details["Industry Type"]
                print(Industry_Type)
        except:
            Industry_Type = None
        try:
            try:
                Job_Type = detail_json['employmentType']
                print(Job_Type)
            except:
                Job_Type = _dict_job_details["Employment Type"]
                print(Job_Type)
        except:
            Job_Type = None
        try:
            try:
                Functional_Area = detail_json['occupationalCategory'][1:-1].text
                print(Functional_Area)
            except:
                Functional_Area = _dict_job_details["Functional Area"]
                print(Functional_Area)
        except:
            Functional_Area = None
        try:
            Role_Categories = _dict_job_details["Role Category"]
            print(Role_Categories)
        except:
            Role_Categories = None

        #=============================================================================================

        try:
            try:
                Job_education = detail_json['description']
                print(Job_education)
            except:
                Job_education2 = soup.find('div', attrs={'id': 'root'})
                Job_education = ""
                for Job_education1 in Job_education2.find_all('div', attrs={'class': 'education'}):
                    for Job_education1 in Job_education1.find_all('div', attrs={'class': 'details'}):
                        Job_education1 = self.clean_soup(Job_education1)
                        Job_education += Job_education1+", "
                print(Job_education)
        except:
            Job_education = None
        #=============================================================================================

        try:
            try:
                Key_Skills = detail_json['skills'][1:-1].text
                print(Key_Skills)
            except:
                Key_Skills2 = soup.find('div', attrs={'id': 'root'})
                Key_Skills = ""
                for Key_Skills1 in Key_Skills2.find_all('div', attrs={'class': 'key-skill'}):
                    for Key_Skills1 in Key_Skills1.find_all('a'):
                        Key_Skills1 = self.clean_soup(Key_Skills1)
                        Key_Skills += Key_Skills1 + ", "
                print(Key_Skills[:-1])
        except:
            Key_Skills = None
        #=============================================================================================
        try:
            if soup.find('div', attrs={'id': 'root'}):
                About_company = soup.find('div', attrs={'class': 'detail dang-inner-html'}).text
                About_company = self.clean_soup(About_company)
                print(About_company)
        except:
            About_company = None
        print("===================================================TEST============================================================")
        try:
            if soup.find('div', attrs={'id': 'root'}):
                for Company_Info in soup.find_all('div', attrs={'class': 'comp-info-detail'}):
                    # try:
                    #     Carrer_page_url1 = Company_Info.find('span')
                    #     Carrer_page_url2 = Carrer_page_url1.find('a')
                    #     Carrer_page_url3 = Carrer_page_url2['href']
                    #     Carrer_page_url = Carrer_page_url3.find(re.compile("^http"))
                    #     print(Carrer_page_url)
                    # except:
                    #     Carrer_page_url = None

                    try:
                        Company_Address1 = Company_Info.find('span').text
                        Company_Address2 = self.clean_soup(Company_Address1)
                        try:
                            Carrer_page_url = (re.search("(?P<url>https?://[^\s]+)", Company_Address2).group("url"))
                            print("url...........", Carrer_page_url)
                            Company_Address = None
                        except:
                            Carrer_page_url = None
                            Company_Address = Company_Address2
                            print(Company_Address)
                    except:
                        Company_Address = None


        except:
            Company_Info = None



        #csv_columns
        Job_Id_list.append(Job_Id)
        Company_Name_list.append(Company_Name)
        Company_Logo_list.append(Company_Logo)
        Job_Title_list.append(Job_Title)
        Job_Location_list.append(Job_Location)
        City_list.append(City)
        Company_Address_list.append(Company_Address)
        Carrer_page_url_list.append(Carrer_page_url)
        Job_Posted_list.append(Job_Posted)
        Job_Expire_list.append(Job_Expire)
        Job_Type_list.append(Job_Type)
        Job_education_list.append(Job_education)
        Job_Experence_list.append(Job_Experence)
        Role_Categories_list.append(Role_Categories)
        Functional_Area_list.append(Functional_Area)
        Industry_Type_list.append(Industry_Type)
        Role_list.append(Role)
        Job_Description_list.append(Job_Description)
        About_company_list.append(About_company)
        Key_Skills_list.append(Key_Skills)
        Company_Info_list.append(Company_Info)
        Salary_des_list.append(Salary_des)
        Links_list.append(link)



        # print("Job is available...")
        # # UPDATE CURRENT DATA
        # table_name = 'jobs'
        # update_columns = "description= '%s'" % Job_Description
        # search_key = 'id'
        # update_ids = [check_job_available["id"]]
        # self.db_model.update_multiple_records(table_name, update_columns, search_key, update_ids)
        # print("Job ID %s is updated..." % check_job_available["id"])

    # def make_output(self):
        post_data = {
            'platform': self.platform,
            'unique_id': Job_Id_list,
            'source_id': self.source_id,
            'job_title': Job_Title_list,
            'company_name': Company_Name_list,
            'company_logo': Company_Logo_list,
            'company_description': About_company_list,
            # 'contect_info': Company_Info_list,
            'company_address': Company_Address,
            'career_page_url': Carrer_page_url,
            'job_type': Job_Type_list,
            'extra_job_location_details': Job_Location_list,
            'job_city': City_list,
            'job_state': Job_State,
            'job_link': Links_list,
            'job_start_date': Job_Posted_list,
            'job_closing_date': Job_Expire_list,
            'job_raw_description': Job_Description_list,
            'educational_requirements': Job_education_list,
            'working_experience': Job_Experence_list,
            'job_salary_desc': Salary_des_list,
            'job_category': Role_Categories_list,
            'functional_area': Functional_Area_list,
            'company_industry': Industry_Type_list,
            'extra_job_details': Role_list,
            'extra_job_requirement_details': Key_Skills_list

            # 's3_url_company_logo': s3_url_company_logo,
            # 's3_url_job_poster': s3_url_job_poster

        }
        df = pd.DataFrame(post_data)
        if os.path.isfile('Naukri_test.csv'):
            df.to_csv("Naukri_test.csv", mode='a', header=False)
        else:
            df.to_csv("Naukri_test.csv")

        print("||||||||||||||>>>>UPDATED<<<<||||||||||||||")



    # def post_request(self, Job_url0, job_sub):
    def post_request(self):
        print("next===> Post_request")
        job_sub = "https://in.indeed.com/browsejobs/Accounting"
        Job_url0 = ['https://in.indeed.com/rc/clk?jk=7d45d4664ef17935&fccid=cce3e9ab7a6f08b8&vjs=3']
        # self.driver_load()
        for link in Job_url0:
            print("|||||>>>>>+++++*****SCRAPE_REQUEST*****+++++<<<<<|||||")
            print("+++++||||Job_Post_Count==>>>>>",self.post_count,"<<<<<<||||+++++", )
            self.post_count += 1
            try:
                # self.driver.get(link)
                sleep = random.randint(1, 3)
                time.sleep(sleep)
                # content1 = requests.get(self.current_page, headers=headers, timeout=30)
                # soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                content = requests.get(link, timeout=30)
                soup = BeautifulSoup(content.text, features="lxml")
                # print(soup.prettify())
                print("||||||||||||||||****SCRAPED****|||||||||||||||||")
                # self.driver.quit()
            except:
                pass
            self.create_final_output(soup, link, job_sub)




    def get_all_jobs_urls(self, Job_sub0, job_sub):
        Job_url0 = []
        # Job_sub0 = ['https://in.indeed.com/jobs?q=Account+Assistant&from=brws&nc=brws']
        for job_url in Job_sub0:
            print("<<<<<<<<<<<<<Get_job_sub_links>>>>>>>>>>>>>")
            print("Job_Sub_category====>", job_url)

            while self.page_count < 100:
                print("||||||Page_Count>>>", self.page_count, "------------", job_url)
                self.page_count += 1
                try:
                    content = requests.get(job_url, timeout=30)
                    soup = BeautifulSoup(content.text, features="lxml")
                    sleep = random.randint(3, 5)
                    time.sleep(sleep)
                except Exception as e:
                    print(e)
                    print("Job Urls Nor Available ==> Domain Issue")
                job_url1 = soup.find('table', attrs={'id': 'resultsBody'})
                job_url2 = job_url1.find('table', attrs={'id': 'pageContent'})
                for job_url3 in job_url2.find_all('td', attrs={'id': 'resultsCol'}):
                    for job_url4 in job_url3.find_all('div', attrs={'data-tn-component': 'organicJob'}):
                        job_url5 = job_url4.find('h2', attrs={'class': 'title'})
                        job_url6 = job_url5.find('a')["href"]
                        job_url7 = self._main_url + job_url6
                        Job_url0.append(job_url7)
                        print(job_url7)
                self.post_request(Job_url0, job_sub)

                # --------------------Pagination-----------------------
                try:
                    page1 = soup.find('table', attrs={'id': 'resultsBody'})
                    page2 = page1.find('table', attrs={'id': 'pageContent'})
                    page3 = page2.find('nav', attrs={'role': "navigation"})
                    page4 = page3.find('ul', attrs={'class': 'pagination-list'})
                    page5 = page4.find('a', attrs={'aria-label': "Next"})["href"]
                    page6 = self._main_url+page5
                    print(page6)
                    job_url = page6
                except:
                    break
    # ============================================================================================================


    def get_all_jobs_sub_cat(self, Job_cat0):
        Job_sub0 = []
        for job_sub in Job_cat0:
            print("<<<<<<<<<<<<<Get_job_main_links>>>>>>>>>>>>>")
            print("Job_main_category==>", job_sub)
            try:
                content = requests.get(job_sub, timeout=30)
                soup = BeautifulSoup(content.text, features="lxml")
                sleep = random.randint(3, 5)
                time.sleep(sleep)
            except Exception as e:
                print(e)
                print("Job Category Not Availabel ==> Domain Issue")
            job_sub = soup.find('div', attrs={'class': re.compile('by_title')})
            for job_sub1 in job_sub.find_all('table', attrs={'role': re.compile('presentation')}):
                for job_sub2 in job_sub1.find_all("tr"):
                    for job_sub3 in job_sub2.find_all("td"):
                        for job_sub4 in job_sub3.find_all('p', attrs={'class': "job"}):
                            job_sub5 = job_sub4.find('a')["href"]
                            job_sub6 = self._main_url+job_sub5
                            Job_sub0.append(job_sub6)
                            print(job_sub6)
            # -----------------------------------------------
            self.get_all_jobs_urls(Job_sub0, job_sub)
    # ============================================================================================================


    def get_all_jobs_cat_urls(self, url):
        print(url)
        links = []
        try:
            content = requests.get(url, timeout=30)
            soup = BeautifulSoup(content.text, features="lxml")
            print("********************INITIATION*********************")
            sleep = random.randint(3, 5)
            time.sleep(sleep)
            # print(soup.prettify())
            # sys.exit()
        except:
            print("Domain Not Availabe")
            pass

        job_cat = soup.find('table', attrs={'id': "main_content"})
        # print(job_cities)
        for job_cat1 in job_cat.find_all('ul', attrs={'id': "categories"}):
            # print(job_cities1)
            job_cat0 = []
            for job_cat2 in job_cat1.find_all('li', attrs={'class': re.compile('^category')}):
                job_cat3 = job_cat2.find('a')['href']
                job_cat4 = self._main_url+job_cat3
                job_cat0.append(job_cat4)
                print(job_cat4)
            #----------------------------------------------
            self.get_all_jobs_sub_cat(job_cat0)
    # ============================================================================================================


    def input_url_download(self):
        url = self._all_jobs_cat_url
        self.get_all_jobs_cat_urls(url)
        print("one")
    # ============================================================================================================


    def test(self):
        # self.driver_load()
        link = 'https://in.indeed.com/viewjob?jk=5f86372e2cb171d3&tk=1f0qii15fsttb800&from=serp&vjs=3'
        # self.driver.get(link)
        # soup = BeautifulSoup(self.driver.page_source, features="lxml")
        content = requests.get(link, timeout=30)
        soup = BeautifulSoup(content.text, features="lxml")
        print(soup.prettify())
    # ============================================================================================================



if __name__ == '__main__':
    scraper = in_indeed()
    # scraper.input_url_download()
    # scraper.get_all_jobs_urls()
    # scraper.read_city_main_urls()
    # scraper.test()
    scraper.post_request()


