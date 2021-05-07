from dotenv import load_dotenv
import os
# import pytest
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


class wwr:
    def __init__(self):
        # self.helper = Helper()
        self.driver = None
        self.wait = None
        self.page_link = None
        self.page_count = 1
        self.post_count = 1
        self.link_count = 1
        self._main_url = "https://weworkremotely.com"
        self._all_com_url = "https://weworkremotely.com/remote-companies"
        self.platform = "https://weworkremotely.com/"
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
        # options.headless = True
        # options.add_argument("--headless")
        self.driver = webdriver.Chrome(executable_path="/home/kishanthan/Desktop/Amazon/amozon_fetcher/source/chromedriver",
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

    def create_final_output(self, soup, link):
        # print(soup)
        # job_ad_url = link
        # Job_ID = link.split("/")[5]
        Job_Id = ''
        Job_Title = ''
        Company_Name = ''
        Company_Logo = ''
        Job_Location = ''
        Company_Info = ''
        Contact = ''
        mail = ''
        OccupationalCategory = ''
        Job_Position = ''
        Job_Posted = ''
        Job_Expire = ''
        Job_Type = ''
        Job_Description = ''


        s3_url_company_logo = ''
        s3_url_job_poster = ''
        company_email = ''

        Job_Id_list = []
        Job_Title_list = []
        Company_Name_list = []
        Company_Logo_list = []
        Job_Location_list = []
        Company_Info_list = []
        Contact_list = []
        mail_list = []
        OccupationalCategory_list = []
        Job_Position_list = []
        Job_Posted_list = []
        Job_Expire_list = []
        Job_Type_list = []
        Job_Description_list = []
        Job_Description_html_list = []


        Links_list = []


        #=====source_from_page_elements=========
        set = soup.find('div', attrs={'class': "content"})
        # print(set)
        print("============================================")

        #=====source_from_Header_Json===========
        try:
            for details in soup.find_all('script', attrs={'type': 'application/ld+json'}):
                details1 = self.clean_soup(details)
                detail_json = json.loads(details1)
                # print(detail_json)
        except:
            pass

        # detail_json = json.loads(detail_json0)
        # print(detail_json)
        #==============================================================
        try:
            try:
                J_T = set.find('h1')
                Job_Title = self.clean_soup(J_T)
                print(Job_Title)
            except:
                Job_Title = detail_json["title"]
                print(Job_Title)
        except:
            Job_Title = None
        #======================================================================
        try:
            try:
                C_N = set.find('div', attrs={"class": "company-card"})
                C_N1 = C_N.find('h2')
                Company_Name = self.clean_soup(C_N1)
                print(Company_Name)
            except:
                Company_Name = detail_json["hiringOrganization"]["name"]
                print(Company_Name)
        except:
            Company_Name = None
        #==============================================================================
        Logo_base = ""
        #========================================================================================
        try:
            try:
                C_L = set.find('div', attrs={"class": "company-card"})
                C_L1 = C_L.find('div', attrs={"class": "listing-logo"})
                Company_Logo = C_L1.find('img')["src"]
                try:
                    Company_Logo = Company_Logo.replace("?ixlib=rails-4.0.0&w=50&h=50&dpr=2&fit=fill&auto=compress","")
                except:
                    pass
                Logo_base += Company_Logo
                print(Company_Logo)
            except:
                Company_Logo = detail_json["image"]
                try:
                    Company_Logo = Company_Logo.replace("?ixlib=rails-4.0.0&w=50&h=50&dpr=2&fit=fill&auto=compress","")
                except:
                    pass
                Logo_base += Company_Logo
                print(Company_Logo)
        except:
            Company_Logo = None
        #========================================================================================
        try:
            try:
                J_L = set.find('div', attrs={"class": "company-card"})
                J_L1 = J_L.find('h3')
                Job_Location = self.clean_soup(J_L1)
                print(Job_Location)
            except:
                Job_Location = detail_json["hiringOrganization"]["address"]
                print(Job_Location)
        except:
            Job_Location = None
        #=========================================================================================
        try:
            for Company_Info1 in set.find_all('div', attrs={"class": "company-card"}):
                Company_Info = Company_Info1.find('a', attrs={"target": "_blank"})["href"]
                print(Company_Info)
        except:
            Company_Info = None
        #=======================================================================================
        try:
            Contact1 = set.find('div', attrs={"class": "company-card"})
            Contact = Contact1.find('a', attrs={"id": "job-cta-alt-2"})["href"]
            print(Contact)
            try:
                mail = re.search(r'[\w\.-]+@[\w\.-]+', Contact)
                mail = mail.group(0)
                try:
                    mail = mail.replace("jobs@weworkremotely.com","")
                    Contact = None
                except:
                    mail = None
                    pass
            except:
                mail = None
                pass
        except:
            Contact = None
        #========================================================================================
        try:
            try:
                O_C = set.find('a', attrs={"href": re.compile("/categories")})
                O_C1 = O_C.find('span', attrs={"class": "listing-tag"})
                OccupationalCategory = self.clean_soup(O_C1)
                print(OccupationalCategory)
            except:
                OccupationalCategory = detail_json["occupationalCategory"]
                print(OccupationalCategory)
        except:
            OccupationalCategory = None
        #=========================================================================================
        try:
            for Job_Position1 in set.find('div', attrs={"class": "listing-header-container"}):
                Job_Position = self.clean_soup(Job_Position1)
                try:
                    Job_Position = Job_Position.replace("Only", "")
                except:
                    pass
                try:
                    Job_Position = Job_Position.replace("(100% Remote)", "")
                except:
                    pass
                try:
                    Job_Position = Job_Position.replace("Anywhere", "global")
                except:
                    pass
            print(Job_Position)
        except:
            Job_Position = None
        #===========================================================================================
        try:
            try:
                Job_Posted = detail_json["datePosted"]
                Job_Posted = Job_Posted.replace("UTC", "")
                print(Job_Posted)
            except:
                J_P = set.find('div', attrs={"class": "listing-header-container"})
                J_P1 = J_P.find('h3')
                J_P2 = J_P1.find('time')
                Job_Posted = J_P2["datetime"]
                Job_Posted = Job_Posted.replace("UTC", "")
                print(Job_Posted)
        except:
            Job_Posted = None
        #=========================================================================================
        try:
            Job_Expire = detail_json["validThrough"]
            Job_Expire = Job_Expire.replace("UTC", "")
            print(Job_Expire)
        except:
            Job_Expire = None
        #=========================================================================================
        try:
            try:
                J_T1 = set.find('a', attrs={"href": re.compile("/remote")})
                J_T2 = J_T1.find('span', attrs={"class": "listing-tag"})
                Job_Type = self.clean_soup(J_T2)
                print(Job_Type)
            except:
                Job_Type = detail_json["employmentType"]
                print(Job_Type)
        except:
            Job_Type = None
        #=========================================================================================
        try:
            Job_Id = re.search(r"(?<=logos/).*?(?=/logo)", Logo_base).group(0)
            Job_Id = Job_Id.replace("/", "")
            print("********************|||||>>>>unique_ID<<<<<|||||*********************>>>>>>" + Job_Id)
        except:
            Job_Id = None
        #=========================================================================================
        try:
            try:
                Job_Description = ""
                Job_Description_html0 = []
                for J_D in set.find('div', attrs={"class": "listing-container"}):
                    J_D1 = self.clean_soup(J_D)
                    Job_Description += (J_D1+'\n')
                    Job_Description_html0.append(J_D)
                    # print(J_D1)
                print(Job_Description)
                print("========================================DESCRIPTION==================================================")
                Job_Description_html0 = str(Job_Description_html0)[1:-1]
                print(Job_Description_html0)
            except:
                Job_Description1 = detail_json["description"]
                Job_Description = self.clean_soup(Job_Description1)
                print(Job_Description)
        except:
            Job_Description = None



        # print(c_url)
        # try:
        #     City = re.search(r"(?<=-in-)\w+", c_url).group(0)
        #     print("city*************"+City)
        # except:
        #     City = None




        #<<<<<<<<<<<<<csv_columns>>>>>>>>>>>>>>>>>>
        Job_Id_list.append(Job_Id)
        Job_Title_list.append(Job_Title)
        Company_Name_list.append(Company_Name)
        Company_Logo_list.append(Company_Logo)
        Job_Location_list.append(Job_Location)
        Company_Info_list.append(Company_Info)
        Contact_list.append(Contact)
        mail_list.append(mail)
        OccupationalCategory_list.append(OccupationalCategory)
        Job_Position_list.append(Job_Position)
        Job_Posted_list.append(Job_Posted)
        Job_Expire_list.append(Job_Expire)
        Job_Type_list.append(Job_Type)
        Job_Description_list.append(Job_Description)
        Job_Description_html_list.append(Job_Description_html0)

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
            'unique_key': Job_Id_list,
            'job_title': Job_Title_list,
            'company_name': Company_Name_list,
            'company_logo': Company_Logo_list,
            'location': Job_Location_list,
            'company_info': Company_Info_list,
            'contact': Contact_list,
            'mail': mail_list,
            'category': OccupationalCategory_list,
            'work_location': Job_Position_list,
            'job_start_date': Job_Posted_list,
            'job_closing_date': Job_Expire_list,
            'job_type': Job_Type_list,
            'job_raw_description': Job_Description_list,
            'is_html_description': Job_Description_html_list,
            'job_link': Links_list,

            # 'job_description': self.html_job_description_list,


            # 's3_url_company_logo': s3_url_company_logo,
            # 's3_url_job_poster': s3_url_job_poster

        }
        df = pd.DataFrame(post_data)
        if os.path.isfile('WWR_test.csv'):
            df.to_csv("WWR_test.csv", mode='a', header=False)
        else:
            df.to_csv("WWR_test.csv")


        print("<<<<<<<<<<<<<<<<<<<Updated>>>>>>>>>>>>>>>>>>>>>>")

    # def Post_request(self):
    def Post_request(self, post_urls):
        print("next===> Post_request")
        # self.driver_load()
        # df = pd.read_csv('Naukri_test.csv')
        # post_urls = df['post_url'].tolist()
        # c_urls = df['city_link'].tolist()
        # post_urls = ['https://weworkremotely.com/remote-jobs/quickmail-senior-growth-marketer']
        for link in post_urls:
            # link = 'https://weworkremotely.com/remote-jobs/institute-for-corporate-productivity-i4cp-software-developer-1'
            print("Job_Post_Count======", self.post_count)
            print("Post_link=> ",link)
            self.post_count += 1
            try:
                # self.driver.get(link)
                sleep = random.randint(3, 5)
                time.sleep(sleep)
                # content1 = requests.get(self.current_page, headers=headers, timeout=30)
                # soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                # print(soup.prettify())
                content = requests.get(link, timeout=30)
                soup = BeautifulSoup(content.text, features="lxml")
                # print(soup.prettify())
                # self.driver.quit()
                print("||||||||||||||||||||||||SCRAPED||||||||||||||||||||||||||")
            except Exception as error:
                print(error)
                pass
            self.create_final_output(soup, link)
            # self.make_output()
        # self.driver.quit()

    def get_job_post_url(self, Job_cat):
        # df = pd.read_csv('all_indian_cities.csv')
        # city_list = df['urls'].tolist()
        print(">>>>>>>>>>>>>>>>>>>>>>REQUESTING<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        # self.driver_load()
        post_urls = []
        for cat in Job_cat:
            print("JOBZ  ==> " + cat)
            # while self.page_count < 100:
            self.page_count += 1
            # self.driver.get(c_link)
            sleep = random.randint(5, 7)
            time.sleep(sleep)
            print("REQUEST DONE")
            content1 = requests.get(cat)
            soup = BeautifulSoup(content1.text, features="lxml")
            # print(soup.prettify())
            # soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            try:
                post = soup.find('div', attrs={'class': "jobs-container"})
                post1 = post.find('article')
                post2 = post1.find('ul')
                # link_count = 1
                for post3 in post2.find_all('li', attrs={'class': "feature"}):
                    for post4 in post3.find_all('a', attrs={'href': re.compile("^/remote")}):
                        post5 = post4['href']
                        post6 = self._main_url+post5
                        post_urls.append(post6)
                        print("link_no", self.link_count, post6)
                        self.link_count += 1


            except Exception as error:
                print(error)
                pass
            print(post_urls)
            self.Post_request(post_urls)
            # try:
            #     print("Pagination")
            #     self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div[3]/div[2]/section[2]/div[3]/a[2]'))).click()
            #     # sleep = random.randint(3, 5)
            #     # time.sleep(sleep)
            #     c_link = self.driver.current_url
            #
            # except:
            #     pass

            #------------------------------------------------------------

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


    def get_job_cat(self):
        url = self._main_url
        print("INITIATED==> ", url)
        # url = 'https://weworkremotely.com/remote-companies?page=190'
        Job_cat0 = []
        try:
            content = requests.get(url, timeout=30)
            soup = BeautifulSoup(content.text, features="lxml")
            # print(soup.prettify())
        except Exception as e:
            print(e)
            print("Domain Not Availabe")
            pass

        try:
            job_cat1 = soup.find('div', attrs={'class': "container"})
            for job_cat2 in job_cat1.find_all('ul', attrs={'class': "dropdown categories"}):
                for job_cat3 in job_cat2.find_all('li'):
                    job_cat4 = job_cat3.find('a')["href"]
                    job_cat = self._main_url+job_cat4
                    Job_cat0.append(job_cat)
                    print(job_cat)
        except Exception as e:
            print(e)
            pass
        print(Job_cat0)
        self.get_job_post_url(Job_cat0)


    def get_all_company_links(self):
        url = self._all_com_url
        print("INITIATED==> ", url)
        # url = 'https://weworkremotely.com/remote-companies?page=190'
        Job_com0 = []
        self.page_link = url
        while self.page_count < 500:
            print("Page Number ==> ", self.page_count)
            self.page_count += 1
            try:
                content = requests.get(self.page_link, timeout=30)
                soup = BeautifulSoup(content.text, features="lxml")
                # print(soup.prettify())
            except:
                print("Domain Not Availabe")
                pass

            try:
                job_com1 = soup.find('div', attrs={'class': "container"})
                for job_com2 in job_com1.find_all('section', attrs={'class': "jobs"}):
                    for job_com3 in job_com2.find_all('ul'):
                        job_com4 = job_com3.find('a')["href"]
                        job_com = self._main_url+job_com4
                        Job_com0.append(job_com)
                        print(job_com)
            except:
                pass

            #Pagination----------------------------------------------------
            try:
                page1 = job_com1.find('nav', attrs={'class': "pagination"})
                page2 = page1.find('span', attrs={'class': "next"})
                page3 = page2.find('a')["href"]
                page = self._main_url+page3
                print("page_link", page)
                self.page_link = page
            except:
                break
            print(Job_com0)

        # df = pd.DataFrame(links)
        # df.to_csv('file22.csv', index=False, header=False)
        #
            # self.read_city_main_urls(Job_cat0, state)



    def test(self):
        # self.driver_load()
        link = 'https://weworkremotely.com/categories/remote-programming-jobs'
        # self.driver.get(link)
        content = requests.get(link, timeout=30)
        soup = BeautifulSoup(content.text, features="lxml")
        # soup = BeautifulSoup(self.driver.page_source, features="lxml")
        print(soup.prettify())



if __name__ == '__main__':
    scraper = wwr()
    # scraper.get_all_company_links()
    scraper.get_job_cat()
    # scraper.read_city_main_urls()
    # scraper.test()
    # scraper.Post_request()


