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


class jobsdb:
    def __init__(self):
        # self.helper = Helper()
        self.driver = None
        self.wait = None
        self.page_count = 1
        self.post_count = 1
        self._main_url = "https://sg.jobsdb.com"
        self._all_jobs_url = "https://sg.jobsdb.com/findjobs"
        self.platform = "https://sg.jobsdb.com/findjobs"
        self.output = pd.DataFrame()
        self.chromedriver_path = os.environ.get("CHROME_DRIVER")
        self.S3_BUCKET_URL = os.environ.get("S3_BUCKET_URL")
        # self.current_page = None



        # self.db_model = BaseDBModel()
    def driver_load(self):
        options = webdriver.ChromeOptions()
        options.headless = True
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

    def create_final_output(self, soup, iframe_link, p_link, Job_Id0, loc_cat, state1, sub_cat, m_cat):
    # def create_final_output(self, soup, iframe_link):
        # job_ad_url = link
        # Job_ID = link.split("/")[5]
        Job_Id = ''
        Company_Name = ''
        Job_Title = ''
        Job_Location = ''
        State = ''
        Company_Address = ''
        Carrer_page_url = ''
        Role_Categories = ''
        Functional_Area = ''
        Job_Description = ''
        Job_link = ''


        Job_Id_list = []
        Company_Name_list = []
        Job_Title_list = []
        Job_Location_list = []
        State_list = []
        Company_Address_list = []
        Carrer_page_url_list = []
        Role_Categories_list = []
        Functional_Area_list = []
        Job_Description_list = []
        Job_link_list = []



        try:
            Job_Id = Job_Id0
            print("unique_ID*************"+Job_Id)
        except:
            Job_Id = None

        try:
            Job_Location = loc_cat
            print("Job_Location*************"+Job_Location)
        except:
            Job_Location = None

        try:
            State = state1
            print("State*************"+State)
        except:
            State = None

        try:
            Functional_Area = sub_cat
            print("Functional_Area*************"+Functional_Area)
        except:
            Functional_Area = None

        try:
            Role_Categories = m_cat
            print("Role_Categories*************"+Role_Categories)
        except:
            Role_Categories = None

        try:
            Carrer_page_url = iframe_link
            print("Carrer_page_url*************"+Carrer_page_url)
        except:
            Carrer_page_url = None

        try:
            Job_link = p_link
            print("Job_link*************"+Job_link)
        except:
            Job_link = None

        try:
            Title_Content1 = soup.find('div', attrs={'class': 'job-details-page content-container -wide grid-container -two-columns'})
            Title_Content2 = Title_Content1.find('div', attrs={'class': 'job-view-content grid-content'})
            Title_Content3 = Title_Content2.find('div', attrs={'id': 'job-info-container'})
            Job_Title1 = Title_Content3.find('h3', attrs={'class': 'job-title heading-xxlarge'})
            Job_Title = self.clean_soup(Job_Title1)
            print("Job_Title*************" + Job_Title)
        except:
            Job_Title = None

        try:
            Company_Name1 = Title_Content3.find('div', attrs={'id': 'company-location-container'})
            Company_Name2 = Company_Name1.find('span', attrs={'class': 'company'})
            Company_Name = self.clean_soup(Company_Name2)
            print("Company_Name*************" + Company_Name)
        except:
            Company_Name = None

        try:
            Company_Address1 = Title_Content3.find('div', attrs={'id': 'company-location-container'})
            Company_Address = Company_Address1.find('span', attrs={'class': 'location'})
            Company_Address = self.clean_soup(Company_Address)
            print("Company_Address*************" + Company_Address)
        except:
            Company_Address = None

        Job_Description = ""
        try:
            for Job_Description1 in Title_Content2.find_all('div', attrs={'id': 'job-description-container'}):
                print("DES===>>",Job_Description1)
                Job_Description = self.clean_soup(Job_Description1)
                print(Job_Description)
        except:
            Job_Description = None


        # try:
        #     apply_details1 = soup.find('div', attrs={'class': 'job-details-page content-container -wide grid-container -two-columns'})
        #     apply_details2 = apply_details1.find('div', attrs={'class': 'job-view-content grid-content'})
        #     apply_details3 = apply_details2.find('div', attrs={'id': 'job-view-actions-container'})
        #     apply_details4 = apply_details3.find('div', attrs={'class': 'quick-apply-container'})
        #     apply_details5 = apply_details4.find('span')
        #     apply_details6 = apply_details5["data-jqa"]
        #     print("job_details",apply_details6)
        # except:
        #     print("***********************----------------------***********************")
        #
        # try:
        #     career_url = soup.find('div', attrs={'id': "jobseeker-apply-container"})
        #     print(career_url)
        #     career_url1 = career_url.find('body')
        #     print("career_url", career_url1)
        # except:
        #     print("/./././/./././././././././/././/././././")



        #csv_columns
        Job_Id_list.append(Job_Id)
        Company_Name_list.append(Company_Name)
        Job_Title_list.append(Job_Title)
        Job_Location_list.append(Job_Location)
        State_list.append(State)
        Company_Address_list.append(Company_Address)
        Carrer_page_url_list.append(Carrer_page_url)
        Role_Categories_list.append(Role_Categories)
        Functional_Area_list.append(Functional_Area)
        Job_Description_list.append(Job_Description)
        Job_link_list.append(Job_link)



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
            # 'job_source': [self.naukri_source_name],
            'unique_key': Job_Id_list,
            'job_title': Job_Title_list,
            'company_name': Company_Name_list,
            'company_address': Company_Address,
            'career_page_url': Carrer_page_url,
            'extra_job_location_details': Job_Location_list,
            'location': State_list,
            # 'district': Job_State,
            'job_link': Job_link_list,
            'job_description': Job_Description_list,
            'category': Role_Categories_list,
            'job_email': ['jobeka.in@incubatelabs.com'],
            'company_email': ['jobeka.in@incubatelabs.com']
        }

        df = pd.DataFrame(post_data)
        if os.path.isfile('jobsdb.csv'):
            df.to_csv("jobsdb.csv", mode='a', header=False)
        else:
            df.to_csv("jobsdb.csv")




    def post_request(self, post_links, loc_cat, state1, sub_cat, m_cat):
    # def post_request(self):
    #     post_links = {'98f976c2a0f97b2e9b03589973e9fc91': 'https://sg.jobsdb.com/job/Finance-Assistant-98f976c2a0f97b2e9b03589973e9fc91?from_url=https%3A%2F%2Fsg.jobsdb.com%2FAccount-jobs-in-Bugis&sl=Bugis&sol_srt=20bff909-0574-45be-bd15-9b55e0aaf77a&sp=serp&sponsored=false&sq=Account&sr=1&tk=8mKgL4AoG8wnK9nWWwA7-FTZ45WCgE1g2yScSdlqu'}
    #     sub_cat = "Bugis"
    #     main_cat = "Account"
        self.driver_load()
        print("next===> Post_request")
        local_count = 0
        for key in post_links:
            p_link = post_links[key]
            print(key,"...",p_link)
            Job_Id0 = key
            print("Job_Post_Count======", self.post_count)
            self.post_count += 1
            local_count += 1
            if local_count == 5:
                sleep = random.randint(10, 15)
                time.sleep(sleep)
                local_count = 0
            else:
                pass
            # try:
            #     sleep = random.randint(3, 5)
            #     time.sleep(sleep)
            #     content = requests.get(p_link, timeout=30)
            #     soup = BeautifulSoup(content.text, features="lxml")
            #     # print(soup.prettify())
            # except:
            #     pass
            self.driver.get(p_link)
            sleep = random.randint(3, 5)
            time.sleep(sleep)
            Url_button = self.driver.find_elements_by_xpath('//*[@id="job-view-actions-container"]/div[1]/div/span')[0]
            Url_button.click()
            WebDriverWait(self.driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '/html/body/div/iframe')))
            try:
                iframe_link_element = self.driver.find_element_by_tag_name('iframe')
                # print('iframe_link_element', iframe_link_element)
                iframe_link = iframe_link_element.get_attribute('src')
            except:
                iframe_link = None

            print('iframe_link', iframe_link)
            # print(self.driver.page_source)
            self.driver.switch_to_default_content()

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            # self.driver.close()
            self.create_final_output(soup, iframe_link, p_link, Job_Id0 , loc_cat, state1, sub_cat, m_cat)
            # self.create_final_output(soup, iframe_link)


            # self.make_output()



    def read_job_page_urls(self, sub_cat_link_loc_dict, state1, sub_cat, m_cat):
        for key in sub_cat_link_loc_dict:
            s_link = sub_cat_link_loc_dict[key]
            print(key,"...",s_link)
            loc_cat = key
            while self.page_count < 10000:
                try:
                    content = requests.get(s_link, timeout=30)
                    soup = BeautifulSoup(content.text, features="lxml")
                except:
                    print("Domain Not Availabe")
                    pass
                sleep = random.randint(2, 5)
                time.sleep(sleep)

                post_links ={}
                job_page = soup.find('div', attrs={'class': re.compile("^search-results-page content-container -wide grid-container -three-columns")})
                job_page1 = job_page.find('div', attrs={'class': re.compile("^serp-content grid-content")})
                for job_page2 in job_page1.find_all('div', attrs={'id': "jobresults"}):
                    for job_page3 in job_page2.find_all('div', attrs={'class': "job-container result organic-job"}):
                        job_id1 = job_page3["id"]
                        job_id = job_id1.replace("r_", "")
                        print("JOB_ID-----",job_id)
                        job_post_link1 = job_page3.find('a', attrs={'class': "job-item"})
                        job_post_link2 = job_post_link1["href"]
                        job_post_link3 = self._main_url+job_post_link2
                        print("POST_LINK-----",job_post_link3)
                        post_links[job_id] = job_post_link3

                sleep = random.randint(45, 50)
                time.sleep(sleep)
                self.post_request(post_links, loc_cat, state1, sub_cat, m_cat)
                self.driver.quit()
                try:
                    print("PAGINATION>>>")
                    page = job_page1.find('div', attrs={'class': "multi-pages-pagination pagination-container"})
                    page1 = page.find('a', attrs={'class': "next-page-button"})
                    page2 = page1["href"]
                    s_link = self._main_url+page2
                    print("Next_Page_URL===>", s_link)
                except:
                    break

    def read_sub_category_loc_urls(self, sub_cat_link_dict, m_cat):
        for key in sub_cat_link_dict:
            s_link = sub_cat_link_dict[key]
            print(key,"...",s_link)
            sub_cat = key
            try:
                content = requests.get(s_link, timeout=30)
                soup = BeautifulSoup(content.text, features="lxml")
            except:
                print("Domain Not Availabe")
                pass
            sleep = random.randint(5, 7)
            time.sleep(sleep)

            job_sat_loc = soup.find('div', attrs={'class': "browse-jobs-page content-container -wide -tall"})
            for job_sat_loc1 in job_sat_loc.find_all('div', attrs={'id': "browse-keyword-and-locations"}):
                print("***>>3<<******REQUEST===>>Sub_Category_location***************")
                state = job_sat_loc1.find('h2', attrs={'class': "heading-medium browse-heading"})
                state1 = state.text
                print("state-------------------------------------------------------------------------------------------------", state1)
                # sub_cat_loc_link = []
                sub_cat_link_loc_dict = {}
                for job_sat_loc2 in job_sat_loc1.find_all('div', attrs={'class': re.compile('^browse-link')}):
                    job_sat_loc3 = job_sat_loc2.find('a', attrs={'class': "-link-highlight"})
                    job_sat_loc_name = job_sat_loc3.text
                    print(job_sat_loc_name)
                    job_sat_loc_link1 = job_sat_loc3["href"]
                    job_sat_loc_link2 = self._main_url + job_sat_loc_link1
                    print(job_sat_loc_link2)
                    sub_cat_link_loc_dict[job_sat_loc_name] = job_sat_loc_link2
                print(sub_cat_link_loc_dict)

                self.read_job_page_urls(sub_cat_link_loc_dict, state1, sub_cat, m_cat)



    def read_main_category_urls(self, m_links):
        for m_link in m_links:
            print("Main_Category  ==> " + m_link)
            try:
                m_cat = re.search(r"(?<=findjobs/)\w+", m_link).group(0)
                print("Main_category*************" + m_cat)
            except:
                m_cat = None
            try:
                content = requests.get(m_link, timeout=30)
                soup = BeautifulSoup(content.text, features="lxml")
            except:
                print("Domain Not Availabe")
                pass

            job_sat = soup.find('div', attrs={'class': "browse-jobs-page content-container -wide -tall"})
            for job_sat1 in job_sat.find_all('div', attrs={'id': "browse-keywords"}):
                print("***>>2<<******REQUEST===>>Sub_Category***************")
                sub_cat_link_dict = {}
                for job_sat2 in job_sat1.find_all('div', attrs={'class': re.compile('^browse-link')}):
                    job_sat_name = job_sat2.find('a', attrs={'class': "-link-highlight"}).text
                    print(job_sat_name)
                    job_loc_link = job_sat2.find('a', attrs={'class': re.compile('^heading-xsmall -link-muted')})
                    job_loc_link2 = job_loc_link["href"]
                    job_loc_link3 = self._main_url + job_loc_link2
                    print(job_loc_link3)
                    sub_cat_link_dict[job_sat_name] = job_loc_link3
                print(sub_cat_link_dict)

                self.read_sub_category_loc_urls(sub_cat_link_dict, m_cat)


    def get_all_jobs_urls(self, url):
        print(url)
        try:
            content = requests.get(url, timeout=30)
            soup = BeautifulSoup(content.text, features="lxml")
        except:
            print("Domain Not Availabe")
            pass

        job_cat = soup.find('div', attrs={'class': "browse-jobs-page content-container -wide -tall"})
        for job_cat1 in job_cat.find_all('div', attrs={'id': "browse-categories"}):
            print("***>>1<<***REQUEST===>>Main_Category***********")
            m_links = []
            for job_cat2 in job_cat1.find_all('a', attrs={'class': re.compile('^-link-highlight')}):
                job_cat3 = (job_cat2['href'])
                job_cat4 = self._main_url + job_cat3

                m_links.append(job_cat4)
                print(job_cat4)
            print(m_links)

            self.read_main_category_urls(m_links)


    def input_url_download(self):
        url = self._all_jobs_url
        self.get_all_jobs_urls(url)
        print("one")

    def test(self):
        # self.driver_load()
        link = "https://apply-sg.jobsdb.com/apply/xd?hostOrigin=https%3A%2F%2Fsg.jobsdb.com"
        # self.driver.get(link)
        content = requests.get(link, timeout=30)
        # soup = BeautifulSoup(self.driver.page_source, features="lxml")
        soup = BeautifulSoup(content.text, features="lxml")
        print(soup.prettify())



if __name__ == '__main__':
    scraper = jobsdb()
    scraper.input_url_download()
    # scraper.read_city_main_urls()
    # scraper.test()
    # scraper.post_request()


