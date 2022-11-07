import builtins
from lib2to3.pgen2 import driver
from requests import ConnectionError

import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import csv
import time
import requests
from itertools import zip_longest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.keys import Keys
from time import sleep

nama_hotel = []
address_hotel = []
latitude = []
longitude = []
walk_grade = []
no_restaurant = []
no_attraction = []
lst_res = []
lst_attr = []
ignored = (NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException)


def latlong(link):
    """
    Fungsi untuk dapet data lat long hotel
    :param link:
    :return lattitude dan longitude:
    """
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}
    sleep(15)
    raw = requests.get(link, headers=headers)
    data = raw.json()
    lat = data['hotels'][0]['location']['geoPoint']['latitude']
    long = data['hotels'][0]['location']['geoPoint']['longitude']
    return lat, long



# Bikin lagi windows page baru khusus buat pagination
driver_page = webdriver.Firefox()
driver_page.get('https://www.tripadvisor.com/Hotels-g294225-Indonesia-Hotels.html')
delay_page = WebDriverWait(driver_page, 3, ignored_exceptions=ignored)
WebDriverWait(driver_page, 90)
driver_page.find_element(By.XPATH, "//button[@class='rmyCe _G B- z _S c Wc wSSLS pexOo sOtnj']").click()
temp = 0
link_page = []

WebDriverWait(driver_page, 30, ignored_exceptions=ignored)
page = 0

# Looping Pagination Function
for i in range(0, 106):
    print('Page ke-{} lagi discrap'.format(page))
    page += 1
    driver_utama = driver_page.current_window_handle
    sleep(5)
    delay_page.until(EC.invisibility_of_element_located((By.XPATH, "//div[@class='tppr_rup ppr_priv_hotels_loading_box']")))
    delay_page.until(EC.invisibility_of_element_located((By.XPATH, "//div[@class='ppr_rup ppr_priv_hotels_loading_box']")))
    sleep(3)
    try:
        url_fresh = WebDriverWait(driver_page, 3).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "a[data-clicksource='HotelName']")))
        for asik in url_fresh:
            link_page.append(asik.get_attribute('href'))
    except StaleElementReferenceException:
        print('Gagal lagi')
        url_fresh2 = WebDriverWait(driver_page, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "a[data-clicksource='HotelName']")))
        for asik in url_fresh2:
            sleep(10)
            link_page.append(asik.get_attribute('href'))

    driver_page.execute_script("window.open(''),'_blannk'") #Open new tab
    driver_page.switch_to.window(driver_page.window_handles[1]) #Ke Tab Baru
    #Looping URLS
    for urls in range(0, len(link_page)):
        stak = True
        attempt = 300
        linkgeo = link_page.pop(0)
        while stak and attempt > 0:
            try:
                driver_page.implicitly_wait(10)
                lg_split = linkgeo.split('-')
                no_geo = lg_split[2].removeprefix('d')
                # Mulai Pagination dengan driver baru
                driver_page.get(linkgeo)
                sleep(10)
                res_temp = []
                attr_temp = []
                # Extract data alamat, nearby POI, etc
                try:
                    hotel = driver_page.find_element(By.XPATH, "//div[@class='jvqAy']/h1[@id='HEADING']")
                    driver_page.implicitly_wait(3)
                    nama_hotel.append(hotel.text)
                except NoSuchElementException:
                    vac_rental = driver_page.find_element(By.XPATH, "//h1[@data-test-target='rental-detail-header']")
                    nama_hotel.append(vac_rental.text)
                    print('Hotel {} di page {} dan urutan {} tidak mempunyai atribut yang sesuai standar'.format(vac_rental.text, i, temp))
                
                try:
                    add_hot = driver_page.find_element(By.XPATH, "//div[@class='gZwVG S4 H3 f u FUyxx']/span[@class='oAPmj _S YUQUy PTrfg']/span[@class='fHvkI PTrfg']")
                    sleep(5)
                    address_hotel.append(add_hot.text)
                except NoSuchElementException:
                    address_hotel.append('Alamat gak jelas')
                    print('Alamat gak jelas')
                sleep(5)
                try:
                    a, b = latlong('https://www.tripadvisor.com/data/1.0/mapsEnrichment/hotel/{}?rn=1&rc=Hotel_Review&stayDates=2022_11_13_2022_11_14&guestInfo=1_2&placementName=Hotel_Review_MapDetail_Anchor&currency=IDR'.format(no_geo))
                    latitude.append(a)
                    longitude.append(b)
                except TypeError:
                    latitude.append('No Data')
                    longitude.append('No Data')
                    temp += 1
                    stak = False
                try:# Blok Try-Catch untuk grade walk, no resto dan no atrr
                    walk = driver_page.find_element(By.XPATH, "//span[@class='iVKnd fSVJN']")
                    resto = driver_page.find_element(By.XPATH, "//span[@class='iVKnd Bznmz']")
                    attra = driver_page.find_element(By.XPATH, "//span[@class='iVKnd rYxbA']")
                    walk_grade.append(walk.text)
                    no_restaurant.append(resto.text)
                    no_attraction.append(attra.text)

                except NoSuchElementException:
                    walk_grade.append('Not Graded Yet')
                    no_restaurant.append('No Data Yet')
                    no_attraction.append('No Data Yet')

                try:
                    poi_rest = driver_page.find_elements(By.XPATH, "//div[@class='ui_column is-4 SdZtm f e'][2]/a[@class='cpyVm _S I']/div[@class='sinXi']")
                    if poi_rest is None:
                        lst_res.append('Nope')
                    else:
                        for il in poi_rest:
                            res_temp.append(il.text)
                        lst_res.append(res_temp)
                except(NoSuchElementException, TimeoutException, StaleElementReferenceException):
                    driver_page.implicitly_wait(2)
                    lst_res.append('Gak Ada Data')

                try:
                    poi_attr = driver_page.find_elements(By.XPATH, "//div[@class='ui_column is-4 SdZtm f e'][3]/a[@class='cpyVm _S I']/div[@class='sinXi']")
                    if poi_attr is None:
                        lst_attr.append('Nope')
                    else:
                        for j in poi_attr:
                            attr_temp.append(j.text)
                        lst_attr.append(attr_temp)
                except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
                    driver_page.implicitly_wait(5)
                    lst_attr.append('Empty')
                k = [nama_hotel, address_hotel, latitude, longitude, walk_grade, no_restaurant, no_attraction, lst_res, lst_attr]
                export = zip_longest(*k, fillvalue='')

                #Setiap ada data baru, langsung diinput kedalam file csv

                with open('tripadvisor_indo_hotel', 'w', encoding='utf-8') as file_csv:
                    wb = csv.writer(file_csv)
                    wb.writerow(
                            ("Nama Hotel", "Alamat Hotel", "Latitude", "Longitude", "Walking Grade", "Jumlah Restoran Terdekat",
                             "Jumlah Attraction Terdekat", "Top Reviewed Restoran Terdekat",
                             "Top Reviewed Attraction Terdekat"))
                    wb.writerows(export)
                file_csv.close()
                temp += 1
                print('Hotel ke-{}'.format(temp))
                stak = False #Hentikan while loop ketika proses iterasi entry data selesai

            except(TimeoutException, StaleElementReferenceException, NoSuchElementException, requests.Timeout, requests.ConnectionError, builtins.TimeoutError, ElementClickInterceptedException):
                driver_page.refresh()
                print('Error lagi')
                sleep(5)
                attempt -= 1
            if attempt == 0:
                print('Masih stak, refresh attempt sampe dapet')
                driver_page.refresh()
                attempt = 10

    driver_page.close()
    driver_page.switch_to.window(driver_utama)
    try:
        driver_page.find_element(By.XPATH, "//span[@class='nav next ui_button primary']").click()
    except NoSuchElementException:
        break


print('Proses Selesai')
driver_page.quit()


