import requests
from bs4 import BeautifulSoup
import re
from time import sleep
import json
import pandas as pd
from helpers.Helper import Helper
from helpers.BaseDBModel import BaseDBModel
import os
import sys
from dotenv import load_dotenv


class IkmanJobs:
    def __init__(self):
        # self._ik_base_url = 'https://ikman.lk/en/ads/sri-lanka/jobs?sort=date&order=desc&buy_now=0&urgent=0&page='
        self.ik_main_url = 'https://ikman.lk'
        self.helper = Helper()
        self.IKMAN_JOB_SCRAPER = os.environ.get("IKMAN_JOBS_SCRAPER")
        self.list_remove_words = ['ikman.lk', 'ikman', 'ikmanjobs']
        self.db_model = BaseDBModel()

    def get_date(self, value):
        return re.split("T", value)[0]

    def _create_final_output(self, url, _data_dict):

        job_ad_url = url
        job_title = ''
        job_employer = ''
        job_role = ''
        job_salary = ''
        currency = ''
        min_salary = ''
        max_salary = ''
        job_experience = ''
        job_type = ''
        req_edu = ''
        website = ''
        application_deadline = ''
        job_description = ''
        job_id = ''
        primary_phone_number = []
        phone_numbers = ''
        job_primary_category = ''
        job_location_area = ''
        account_id = ''
        is_member = ''
        company_name = ''
        job_post_date = ''
        membership_level = ''
        img_logo_url = ''
        job_deactivate = ''
        job_location = ''
        job_location_id = ''
        job_category_name = ''
        job_category_id = ''
        job_geo_region = ''
        job_contact_name = ''
        company_contact_numbers = []
        contact_numbers = ""
        shop_id = ''
        shop_name = ''
        shop_email = ''
        shop_logo = ''
        s3_url = ''

        try:
            job_id = _data_dict['adDetail']['data']['ad']['id']
        except Exception as e:
            # print(f'job_id:{e}')
            pass
        try:
            phone_numbers = _data_dict['adDetail']['data']['ad']['job']['apply_via']['phone_numbers']
        except Exception as e:
            # print(f'phone_numbers:{e}')
            pass
        try:
            primary_phone_number = _data_dict['adDetail']['data']['ad']['job']['apply_via']['phone_number']
        except Exception as e:
            # print(f'primary_phone_number:{e}')
            pass
        if len(primary_phone_number) == 0:
            primary_phone_number = ''
        else:
            primary_phone_number = str(primary_phone_number)[1:-1]
        try:
            contact_numbers = ""
            company_contact_numbers_all = _data_dict['adDetail']['data']['ad']['contactCard']['phoneNumbers']
            for num in company_contact_numbers_all:
                if str(num.get('verified')).lower().strip() == 'true':
                    company_contact_numbers.append(num.get('number'))
                    contact_numbers += ",%s" % str(num.get('number'))
            contact_numbers = contact_numbers[1:]
            contact_numbers = contact_numbers.replace("'", "").replace('"', '')
            if contact_numbers:
                contact_numbers = str(contact_numbers)
        except:
            contact_numbers = ""
            pass

        try:
            job_title = _data_dict['adDetail']['data']['ad']['title']
        except Exception as e:
            # print(f'job_Title:{e}')
            pass
        try:
            job_description = _data_dict['adDetail']['data']['ad']['description']
            job_description = self.helper.remove_words(job_description, self.list_remove_words)
            job_description = job_description.strip()
            job_description = job_description.replace(". ", "\n")
            job_description = os.linesep.join([s for s in job_description.splitlines() if s])
        except Exception as e:
            pass
        try:
            ad_properties = _data_dict['adDetail']['data']['ad']['properties']
            for one in ad_properties:
                if one.get('key') == 'company_name':
                    job_employer = one.get('value')
                elif one.get('key') == 'item_type':
                    job_role = one.get('value')
                elif one.get('key') == 'employment':
                    job_type = one.get('value')
                elif one.get('key') == 'min_qualification':
                    req_edu = one.get('value')
                elif one.get('key') == 'experience':
                    job_experience = one.get('value')
                elif one.get('key') == 'company_website':
                    website = one.get('value')
                elif one.get('key') == 'salary':
                    job_salary = one.get('value')
                elif one.get('key') == 'deadline':
                    application_deadline = one.get('value')

        except Exception as e:
            print(f'Job add details:{e}')
            pass

        try:
            job_primary_category = _data_dict['category']['name']
        except Exception as e:
            pass

        try:
            job_category_name = _data_dict['adDetail']['data']['ad']['category']['name']
        except:
            pass

        try:
            job_category_id = _data_dict['adDetail']['data']['ad']['category']['id']
        except:
            pass

        try:
            job_location_area = _data_dict['adDetail']['data']['ad']['area']['name']
        except Exception as e:
            pass

        try:
            job_location = _data_dict['adDetail']['data']['ad']['location']['name']
        except Exception as e:
            pass

        try:
            job_location_id = _data_dict['adDetail']['data']['ad']['location']['id']
        except Exception as e:
            pass
        try:
            job_geo_region = _data_dict['adDetail']['data']['ad']['location']['geo_region']
        except Exception as e:
            pass

        try:
            account_id = _data_dict['adDetail']['data']['ad']['account']['id']
        except Exception as e:
            pass

        try:
            is_member = _data_dict['adDetail']['data']['ad']['account']['traits']['member']
        except Exception as e:
            pass

        try:
            company_name = _data_dict['adDetail']['data']['ad']['details']
        except Exception as e:
            pass

        try:
            job_post_date = _data_dict['adDetail']['data']['ad']['adDate']
            job_post_date = self.get_date(job_post_date)
        except Exception as e:
            pass

        try:
            job_deactivate = _data_dict['adDetail']['data']['ad']['deactivates']
            job_deactivate = self.get_date(job_deactivate)
        except Exception as e:
            pass
        try:
            membership_level = _data_dict['adDetail']['data']['ad']['membershipLevel']
        except Exception as e:
            pass

        try:
            img_logo_url = _data_dict['adDetail']['data']['ad']['imgUrl']
        except Exception as e:
            pass
        try:
            job_contact_name = _data_dict['adDetail']['data']['ad']['contactCard']['name']
        except:
            pass

        try:
            shop_id = _data_dict['adDetail']['data']['ad']['shop']['id']
        except:
            pass
        try:
            shop_name = _data_dict['adDetail']['data']['ad']['shop']['name']
        except:
            pass
        try:
            shop_email = _data_dict['adDetail']['data']['ad']['shop']['email']
        except:
            pass

        try:
            if job_salary:
                currency = 'Rs' if 'Rs' in job_salary else '$' if '$' in job_salary else None
                job_salary = job_salary.replace(",", "")
                splitted_salary = job_salary.split(" ")
                splitted_salary.remove('-') if '-' in splitted_salary else None
                splitted_salary.remove('Rs') if 'Rs' in splitted_salary else None
                splitted_salary.remove('$') if '$' in splitted_salary else None

                min_salary = splitted_salary[0] if len(splitted_salary) > 0 else None
                max_salary = splitted_salary[1] if len(splitted_salary) > 1 else None
        except:
            pass
        df = pd.DataFrame({'platform': self.IKMAN_JOB_SCRAPER,
                           'unique_key': [job_id],
                           'category': [job_category_name],
                           'company_name': [job_employer],
                           'company_email': [''],
                           'job_title': [job_title],
                           'expire_at': [application_deadline],
                           'job_description': [job_description],
                           'job_link': [job_ad_url],
                           'job_role': [job_role],
                           'job_type': [job_type],
                           'currency': [currency],
                           'min_salary': [min_salary],
                           'max_salary': [max_salary],
                           'educational_requirements': [req_edu],
                           'job_experience': [job_experience],
                           'job_category': [job_primary_category],
                           'start_at': [job_post_date],
                           'district': [job_location_area],
                           'primary_phone_number': [str(primary_phone_number)],
                           'company_telephone': [phone_numbers],
                           'membership': [membership_level],
                           'account_id': [account_id],
                           'is_member': [is_member],
                           'job_category_id': [job_category_id],
                           'location ': [job_location],
                           'job_location_id ': [job_location_id],
                           'job_geo_region': [job_geo_region],
                           'job_deactivate ': [job_deactivate],
                           'shop_id': [shop_id],
                           'shop_name': [shop_name],
                           'shop_email': [shop_email],
                           'shop_logo': [shop_logo],
                           'job_contact_name': [job_contact_name],
                           'company_contact_numbers': [contact_numbers]
                           })
        # df.to_csv("test111.csv", mode='a', header=False, index=False, encoding='utf-8')
        check_job_available = self.db_model.check_job_availability(self.IKMAN_JOB_SCRAPER, job_id)
        if not check_job_available:
            self.db_model.base_job_handler(df)
        else:
            print(job_id, "Job is available...")
            # UPDATE CURRENT DATA
            table_name = 'jobs'
            update_columns = "currency= '%s', min_salary='%s', max_salary= '%s', educational_requirements='%s'" % (currency, min_salary, max_salary, req_edu)
            search_key = 'id'
            update_ids = [check_job_available["id"]]
            self.db_model.update_multiple_records(table_name, update_columns, search_key, update_ids)
        return True

    def get_all_jobs_urls(self):
        i = 0
        while i in range(0, 150):
            try:
                print('Page Number :', i+1)
                i += 1
                content = requests.get(f'https://ikman.lk/en/ads/sri-lanka/jobs?sort=date&order=desc&buy_now=0&urgent=0'
                                       f'&page={i}', timeout=30,  headers = {"Accept-Language": "en-US"})
                soup = BeautifulSoup(content.text, features="html.parser")
                all_links = soup.find('div', attrs={'class': re.compile('^list-wrapper')})
                links_list = []
                for one in all_links:
                    for two in one.findAll('li'):
                        for three in two:
                            link = self.ik_main_url + three.get('href')
                            links_list.append(link)
                _data_dict = None
                count = 1
                for single_url in links_list:
                    print("Scraped %s out of %s of Page Number : %s" % (count, len(links_list), i))
                    count += 1
                    try:
                        _res = requests.get(single_url, headers = {"Accept-Language": "en-US"}).content
                        soup = BeautifulSoup(_res.decode('utf-8', 'ignore'), features="lxml")
                        _page_data = soup.findAll('script', attrs={'type': "text/javascript"})
                        for _job_data in _page_data:
                            try:
                                if re.search('window.initialData', str(_job_data)):
                                    _split_data_1 = str(_job_data).split('window.initialData =')
                                    _split_data_2 = str(_split_data_1[1]).split('</script>')[0]
                                    _data_dict = json.loads(_split_data_2)
                                    self._create_final_output(single_url, _data_dict)
                            except:
                                pass
                    except Exception as e:
                        print(f'e:{e}')
                    # print('sleep')
                    # sleep(100)
                # sleep 5 seconds after finishing one page
                sleep(5)
            except requests.ConnectionError:
                print('Connection error')
            except Exception as e:
                print(f'e:{e}')

    def input_url_download(self):
        self.get_all_jobs_urls()
