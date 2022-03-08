# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from itemadapter import ItemAdapter
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import re


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.vacancies0103

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            item['min'], item['max'], item['cur'] = self.process_salary(item['salary'])

        elif spider.name == 'superjob':
            item['min'], item['max'], item['cur'] = self.process_salary_superjob(item['salary'])

        del item['salary']
        collection = self.mongobase[spider.name]
        try:
            collection.insert_one(item)
        except DuplicateKeyError:
            pass
        return item

    def process_salary(self, salary):

        if len(salary) == 1:
            return None, None, None

        if len(salary) == 7:
            min_salary = int(salary[1].replace('\xa0', ''))
            max_salary = int(salary[3].replace('\xa0', ''))
            cur = salary[5]
            return min_salary, max_salary, cur

        if len(salary) == 5:
            if salary[0] == 'от ':
                min_salary = int(salary[1].replace('\xa0', ''))
                cur = salary[3]
                return min_salary, None, cur

            elif salary[0] == 'до ':
                max_salary = int(salary[1].replace('\xa0', ''))
                cur = salary[3]
                return None, max_salary, cur


    def process_salary_superjob(self, salary):
        try:

            if len(salary) == 1:
                return None, None, None

            if len(salary) == 5:
                if salary[0] == 'от':
                    min_salary = int(re.search(r'\d+', salary[2].replace('\xa0', '')).group())
                    cur = re.search(r'[^\d]+', salary[2].replace('\xa0', '')).group()
                    return min_salary, None, cur

                elif salary[0] == 'до':
                    max_salary = int(re.search(r'\d+', salary[2].replace('\xa0', '')).group())
                    cur = re.search(r'[^\d]+', salary[2].replace('\xa0', '')).group()
                    return None, max_salary, cur

            if len(salary) > 5:
                return None, None, None

        except:
            return None, None, None

