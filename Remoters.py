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


class Remoters:
    def __init__(self):
        # self.helper = Helper()
        self.driver = None
        self.wait = None
        self.page_count = 1
        self.post_count = 1
        self._main_url = "https://remoters.net"
        self._all_jobs_url = "https://remoters.net/jobs/"
        self.platform = "App\\Remoters"
        self.source_id = "15"
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

    def create_final_output(self, soup, link, c_url, state):
        # job_ad_url = link
        # Job_ID = link.split("/")[5]
        Job_Id = ''
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
            details1 = soup.find('script', attrs={'type': 'application/ld+json'})
            details2 = self.clean_soup(details1)
            detail_json = json.loads(details2)
            print("||||||||SOURCE_NO=>01======>>PAGE_JSON")

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
        #=============================================================================================

        try:
            try:
                Job_Id1 = detail_json['identifier']['value']
                unique_key_pre = self.platform.replace("\\", "-").lower()
                Job_Id = unique_key_pre + "_" + Job_Id1
                print("unique_ID*************" + Job_Id)
            except:
                Job_Id2 = re.search(r"(?<=-years-).*?(?=src=)", link).group(0)
                try:
                    Job_Id1 = Job_Id2.replace("?", "")
                except:
                    pass
                unique_key_pre = self.platform.replace("\\", "-").lower()
                Job_Id = unique_key_pre + "_" + Job_Id1
                print("unique_ID*************"+Job_Id)
        except:
            Job_Id = None
        #=============================================================================================
        try:
            try:
                City = detail_json['jobLocation']['addressRegion']
                print("city*****JN********" + City)
            except:
                City = re.search(r"(?<=-in-)\w+", c_url).group(0)
                print("city*************"+City)
        except:
            City = None
        #=============================================================================================
        try:
            Job_State = re.search(r"(?<=-in-)\w+", state).group(0)
            print("state*************" + Job_State)
        except:
            Job_State = None
        #=============================================================================================

        try:
            try:
                Job_Title = detail_json['title']
                print(Job_Title)
            except:
                Job_Title1 = soup.find('div', attrs={'id': 'root'})
                Job_Title2 = Job_Title1.find('h1', attrs={'class': 'jd-header-title'}).text
                Job_Title = self.clean_soup(Job_Title2)
                print(Job_Title)
        except:
            Job_Title = None
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




    def Post_request(self, post_urls, c_urls, state):
        print("next===> Post_request")
        self.driver_load()
        # df = pd.read_csv('Naukri_test.csv')
        # post_urls = df['post_url'].tolist()
        # c_urls = df['city_link'].tolist()

        for link, c_url in zip(post_urls, c_urls):
        # for link in post_urls:
            print("|||||>>>>>+++++*****SCRAPE_REQUEST*****+++++<<<<<|||||")
            # print(link+"********"+c_url )
            print("+++++||||Job_Post_Count==>>>>>",self.post_count,"<<<<<<||||+++++", )
            self.post_count += 1
            try:
                self.driver.get(link)
                sleep = random.randint(3, 5)
                time.sleep(sleep)
                # content1 = requests.get(self.current_page, headers=headers, timeout=30)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                print("||||||||||||||||****SCRAPED****|||||||||||||||||")
                # print(soup.prettify())
                # content = requests.get(link, timeout=30)
                # soup = BeautifulSoup(content.text, features="lxml")
                # self.driver.quit()
            except:
                pass
            self.create_final_output(soup, link, c_url, state)
            # self.make_output()
        # self.driver.quit()

    def read_city_main_urls(self, city_list, state):
        # df = pd.read_csv('all_indian_cities.csv')
        # city_list = df['urls'].tolist()
        print(state)
        print("===============================================================")
        # print(city_list)
        self.driver_load()
        post_urls = []
        c_link_list = []
        for c_link in city_list:
            print("NAUKRI_CITY  ==> " + c_link)


            while self.page_count < 100:
                print("||||||Page_Count>>>",self.page_count,"------------", c_link)
                self.page_count += 1
                self.driver.get(c_link)
                sleep = random.randint(5, 7)
                time.sleep(sleep)
                print("....Dynamic..Request....")
                # content1 = requests.get(self.current_page, headers=headers, timeout=30)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                post = soup.find('div', attrs={'id': "root"})
                try:
                    for post1 in post.find_all('div', attrs={'class': "list"}):
                        for post2 in post1.find_all('a', attrs={'class': "title fw500 ellipsis"}):
                            post2 = post2['href']
                            # post_urls.append(post2)
                            post_urls.append(post2)
                            c_link_list.append(c_link)
                            print(post2)
                except:
                    pass
                print("<<<<<<<<<<<<<Get_job_links>>>>>>>>>>>>>")
                try:
                    print("Pagination")
                    self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div[3]/div[2]/section[2]/div[3]/a[2]'))).click()
                    # sleep = random.randint(3, 5)
                    # time.sleep(sleep)
                    c_link = self.driver.current_url

                except:
                    break

            #------------------------------------------------------------
            self.Post_request(post_urls, c_link_list, state)
            #-----------------------------------------------------------
        # post_csv={
        #     'post_url': self.Job_poster_list1,
        #     'city_link': self.Links_list1,
        # }
        # df = pd.DataFrame(post_csv)
        # df.to_csv("Test_naukri.csv")

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
            print("********************INITIATION*********************")
            # print(soup.prettify())
            # sys.exit()
        except:
            print("Domain Not Availabe")
            pass

        job_cat = soup.find('div', attrs={'class': "container clearfix"})
        # print(job_cat)
        for job_cat1 in job_cat.find_all('div', attrs={'class': re.compile('^table-category-jobs')}):
            # print(job_cat1)
            links = []
            for job_cat2 in job_cat1.find_all('div', attrs={'class': re.compile('^table-responsive')}):
                # print(job_cat2)
                job_cat3 = job_cat2.find('a', attrs={'class': "moreJobs"})
                job_cat4 = (job_cat3['href'])
                print(job_cat4)
                # links.append(job_cat3)
                # print(job_cat3)


            # print(links)
            # state = links.pop(0)
            # print("capital "+state)
            # links.pop(0)
        # print(links)
        # df = pd.DataFrame(links)
        # df.to_csv('file22.csv', index=False, header=False)

            # self.read_city_main_urls(links, state)


    def input_url_download(self):
        url = self._all_jobs_url
        self.get_all_jobs_urls(url)
        print("one")

    def test(self):
        # self.driver_load()
        link = 'https://remoters.net/jobs/'
        # self.driver.get(link)
        # soup = BeautifulSoup(self.driver.page_source, features="lxml")
        content = requests.get(link, timeout=30)
        soup = BeautifulSoup(content.text, features="lxml")
        print(soup.prettify())



if __name__ == '__main__':
    scraper = Remoters()
    scraper.input_url_download()
    # scraper.read_city_main_urls()
    # scraper.test()
    # scraper.Post_request()


