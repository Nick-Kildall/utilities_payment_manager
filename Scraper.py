"""A webscraping application to split bills between my roommates and I.

Using Selenium to grab bills from Avista Utilies and Spectrum Internet.
Calculates how to split up the bills. Sends Venmo requests to whomever
specified. Sends emails to let specified people know the bill breakdown.

This is a purely personal project because I find splitting up the bills dreadful.
As such, this code is very hacky and low quality... it's meant to be a time savor
and I don't anticipate anyone having the exact same needs as me.
"""

from selenium import webdriver
import time
import yagmail
from venmo_api import Client

# should be in same directory. Use private_info_example.py as an example
import private_info as info
from helpers import get_last_month, get_balance, ask_user_to_quit

driver = webdriver.Chrome() # selenium driver

###### Avista Vars ######
avista_username = info.avista_username
avista_password = info.avista_password

avista_login_url = 'https://www.myavista.com/sign-in'
avista_summary_url = 'https://www.myavista.com/your-account/account-summary'
avista_email_path = '//*[@id="sign-in-email-field"]'
avista_password_path = '//*[@id="sign-in-pw-field"]'
avista_button_path = '//*[@id="navmain"]/div[2]/div[1]/div/div[1]/fieldset/ol/li[5]/ol/li[2]/div/div[2]/button'
avista_balance_path = '//*[@id="balanceDue"]'

spectrum_username = info.spectrum_username
spectrum_password = info.spectrum_password
###### end ######

###### Spectrum Vars ######
spectrum_login_url = 'https://id.spectrum.net/login?account_type=RESIDENTIAL&client_id=consumer_portal&code_challenge=2_y_2CV-jGxm9reIO38rjw9IjvV7OnS3fxAHIfT6Ht4&code_challenge_method=S256&exVisitID=202210190201P-414b8b36-1f8b-420a-8bbb-864ea7b181b9&nonce=796842834953632539699441024669&redirect_uri=https:%2F%2Fwww.spectrum.net%2Fsign-in-redirect&state=eyJ0YXJnZXRVcmwiOiJodHRwczovL3d3dy5zcGVjdHJ1bS5uZXQvYWNjb3VudC1zdW1tYXJ5IiwieHNyZiI6IlJXOTZRVlJGZUZGQlRVaElWbTFXTGxaWU5tWkVUSGt0U25wblJ6Wi1VSFZFY2paeGJtcHlaRkZPVWciLCJpc0RsYSI6ZmFsc2V9'
spectrum_billing_info_url = 'https://www.spectrum.net/billing'
spectrum_email_path = '//*[@id="cc-username"]'
spectrum_password_path = '//*[@id="cc-user-password"]'
spectrum_button_path = '//*[@id="main-content-card"]/ng-component/div/form/button'
spectrum_balance_path = '//*[@id="total-due-container"]/div[2]/span/h2'
###### end ######

# getting name of last month
month_name = get_last_month()

###### Get Avista Balance ######
driver.get(avista_login_url)

driver.find_element("xpath", avista_email_path).send_keys(avista_username)
driver.find_element("xpath", avista_password_path).send_keys(avista_password)
driver.find_element("xpath", avista_button_path).click()

# grabbing data from page gives '' if handled incorrectly
avista_balance = get_balance(driver, avista_balance_path, try_sleep=20, except_sleep=25)
avista_balance = float(driver.find_element("xpath", avista_balance_path).text.replace('$',''))
###### end ######

###### Get Spectrum Balance ######
driver.get(spectrum_login_url)

try:
    driver.implicitly_wait(30)
    time.sleep(5)
    driver.find_element("xpath", spectrum_email_path).send_keys(spectrum_username)
    driver.find_element("xpath", spectrum_password_path).send_keys(spectrum_password)
    driver.find_element("xpath", spectrum_button_path).click()
except: 
    time.sleep(15)
    driver.find_element("xpath", spectrum_email_path).send_keys(spectrum_username)
    driver.find_element("xpath", spectrum_password_path).send_keys(spectrum_password)
    driver.find_element("xpath", spectrum_button_path).click()

# Spectrum is also slow. Give it time so nothing breaks
try:
    driver.implicitly_wait(5)
    time.sleep(5)
    driver.get(spectrum_billing_info_url)
except:
    time.sleep(15)
    driver.get(spectrum_billing_info_url)

spectrum_balance = get_balance(driver, spectrum_balance_path, try_sleep=5, except_sleep=15)
spectrum_balance = float(spectrum_balance.text.replace('$',''))
###### end ######

###### Calculate Bill Split ######

# split total cost as specified in private_info.py
total_amount = round(((avista_balance + spectrum_balance)), 2)
venmo_amount = round(total_amount/info.split_num_ways, 2)

with open((month_name + " WSU Bills"), 'w') as out_file:
    out_file.write("Avista Power Bill: $" + str(avista_balance) + "\n")
    out_file.write("Spectrum Internet Bill: $" + str(spectrum_balance) + "\n")
    out_file.write("Total Cost: $" + str(total_amount) + "\n\n")
    out_file.write("--> Each Member owes: $" + str(venmo_amount) + "\n")

print("Avista Power Bill: ", avista_balance)
print("Spectrum Internet Bill: ", spectrum_balance)
print("Each Member owes: ", venmo_amount)


while True:
    send_report = input("Would you like to send out email reciepts and venmo requests? [y/n] ").lower()
    if send_report == 'y' or send_report == 'yes':
        break
    if send_report == 'n' or send_report == 'no':
        driver.close()
        quit()
    print("Please enter y/yes/n/no.")

###### end ######

###### Send Venmo Requests ######
access_token = Client.get_access_token(username=info.venmo_username,
                                    password=info.venmo_password)

client = Client(access_token=access_token)
approval_dict = {}
for venmo_name in info.venmo_names:
    users = client.user.search_for_users(query=venmo_name, username=True, limit=1)
    if users:
        for user in users:
            while True: # confirm payment request
                approval = input(f"Approve ${venmo_amount} Venmo request for {user.display_name} [y/n]: ").lower()
                if approval == 'yes' or approval == 'y':
                    approval_dict[user.username] = user.id
                    pass
                    break
                elif approval == 'no' or approval == 'n':
                    ask_user_to_quit()
                    break
    else: # no user with venmo_name found
        print(f"The provided Venmo name {venmo_name} is not valid. Skipping")
        ask_user_to_quit()

print(f"Sending Venmo requests to {list(approval_dict.keys())}")
for username in approval_dict:
    client.payment.request_money(venmo_amount, f"{month_name} WSU Bills", approval_dict[username])
    pass

client.log_out(access_token)

###### end ######

###### Send Emails ######
email_list = info.email_list
print(f"Sending emails to {email_list}")
formated_email = f"Hello Everyone, here is the breakdown for {month_name}'s bills:\n- Internet: ${spectrum_balance}"+\
    f"\n- Electric: ${avista_balance}\n- Total: ${total_amount}\n- Individual Cost: ${venmo_amount}\n\n" +\
    "I have sent a Venmo request to both of you. If you would like to pay with another method this month, feel free to cancel the Venmo request.\n\n" +\
    f"Let me know if you have any questions or concerns.\n\nBest,\nNick"
yag = yagmail.SMTP({info.source_email:info.source_name}, info.mail_app_key)
yag.send(to=email_list,subject=f"{month_name}'s WSU Bills", contents=formated_email)
###### end ######

# close Selanum browser...slow
driver.close()

