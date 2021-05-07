from dotenv import load_dotenv
import os.path
from os import path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
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


class JobStreet:
    def __init__(self):
        # self.helper = Helper()
        self.driver = None
        self.wait = None
        self.page_count = 1
        self.post_count = 1
        self._main_url = "https://www.jobstreet.com.sg"
        # self._main_url = "https://www.jobstreet.com.my"
        self._all_jobs_url = "https://www.jobstreet.com.sg/en/job-search/find-specialization?sal=1#"
        # self._all_jobs_url = "https://www.jobstreet.com.my/en/job-search/find-specialization?sal=1#"
        self.platform = "https://www.jobstreet.com.sg"
        self.output = pd.DataFrame()
        self.chromedriver_path = os.environ.get("CHROME_DRIVER")
        self.prefix = ['ltd', 'plc', 'pvt', 'private', 'ceylon']
        self.S3_BUCKET_URL = os.environ.get("S3_BUCKET_URL")


        # self.current_page = None
        # self.Job_Id_list = []
        # self.Job_Title_list = []
        # self.Company_Name_list = []
        # self.Company_Logo_list = []
        # self.City_list = []
        # self.Salary_des_list = []
        # self.Job_Posted_list = []
        # self.Job_Expire_list = []
        # self.Job_Highlights_list = []
        # self.Job_Description_list = []
        # self.Role_list = []
        # self.Job_education_list = []
        # self.Job_Experence_list= []
        # self.Job_Type_list = []
        # self.Functional_Area_list = []
        # self.Company_Info_list = []
        # self.Registration_No_list = []
        # self.Company_Size_list = []
        # self.Average_Processing_Time_list = []
        # self.Industry_list = []
        # self.Benefits_list = []




        self.Links_list1 =[]

        # self.Job_poster_list1 = []
        # self.Links_list1 = []




    def driver_load(self):
        # options = webdriver.ChromeOptions()
        # options.headless = True
        self.driver = webdriver.Chrome(executable_path="/home/kishanthan/Desktop/Amazon/amozon_fetcher/source/chromedriver",
                                       keep_alive=True)
        # self.driver = webdriver.Chrome(executable_path="/home/ilabs/Desktop/naukri/source/chromedriver",
        #                                keep_alive=True)
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
        Job_Id_list = []
        Job_Title_list = []
        Company_Name_list = []
        Company_Logo_list = []
        City_list = []
        Salary_des_list = []
        Job_Posted_list = []
        Job_Expire_list = []
        Job_Highlights_list = []
        Job_Description_list = []
        Role_list = []
        Job_education_list = []
        Job_Experence_list = []
        Job_Type_list = []
        Functional_Area_list = []
        Company_Info_list = []
        Registration_No_list = []
        Company_Size_list = []
        Average_Processing_Time_list = []
        Industry_list = []
        Benefits_list = []
        Links_list1 = []



        # try:
        #     details = soup.find('script', attrs={'type': 'application/ld+json'})
        #     detail_json = json.loads(details.text)
        #     try:
        #         Job_Posted = detail_json["datePosted"]
        #         print(Job_Posted)
        #     except:
        #         Job_Posted = None
        #     try:
        #         Job_Expire = detail_json["validThrough"]
        #         print(Job_Expire)
        #     except:
        #         Job_Expire = None
        # except:
        #     pass


        try:
            Job_Id = re.search(r"(?<=-sg-job-).*?(?=&sectionRank)", link).group(0)
            try:
                Job_Id = Job_Id.replace("?","")
            except:
                pass
            print("unique_ID*************"+Job_Id)
        except:
            Job_Id = None


        # print(c_url)
        # try:
        #     City = re.search(r"(?<=-in-)\w+", c_url).group(0)
        #     print("city*************"+City)
        # except:
        #     City = None


        Job_Expire = None


        try:
            Job_Title1 = soup.find('div', attrs={'data-automation': 'detailsTitle'})
            Job_Title = Job_Title1.find('h1', attrs={'class': re.compile('^FYwKg C6ZIU_')}).text
            Job_Title = self.clean_soup(Job_Title)
            print(Job_Title)
        except:
            Job_Title = None


        try:
            Company_Name1 = soup.find('div', attrs={'data-automation': 'detailsTitle'})
            Company_Name = Company_Name1.find('span', attrs={'class': re.compile('^FYwKg _1GAuD C6ZIU_')})
            # Company_Name = Company_Name.find('a').text
            Company_Name = self.clean_soup(Company_Name)
            print(Company_Name)
        except:
            Company_Name = None


        try:
            City2 = soup.find('div', attrs={'class': re.compile('^FYwKg _20Cd9 _3qNSL_')})
            City1 = City2.find('div', attrs={'class': re.compile('^FYwKg d7v3r _3122U_')})
            City = City1.find('div', attrs={'class': 'FYwKg _2cWXo'})
            # Company_Name = Company_Name.find('a').text
            City = self.clean_soup(City)
            print(City)
        except:
            City = None


        try:
            Company_Logo2 = soup.find('div', attrs={'data-automation': 'jobDetailsHeader'})
            Company_Logo1 = Company_Logo2.find('img', attrs={'class': re.compile('^_6CW9R_')})
            Company_Logo = Company_Logo1['src']
            Company_Logo = self.clean_soup(Company_Logo)
            print(Company_Logo)
        except:
            Company_Logo = None


        # try:
        #     if soup.find('div', attrs={'id': 'root'}):
        #         Job_Experence = soup.find('div', attrs={'class': 'exp'}).text
        #         Job_Experence = self.clean_soup(Job_Experence)
        #         print(Job_Experence)
        # except:
        #     Job_Experence = None

        try:
            descri = []
            Salary_des3 = soup.find('div', attrs={'class': re.compile('^FYwKg _20Cd9 _3qNSL_')})
            Salary_des2 = Salary_des3.find('div', attrs={'class': re.compile('^FYwKg d7v3r _3122U_')})
            for Salary_des1 in Salary_des2.find_all('div', attrs={'class': re.compile('^FYwKg _11hx2_')}):
                # Company_Name = Company_Name.find('a').text
                Salary_des1 = self.clean_soup(Salary_des1)
                descri.append(Salary_des1)
            count1 = len(descri)
            print(count1)
            # print(descri)
            if count1 > 2:
                Salary_des = descri[1]
                print(Salary_des)
                try:
                    Job_Posted1 = descri[2].replace("Posted on ", "")
                    print(Job_Posted1)
                    format_closing_date = '%d-%b-%y'
                    datetime_obj = datetime.datetime.strptime(Job_Posted1, format_closing_date)
                    Job_Posted = datetime_obj.date()
                    print(Job_Posted)
                except:
                    Job_Posted = None
            else:
                Salary_des = None
                try:
                    Job_Posted1 = descri[1].replace("Posted on ", "")
                    print(Job_Posted1)
                    format_closing_date = '%d-%b-%y'
                    datetime_obj = datetime.datetime.strptime(Job_Posted1, format_closing_date)
                    Job_Posted = datetime_obj.date()
                    print(Job_Posted)
                except:
                    Job_Posted = None

        except:
            Salary_des = None
            Job_Posted = None
            print("No Salary details")



        try:
            Job_Description0 = ""
            Job_Description1 = soup.find('div', attrs={'id': 'contentContainer'})
            # Job_Description2 = Job_Description1.find_all('div', attrs={'class': re.compile('^FYwKg d7v3r _3BZ6E_')})
            Job_Description3 = Job_Description1.find('div', attrs={'data-automation': 'jobDescription'})
            for Job_Description4 in Job_Description3.find('div', attrs={'class': 'FYwKg'}):
                Job_Description5 = self.clean_soup(Job_Description4)
                Job_Description0 += (Job_Description5+ '\n')
            Job_Description = str(Job_Description0)
            print(Job_Description)
        except:
            Job_Description = None


        try:
            Job_Highlights0 = ""
            Job_Highlights1 = soup.find('div', attrs={'id': 'contentContainer'})
            # Job_Highlights2 = Job_Highlights1.find('div', attrs={'class': 'FYwKg _2mOt7_0 _3gJU3_0 _1yPon_0 _36Yi4_0 _1WtCj_0 FLByR_0 _2QIfI_0'})
            Job_Highlights3 = Job_Highlights1.find('div', attrs={'data-automation': 'job-details-job-highlights'})
            for Job_Highlights4 in Job_Highlights3.find('ul', attrs={'class': re.compile('^FYwKg _302h6 d7v3r UJoTY_')}):
                Job_Highlights5 = self.clean_soup(Job_Highlights4)
                Job_Highlights0 += (Job_Highlights5+ '\n')
            Job_Highlights = str(Job_Highlights0)
            print(Job_Highlights)
        except:
            Job_Highlights = None


        _dict_job_details = {}
        try:
            set = soup.find('div', attrs={'id': "contentContainer"})
            set2 = set.find('div', attrs={'class': re.compile('^FYwKg d7v3r _3BZ6E_')})
            # set2 = set1.find('div', attrs={'class': "FYwKg _2cWXo _194Ob _3gDk-_6"})
            for set3 in set2.find_all('div', attrs={'class': re.compile('^FYwKg _2cWXo _194Ob _3gDk-_')}):
                for set4 in set3.find_all('div', attrs={'class': re.compile('^FYwKg d7v3r _2uGS9_')}):
                    group = []
                    for set5 in set4.find_all('div', attrs={'class': re.compile('^FYwKg zoxBO_0')}):
                        set5 = self.clean_soup(set5)
                        # print(set5)
                        group.append(set5)
                    res_dct = {group[i]: group[i+1] for i in range(0, len(group), 2)}
                    # print(res_dct)
                    _dict_job_details.update(res_dct)
            # print(_dict_job_details)
        except:
            pass

        try:
            Role = _dict_job_details["Career Level"]
            print(Role)
        except:
            Role = None
        try:
            Job_education = _dict_job_details["Qualification"]
            print(Job_education)
        except:
            Job_education = None
        try:
            Job_Experence = _dict_job_details["Years of Experience"]
            print(Job_Experence)
        except:
            Job_Experence = None
        try:
            Job_Type = _dict_job_details["Job Type"]
            print(Job_Type)
        except:
            Job_Type = None
        try:
            Functional_Area = _dict_job_details["Job Specializations"]
            print(Functional_Area)
        except:
            Functional_Area = None
        try:
            Registration_No = _dict_job_details["Registration No."]
            print(Registration_No)
        except:
            Registration_No = None
        try:
            Company_Size = _dict_job_details["Company Size"]
            print(Company_Size)
        except:
            Company_Size = None
        try:
            Average_Processing_Time = _dict_job_details["Average Processing Time"]
            print(Average_Processing_Time)
        except:
            Average_Processing_Time = None
        try:
            Industry = _dict_job_details["Industry"]
            print(Industry)
        except:
            Industry = None
        try:
            Benefits = _dict_job_details["Benefits & Others"]
            print(Benefits)
        except:
            Benefits = None



        try:
            Company_Info0 = ""
            Company_Info1 = soup.find('div', attrs={'id': 'contentContainer'})
            # Company_Info2 = Company_Info1.find('div', attrs={'class': re.compile('^FYwKg _2mOt7_0 _3gJU3_0 _1yPon_0 _36Yi4_0 _1WtCj_0 FLByR_0 _2QIfI_0')})
            # print(Company_Info2)
            Company_Info2 = Company_Info1.find_all('div', attrs={'class': re.compile('^vDEj0_')})
            Company_Info3 = self.clean_soup(Company_Info2[1])
            Company_Info = Company_Info3
            print(Company_Info)
        except:
            Company_Info = None


        #csv_columns
        Job_Id_list.append(Job_Id)
        Job_Title_list.append(Job_Title)
        Company_Name_list.append(Company_Name)
        Company_Logo_list.append(Company_Logo)
        City_list.append(City)
        Salary_des_list.append(Salary_des)
        Job_Posted_list.append(Job_Posted)
        Job_Expire_list.append(Job_Expire)
        Job_Highlights_list.append((Job_Highlights))
        Job_Description_list.append(Job_Description)
        Role_list.append(Role)
        Job_education_list.append(Job_education)
        Job_Experence_list.append(Job_Experence)
        Job_Type_list.append(Job_Type)
        Functional_Area_list.append(Functional_Area)
        Company_Info_list.append(Company_Info)
        Registration_No_list.append(Registration_No)
        Company_Size_list.append(Company_Size)
        Average_Processing_Time_list.append(Average_Processing_Time)
        Industry_list.append(Industry)
        Benefits_list.append(Benefits)



        Links_list1.append(link)



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
            'city': City_list,
            'job_salary': Salary_des_list,
            'start_at': Job_Posted_list,
            'closing_date': Job_Expire_list,
            'highlights': Job_Highlights_list,
            'job_description': Job_Description_list,
            'role': Role_list,
            'educational_requirements': Job_education_list,
            'job_Experence': Job_Experence_list,
            'job_type': Job_Type_list,
            'functional_area': Functional_Area_list,
            'company_info' : Company_Info_list,
            'registration_No': Registration_No_list,
            'company_size': Company_Size_list,
            'average processing time': Average_Processing_Time_list,
            'indusrty type': Industry_list,
            'benefits': Benefits_list,

            'job_link': Links_list1,





            # 'job_description': self.html_job_description_list,
         #    'role_categories': self.Role_Categories_list,
         # 'industry_type' : self.Industry_Type_list,
         #
         #    'key_skills' : self.Key_Skills_list

            # 's3_url_company_logo': s3_url_company_logo,
            # 's3_url_job_poster': s3_url_job_poster

        }
        df = pd.DataFrame(post_data)
        if os.path.isfile('Jobstreet_final.csv'):
            df.to_csv("Jobstreet_final.csv", mode='a', header=False)
        else:
            df.to_csv("Jobstreet_final.csv")

        print("==================Scraped========================")



    def Post_request(self,post_urls):
        print("next===> Post_request")
        # self.driver_load()
        # df = pd.read_csv('Test_dummy.csv')
        # post_urls = df['post_url'].tolist()
        for link in post_urls:
            print("************", link)
            try:
                # self.driver.get(link)
                sleep = random.randint(3, 5)
                time.sleep(sleep)
                # content1 = requests.get(self.current_page, headers=headers, timeout=30)
                # soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                # print(soup.prettify())
                content = requests.get(link, timeout=30)
                soup = BeautifulSoup(content.text, features="lxml")
                print("POST_COUNT======>  ", self.post_count)
                self.post_count += 1
                # print(soup.prettify())

            except:
                pass
            self.create_final_output(soup, link,)
            # self.make_output()
        # self.driver.quit()


    def read_city_main_urls(self, set_list):
        # df = pd.read_csv('Job_special1.csv')
        # set_list = df['urls'].tolist()
        # print(state)
        print("===============================================================")
        print(set_list)
        self.driver_load()

        for c_link in set_list:
            print("JOBSTREET  ==> " + c_link)
            count = 1
            while count < 1000:
                print("--------------------", c_link)
                self.driver.get(c_link)
                sleep = random.randint(5, 7)
                time.sleep(sleep)
                print("Link________Page_count==", self.page_count)
                # content1 = requests.get(self.current_page, headers=headers, timeout=30)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                try:
                    post = soup.find('div', attrs={'class': re.compile("^FYwKg _2H6VN_")})
                except:
                    pass
                try:
                    post1 = post.find('div', attrs={'data-automation': "jobListing"})
                except:
                    pass
                post_urls = []
                try:
                    for post2 in post1.find_all('div', attrs={'class': re.compile("^FYwKg _17IyL_")}):
                        for post3 in post2.find_all('div', attrs={'class': re.compile("^FYwKg _31UWZ fB92N_")}):
                            for post4 in post3.find_all('h1', attrs={'class': re.compile("^FYwKg _1GAuD C6ZIU_")}):
                                for post5 in post4.find_all('a', attrs={'class': re.compile("^DvvsL_")}):
                                    post5 = self._main_url+post5["href"]
                                    post_urls.append(post5)
                                    self.Links_list1.append(c_link)
                                    print(post5)
                except:
                    pass
                #Next_page_scraping---------------------------
                self.Post_request(post_urls)
                #Pagination=========================================================================================================
                try:
                    print("y=======================e==================s")
                    # self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="jobList"]/div/div[4]/div/a[2]'))).click()
                    # sleep = random.randint(3, 5)
                    # time.sleep(sleep)
                    next = post.find('div', attrs={'class': re.compile("^FYwKg _20Cd9 _36UVG_")})
                    next1 = next.find('div', attrs={'class': re.compile("^FYwKg _2cWXo _1QYmq")})
                    next_url = []
                    try:
                        for next2 in next1.find_all('a', attrs={'class': re.compile("^FYwKg _2mOt7_")}):
                            next2 = self._main_url+next2["href"]
                            next_url.append(next2)
                            print(next_url)
                        Total_urls = len(next_url)
                        print("////////////////////",Total_urls)
                        if Total_urls == 2:
                            next_url.pop(0)
                            next_url = str(next_url)[1:-1]
                            next_url = next_url.replace("'", "")
                            c_link = next_url
                        else:
                            next_url = str(next_url)[1:-1]
                            next_url = next_url.replace("'", "")
                            page_number = re.search(r"(?<=-jobs/).*?(?=/)", next_url).group(0)
                            page_number = int(page_number)
                            print("page_number=", page_number)
                            if page_number < 3:
                                c_link = next_url
                            else:
                                break
                                # next_url.pop(0)
                        # next_url = ", ".join(repr(e) for e in next_url)
                        # next_url = str(next_url)[1:-1]
                        # next_url = next_url.replace("'", "")
                        # try:
                        #     if not next_url:
                        #         break
                        #     c_link = next_url
                        # except:
                        #         break

                        self.page_count += 1

                    except:
                        pass
                except:
                    break
#-----------------------------------------------------------------------
                # post_csv = {
                #     'post_url': self.Job_poster_list1,
                #     'Job_specialization': self.Links_list1,
                # }
                # df = pd.DataFrame(post_csv)
                # df.to_csv("Test_Jobstreet.csv")


#--------------------------------------------------------------------------





    def get_all_jobs_urls(self, url):
        print(url)
        self.driver_load()
        links = []
        try:
            self.driver.get(url)
            # content = requests.get(url, timeout=30)
            # soup = BeautifulSoup(content.text, features="lxml")
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            # print(soup.prettify())

        except:
            print("Domain Not Availabe")
            pass


        for job_set in soup.findAll('div', attrs={'id': "rCon"}):
            for job_set1 in job_set.find_all('ul', attrs={'class': "onerow"}):
                for job_set2 in job_set1.find_all('li', attrs={'class': "halfdent"}):
                    for job_set3 in job_set2.find_all('a'):
                        job_set3 = job_set3["href"]
                        links.append(job_set3)

        print("*************************************")

            # links = []
            # for job_cities2 in job_cities1.find_all('a', attrs={'href': re.compile('^https')}):
            #     job_city = (job_cities2['href'])
            #     links.append(job_city)
            #     print(job_city)


            # print(links)
            # state = links.pop(0)
            # print("capital"+state)
            # links.pop(0)
        # print(links)
        # df = pd.DataFrame(links)
        # df.to_csv('Job_special1.csv', index=False)

        self.read_city_main_urls(links)


    def input_url_download(self):
        url = self._all_jobs_url
        self.get_all_jobs_urls(url)
        print("one")

    def test(self):
        self.driver_load()
        link = 'https://www.jobstreet.com.sg/en/job-search/find-specialization?sal=1#'
        self.driver.get(link)
        # content = requests.get(link, timeout=30)
        soup = BeautifulSoup(self.driver.page_source, features="lxml")
        print(soup.prettify())



if __name__ == '__main__':
    scraper = JobStreet()
    scraper.input_url_download()
    # scraper.read_city_main_urls()
    # scraper.test()
    # scraper.Post_request()


