import requests
import re
import time
import os.path
import ssl
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import urllib3
import datetime
import logging.handlers
from dotenv import load_dotenv
# from app import get_base_path

load_dotenv()

# from helpers.BaseDBModel import BaseDBModel
# from helpers.ocr_tesseract import OcrTesseract
# from helpers.Helper import Helper

urllib3.disable_warnings()

logging.basicConfig(filename='top_job_scrape.log', level=logging.ERROR)


class TopJobScrape:
    # initial
    def __init__(self):
        ssl._create_default_https_context = ssl._create_unverified_context
        self.options = webdriver.ChromeOptions()
        self.S3_BUCKET_URL = os.environ.get("S3_BUCKET_URL")
        self.options.add_argument('--ignire-certificate-errors')
        self.options.add_argument('--ignire-ssl-errors')
        self.platform_id = os.environ.get("TOP_JOBS_SCRAPER")
        self.start_time = None
        self.sql_start_time = None
        self.platform = []
        self.job_url_list = []
        self.category_list = []
        self.company_list = []
        self.company_email_list = []
        self.ref_no_list = []
        self.job_title_list = []
        self.closing_date_list = []
        self.image_url_list = []
        self.job_description_list = []
        self.list_remove_words = ['topjobs', 'topjob', 'top jobs', 'top job']
        self.db_model = BaseDBModel()
        self.ocr_model = OcrTesseract()
        self.helper = Helper()

    def _read_csv(self):
        _list_urls = []
        df = pd.read_csv("{}/input/job_source_input.csv".format(get_base_path()))
        _observerjobs_df = df[df['job_source'] == "topjobs"]
        for index, row in _observerjobs_df.iterrows():
            try:
                _list_urls.append(df['url'][index])
            except:
                pass
        self._scrape_first_page(_list_urls)

    def _get_job_url(self, url):
        try:
            first = "('"
            last = "',"
            start = url.rindex(first) + len(first)
            end = url.rindex(last, start)
            job_url_tail = str(url[start:end])
            job_url_tail = job_url_tail[2:]
            job_url = "https://topjobs.lk" + job_url_tail
            return job_url
        except ValueError:
            return None

    def _scrape_first_page(self, _list_urls):
        for url in _list_urls:
            try:
                try:
                    content = requests.get(url, timeout=30)
                    soup = BeautifulSoup(content.text, features="lxml")
                    # GET CATEGORY LIST
                    category_list_div = soup.find('div', attrs={'class': "category-panel-inner"})
                    category_list = category_list_div.find_all('div', attrs={'class': 'category'})
                except:
                    self.helper.check_connection()
                    content = requests.get(url, timeout=30)
                    soup = BeautifulSoup(content.text, features="lxml")
                    # GET CATEGORY LIST
                    category_list_div = soup.find('div', attrs={'class': "category-panel-inner"})
                    category_list = category_list_div.find_all('div', attrs={'class': 'category'})

                # REMOVE "All Vacancies" FROM CATEGORY LIST
                category_list.pop()
                category_list_count = len(category_list)

                category_count = 1
                for category in category_list:
                    try:
                        category_details = category.find('a')
                        category_name = category_details.text
                        category_url_tail = category_details["href"]
                        category_url = "https://topjobs.lk/" + category_url_tail

                        try:
                            category_content = requests.get(category_url, timeout=30)
                            category_soup = BeautifulSoup(category_content.text, features="lxml")
                            job_list_table = category_soup.find('table', attrs={'id': "table"})
                        except:
                            self.helper.check_connection()
                            category_content = requests.get(category_url, timeout=30)
                            category_soup = BeautifulSoup(category_content.text, features="lxml")
                            job_list_table = category_soup.find('table', attrs={'id': "table"})

                        job_list_tr = job_list_table.find_all('tr', attrs={'id': re.compile("^tr")})
                        job_list_count = len(job_list_tr)
                        job_count = 1
                        for row in job_list_tr:
                            try:
                                job_url_td = row.find('td', attrs={'class': "hide_listview"})
                                job_url_a = job_url_td.find('a')
                                job_url = job_url_a["href"]
                                job_url = self._get_job_url(job_url)

                                self._scrape_second_page(job_url, category_name)
                                print("Scraped category count:", category_count, "of", category_list_count,
                                      ":::::::::: Job count:", job_count, "of", job_list_count)
                                job_count += 1
                            except Exception as error:
                                print(error)
                    except Exception as error:
                        print(error)
                    category_count += 1
            except Exception as error:
                print(error)

    def _scrape_second_page(self, job_url, category_name):
        try:
            self.platform = []
            self.job_url_list = []
            self.category_list = []
            self.company_list = []
            self.company_email_list = []
            self.ref_no_list = []
            self.job_title_list = []
            self.closing_date_list = []
            self.image_url_list = []
            self.job_description_list = []

            try:
                content = requests.get(job_url, timeout=30)
                soup = BeautifulSoup(content.text, features="lxml")
                closing_date_label = soup.find('label', attrs={'class': 'lbl-closing-date col-sm-4'})
            except:
                self.helper.check_connection()
                content = requests.get(job_url, timeout=30)
                soup = BeautifulSoup(content.text, features="lxml")
                closing_date_label = soup.find('label', attrs={'class': 'lbl-closing-date col-sm-4'})

            try:
                closing_date = closing_date_label.find('span', attrs={'id': 'endDate'}).text
                format_closing_date = '%d/%m/%Y'
                datetime_obj = datetime.datetime.strptime(closing_date, format_closing_date)
                closing_date = datetime_obj.date()
            except:
                closing_date = None

            try:
                image_div = soup.find('div', attrs={'id': 'remark'})
                image_p = image_div.find('p')
                image_img = image_p.find('img')
                image_link = image_img["src"]
                image_url = "https://topjobs.lk" + image_link
            except:
                image_url = None

            try:
                company_name = soup.find('input', attrs={'id': 'txtAVECompanyName'})
                company_name = company_name["value"]

            except:
                company_name = None

            try:
                company_email = soup.find('input', attrs={'id': 'txtAVECompanyEmail'})
                company_email = company_email["value"]
            except:
                company_email = None

            try:
                job_title = soup.find('input', attrs={'id': 'txtAVEVacancyName'})
                job_title = job_title["value"]
            except:
                job_title = None

            try:
                job_ref_no = soup.find('input', attrs={'id': 'txtAVEJobSpecCode'})
                job_ref_no = job_ref_no["value"]
            except:
                job_ref_no = None

            # CHECK JOB AVAILABILITY BEFORE UPLOAD IMAGE TO S3
            check_job_available = self.db_model.check_job_availability(self.platform_id, job_ref_no)
            if not check_job_available:
                #  UPLOAD IMAGE TO S3
                if image_url:
                    image_url = image_url.replace(" ", "%20")
                    image_name = "%s_job_poster" % job_ref_no
                    try:
                        platform_type = self.platform_id.replace("\\", "-")
                        job_description = self.helper.images_s3_upload_process(image_url, image_name,
                                                                               platform_type, True)
                        job_description = self.helper.remove_words(job_description, self.list_remove_words)
                        job_description = job_description.strip()
                        job_description = job_description.replace(". ", "\n")
                        job_description = os.linesep.join([s for s in job_description.splitlines() if s])
                    except:
                        platform_type = self.platform_id.replace("\\", "-")
                        job_description = None
                    s3_url = "%s%s_%s.jpeg" % (self.S3_BUCKET_URL, image_name, platform_type)
                else:
                    s3_url = job_description = None

                self.platform.append(self.platform_id)
                self.job_url_list.append(job_url)
                self.category_list.append(category_name)
                self.ref_no_list.append(job_ref_no)
                self.company_list.append(company_name)
                self.company_email_list.append(company_email)
                self.job_title_list.append(job_title)
                self.closing_date_list.append(closing_date)
                self.image_url_list.append(s3_url)
                self.job_description_list.append(job_description)
                self.make_output()
            else:
                print("Job is available...")
        except Exception as error:
            print(error)
            pass

    def make_output(self):
        df = pd.DataFrame({'platform': self.platform, 'job_link': self.job_url_list, 'unique_key': self.ref_no_list, 'category': self.category_list,
                           'company_name': self.company_list, 'company_email': self.company_email_list,
                           'job_title': self.job_title_list, 'closing_date': self.closing_date_list,
                           's3_url_job_poster': self.image_url_list, 'job_description': self.job_description_list})
        self.db_model.base_job_handler(df)

    def start(self):
        self.start_time = time.time()
        self._read_csv()

