from seleniumwire import webdriver
import time
import os
import multiprocessing
import json

def run_tor():
    os.system('tor.lnk')

def interceptor(headers, data):
    def intercept_function(request):
        for key in request.headers.keys():
            del request.headers[key]

        for key, value in headers.items():
            request.headers[key] = value

        request.body = json.dumps(data).encode('utf-8')

    return intercept_function

def main():
    options = {'proxy': {"http": "socks5h://localhost:9050", "https": "socks5h://localhost:9050"}}

    driver = webdriver.Chrome(seleniumwire_options=options)

    p = multiprocessing.Process(target=run_tor)
    p.start()

    driver.request_interceptor = interceptor(headers, data)
    driver.get(url)

    driver.find_element_by_xpath('//*[@id="captcha_submit"]').click()

    time.sleep(5)

    p.join()

    driver.close()

if __name__ == '__main__':
    main()