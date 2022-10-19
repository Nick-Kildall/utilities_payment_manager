import datetime
from lib2to3.pgen2.driver import Driver
import time

def get_last_month() -> str:
    """returns str of last month (ex. 'June')"""
    
    month_num = str(int(datetime.datetime.now().strftime("%m")) - 1)
    if month_num == 0:
        month_num = 12
    datetime_object = datetime.datetime.strptime(month_num, "%m")
    month_name = datetime_object.strftime("%B")
    return month_name

def get_balance(driver:Driver, path:int, try_sleep:int, except_sleep:int) -> str:
    try:
        time.sleep(try_sleep)
        result = driver.find_element("xpath", path)
    except:
        time.sleep(except_sleep)
        result = driver.find_element("xpath", path)
    return result 

def ask_user_to_quit() -> None:
    end_run = input("Would you like to end entire process? [y/n]: ").lower()
    if end_run == 'yes' or end_run == 'y':
        quit()