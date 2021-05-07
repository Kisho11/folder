import traceback

from bs4 import BeautifulSoup
import requests
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from dotenv import load_dotenv
import traceback

load_dotenv()


class BdjobsScraper:
    def __init__(self):
        self.category_count = 0
        self.current_page = 1
        self.current_job_category = None
        self.chrome_driver_path = os.environ.get("CHROME_DRIVER")
        self.platform_id = os.environ.get("COMMON_PLATFORM_ID")
        self.bdjobs_source_name = os.environ.get("BDJOBS_JOB_SOURCE_NAME")
        self.job_link = None

    def driver_load(self):
        # options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        self.driver = webdriver.Chrome(executable_path="/home/ilabs/Desktop/AMD/chromedriver_linux64/chromedriver", keep_alive=True)
        # options = options
        self.wait = WebDriverWait(self.driver, 20, poll_frequency=1)
        return True

    def load_categories(self):
        url = 'https://www.bdjobs.com/'
        content = requests.get(url)
        soup = BeautifulSoup(content.text, features="lxml")
        # GET CATEGORY LIST
        category_list_div = soup.find('div', attrs={'class': "category-list padding-mobile functional active"})
        category_list = category_list_div.find_all('li')

        return category_list

    def get_jobs(self, category_list):
        for div in category_list:
            # category_list.pop(0)
            self.driver_load()
            link = div.find("a")
            self.current_job_category = link.text
            link = link["href"]
            link = "https:" + link
            print(link)
            self.driver.get(link)
            print(link)
            self.current_page = 1
            self.page_count = 2
            try:
                page_count = 1
                while page_count <= self.page_count:
                    current_page = self.current_page
                    soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    try:
                        self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="topPagging"]')))
                        print("Loaded...")
                    except Exception as error:
                        print('Not Loaded...', error)
                    # self.job_list_method(soup)
                    pagination_list = soup.find_all('div', attrs={'class': 'pagination'})
                    pagination_div = pagination_list[0]
                    li_list = pagination_div.find_all('li')
                    print("li_list=",li_list)
                    _dict_pages = {}
                    index = 1
                    for li in li_list:
                        page_no = li.text
                        page_no = page_no.replace('...', '')
                        page_no = page_no.strip()
                        print("page_no",page_no)
                        _dict_pages[page_no] = index
                        self.page_count = int(page_no)
                        index += 1
                    next_page = _dict_pages[str(current_page + 1)]
                    self.current_page += 1
                    print('try to click... Page:', next_page)
                    try:
                        self.wait.until(EC.element_to_be_clickable(
                            (By.XPATH, '//*[@id="topPagging"]/ul/li[' + str(next_page) + ']/a'))).click()
                        print("pagination================================")
                    except Exception as error:
                        print('111', error)
                    time.sleep(5)
            except Exception as error:
                print('222', error)

            try:
                self.driver.close()
                print('Web driver closed...')
            except:
                pass

    def job_list_method(self, soup):
        self.wait.until(EC.presence_of_element_located((By.ID, 'jobList')))
        category_list_div = soup.find('div', attrs={'id': "jobList"})
        job_list = category_list_div.find_all('div', attrs={"class": "col-md-12"})
        for d in job_list:
            # self.job_ID = []
            # self.job_title_list_1 = []
            # self.Job_vacancy_1 = []
            # self.company_name_1 = []
            # self.job_context_1 = []
            # self.job_responsibility_1 = []
            # self.job_status_1 = []
            # self.job_work_1 = []
            # self.job_edu_req_1 = []
            # self.job_add_req_1 = []
            # self.job_location_1 = []
            # self.job_salary_1 = []
            # self.job_compenstation_1 = []
            # self.job_summary_1 = []
            # self.job_information_1 = []
            # self.job_exe_req_1 = []
            # self.company_logo = []

            self.category_count += 1
            try:
                category_list_new = d.find('div', attrs={"class": "job-title-text"})
                if not category_list_new:
                    category_list_new = d.find('div', attrs={"class": "title"})
            except:
                category_list_new = None
            try:
                job_link = category_list_new.find("a")
                job_link = job_link["href"]
                job_link = "https://jobs.bdjobs.com/" + job_link
                self.job_link = job_link
                print(job_link)
            except:
                job_link = None
            try:
                job_link_split = job_link.split("asp?", 1)[1]
                _dict_referer_url_para = {x[0]: x[1] for x in [x.split("=") for x in job_link_split[0:].split("&")]}
                job_id = _dict_referer_url_para['id']
            except:
                job_id = None

            try:
                if job_id:
                    unique_key = self.bdjobs_source_name + "_" + job_id
                else:
                    unique_key = None
            except:
                unique_key = None

            try:
                content = requests.get(job_link, timeout=30)
                soup = BeautifulSoup(content.text, features="lxml")
                job_new_list_div = soup.find('div', attrs={'class': 'container job-details1'})
                category_list_div_new = job_new_list_div.find('div', attrs={'id': "job-preview"})
                category_list_div_new_1 = category_list_div_new.find('h2', attrs={'class': "job-title"})
                job_title = category_list_div_new_1.text
                job_title = job_title.strip()
                job_title = os.linesep.join([s for s in job_title.splitlines() if s])
                job_title = job_title.replace('\n', '').replace(' ', '')
                # print(job_title)
            except:
                job_title = None

            try:
                company_logo_div = category_list_div_new.find('div', attrs={'class': "com-logo"})
                company_logo_img = company_logo_div.find('img')
                company_logo_src = company_logo_img['src']
                company_logo = 'https:%s' % company_logo_src
            except:
                company_logo = None

            try:
                company_name_div = category_list_div_new.find('h3', attrs={'class': "company-name"})
                company_name = company_name_div.text
                company_name = company_name.strip()
                company_name = os.linesep.join([s for s in company_name.splitlines() if s])
                company_name = company_name.replace('\n', '').replace(' ', '')
            except:
                company_name = None
            # print("company_name", company_name)

            try:
                job_vacancy_div = category_list_div_new.find('div', attrs={'class': "vac"})
                job_vacancy = job_vacancy_div.text
                job_vacancy = job_vacancy.strip()
                job_vacancy = os.linesep.join([s for s in job_vacancy.splitlines() if s])
                job_vacancy = job_vacancy.replace('\n', '').replace(' ', '')
            except:
                job_vacancy = None
            # print(job_vacancy)

            job_context = ''
            job_responsibility = ''
            job_responsibility_list = ''
            job_context_list_n = ''
            try:
                job_context_div = category_list_div_new.find_all('div', attrs={'class': 'job_des'})
                for s in job_context_div:
                    temp = s.find('h4').text
                    if str(temp).strip().startswith('Job Context'):
                        if s.find('ul'):
                            if s.find('li'):
                                temp_respons = s.find_all('li')
                                for one in temp_respons:
                                    # job_context_list_n.append(one.text.strip())
                                    job_context_list_n += one.text.strip() + '\n'
                            else:
                                job_context = s.find('ul').text.strip()
                                # job_context_list_n.append(job_context)
                                job_context_list_n += job_context + '\n'
                        elif s.find('ul'):
                            job_context = s.find('ul').text.strip()
                    elif str(temp).strip().startswith('Job Responsibilities'):
                        if s.find('ul'):
                            if s.find('li'):
                                temp_respons = s.find_all('li')
                                for one in temp_respons:
                                    # job_responsibility_list.append(one.text.strip())
                                    job_responsibility_list += one.text.strip() + '\n'
                            else:
                                job_responsibility = s.find('ul').text.strip()
                                # job_responsibility_list.append(job_responsibility)
                                job_responsibility_list += job_responsibility + '\n'
                        elif s.find('ul'):
                            job_responsibility = s.find('ul')
            except:
                pass
            # print(f'job_context:{job_context_list_n}')
            # print(f'job_responsibility_list:{job_responsibility_list}')
            emp_status = ''
            work_status = ''
            try:
                job_status_div = category_list_div_new.find_all('div', attrs={'class': 'job_nat'})
                for setr in job_status_div:
                    temp = setr.find('h4').text
                    if str(temp).strip().lower().startswith('employment'):
                        emp_status = setr.find('p').text.strip()
                    elif str(temp).strip().lower().startswith('workplace'):
                        if setr.find('p'):
                            work_status = setr.find('p').text
                        elif setr.find('ul'):
                            work_status = setr.find('li').text
            except:
                pass
            # print(f'emp_status:{emp_status}')
            # print(f'work_status:{work_status}')
            job_education_list = ''
            job_experience_list_n = ''
            try:
                job_education_requirment_div = category_list_div_new.find_all('div', attrs={'class': 'edu_req'})
                for s in job_education_requirment_div:
                    temp = s.find('h4').text
                    if str(temp).strip().startswith('Educational Requirements'):
                        if s.find('ul'):
                            if s.find('li'):
                                temp_respons = s.find_all('li')
                                # job_education_list += temp_respons.text.strip()
                                for one in temp_respons:
                                    # job_education_list.append(one.text.strip())
                                    job_education_list += one.text.strip() + '\n'
                            else:
                                job_education = s.find('ul').text.strip()
                                # job_education_list.append(job_education)
                                job_education_list += job_education + '\n'
                        elif s.find('ul'):
                            job_education = s.find('ul').text.strip()
                    elif str(temp).strip().startswith('Experience Requirements'):
                        if s.find('ul'):
                            if s.find('li'):
                                temp_respons = s.find_all('li')
                                for one in temp_respons:
                                    # job_experience_list_n.append(one.text.strip())
                                    job_experience_list_n += one.text.strip() + '\n'
                            else:
                                job_experience = s.find('ul').text.strip()
                                # job_experience_list_n.append(job_experience)
                                job_experience_list_n += job_experience + '\n'
                        elif s.find('ul'):
                            job_experience = s.find('ul')
            except:
                pass
            # print(f'Educational:{job_education_list}')
            # print(f'Experience:{job_experience_list_n}')

            try:
                job_additional_requirment_div = category_list_div_new.find('div', attrs={'class': 'job_req'})
                job_additional_requirment = job_additional_requirment_div.text.strip()
                job_additional_requirment = os.linesep.join([s for s in job_additional_requirment.splitlines() if s])
            except:
                job_additional_requirment = None
            # print(job_additional_requirment)

            try:
                job_Location_div = category_list_div_new.find('div', attrs={'class': 'job_loc'})
                job_Location = job_Location_div.text.strip()
                job_Location = os.linesep.join([s for s in job_Location.splitlines() if s])
            except:
                job_Location = None
            # print(job_Location)

            try:
                job_salary_div = category_list_div_new.find('div', attrs={'class': 'salary_range'})
                job_salary = job_salary_div.text.strip()
                job_salary = os.linesep.join([s for s in job_salary.splitlines() if s])
                job_salary = job_salary.replace('\n', '').replace(' ', '')
            except:
                job_salary = None
            # print(job_salary)

            try:
                job_compensation_div = category_list_div_new.find('div', attrs={'class': 'oth_ben'})
                job_compensation = job_compensation_div.text.strip()
                job_compensation = os.linesep.join([s for s in job_compensation.splitlines() if s])
            except:
                job_compensation = None
            # print(job_compensation)

            try:
                job_summary_div = category_list_div_new.find('div', attrs={'class': 'right job-summary'})
                job_summary = job_summary_div.text.strip()
                job_summary = job_summary.replace('\n', '').replace(' ', '')
                job_summary = os.linesep.join([s for s in job_summary.splitlines() if s])
            except:
                job_summary = None
            # print(job_summary)
            job_information = None
            try:
                job_information_div = category_list_div_new.find('div', attrs={'class': 'information'})
                for job_information in job_information_div.find_all('span'):
                    job_information = job_information.text.strip()
                    job_information = job_information.replace('\n', '').replace(' ', '')
                    job_information = os.linesep.join([s for s in job_information.splitlines() if s])
                    # print(job_information)
            except:
                pass

            # self.job_ID.append(unique_key)
            # self.job_title_list_1.append(job_title)
            # self.company_name_1.append(company_name)
            # self.Job_vacancy_1.append(job_vacancy)
            # self.job_context_1.append(job_context_list_n)
            # self.job_responsibility_1.append(job_responsibility_list)
            # self.job_status_1.append(emp_status)
            # self.job_work_1.append(work_status)
            # self.job_edu_req_1.append(job_education_list)
            # self.job_exe_req_1.append(job_experience_list_n)
            # self.job_add_req_1.append(job_additional_requirment)
            # self.job_location_1.append(job_Location)
            # self.job_salary_1.append(job_salary)
            # self.job_compenstation_1.append(job_compensation)
            # self.job_summary_1.append(job_summary)
            # self.job_information_1.append(job_information)
            # self.company_logo.append(company_logo)

            print(self.category_count)
            self.category_count = 0

            try:
                df = pd.DataFrame(
                    {'platform': self.platform_id, 'job_source': self.bdjobs_source_name,
                     'job_link': self.job_link, 'job_title': job_title,
                     'unique_key': unique_key, 'category': self.current_job_category,
                     'company_name': company_name,
                     'job_vacancy': job_vacancy,
                     'Job_Context': job_context_list_n,
                     'Job_Responsibility': job_responsibility_list,
                     'Job_status': emp_status, 'Work_place': work_status,
                     'Education Requirement': job_education_list,
                     'Experience Requirement': job_experience_list_n,
                     'Additional Requirement': job_additional_requirment, 'Location': job_Location,
                     # 'Job_Salary': job_salary, 'Compenstation': job_compensation,
                     # 'Job_summary': job_summary, 'job_information': job_information,
                     # 's3_url_company_logo': company_logo
                     })

                print(df.to_dict())
                print('---------------------------------------------------------------------\n')
            except:
                traceback.print_exc()


if __name__ == '__main__':
    bg = BdjobsScraper()
    category_list = bg.load_categories()
    bg.get_jobs(category_list)


    # def start(self):
    #     bg = BdjobsScraper()
    #     category_list = bg.load_categories()
    #     bg.get_jobs(category_list)
