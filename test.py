import datetime
import pandas as pd


class Test:

    def date_chande(self):
        post_ain = pd.read_csv("jobzpk_final00.csv")
        post_ain_list = post_ain['job_posted'].to_list()
        print(post_ain_list)
        print("next================================================")
        # sys.exit()
        link = 'job-listings-trainer-and-product-specialists-karadi-path-education-company-pvt-ltd-adilabad-pune-nagpur-delhi-bengaluru-bangalore-warangal-dharmapuri-nandurbar-navapur-4-to-6-years-171218500178'
        for link in post_ain_list:
            print("===============================================================================" + link)
            deadline = link
            format_closing_date = '%d %B, %Y'
            datetime_obj = datetime.datetime.strptime(deadline, format_closing_date)
            deadline = datetime_obj.date()
            print(deadline)

if __name__ == '__main__':
    Tester = Test()
    Tester.date_chande()
