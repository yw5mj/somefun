#! /usr/bin/env python3

import requests
import time, sys, os
costco_url = 'https://www.costco.com'
output_dir = 'output/'
# Only save deals, if False then save all prices
run_deals = True
# Only scan 1 product category selected at run time
# If False then scan through all Costco products
all_category = False
# Minimal time allowed every request
time_delta = 0.5
# Output filename
fname = 'deals'

def request_page(url,
                 headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"},
                 timeout = 10):
    start = time.time()
    fail = True
    while fail:
        fail = False
        try:
            res = requests.get(costco_url+url,
                               headers=headers,
                               timeout=timeout).content.decode()
        except:
            print("WARNING: Bad request at {0}, retrying...".format(url))
            time.sleep(30)
            fail = True
    if time.time() - start < time_delta:
        time.sleep(time_delta - (time.time() - start))
    return res

def error_log(log):
    logname = output_dir + 'error_{}.log'.format(round(time.time() * 1000))
    with open(logname, 'w') as f:
        f.write(str(log))
    return logname

def scan_one_page(page, res):
    items = page.split('<input type="hidden" id="product_name_')[1:]
    if (not items) and 'Shop by Category' in page:
        cont = page.split('Shop by Category')[1]
        cont = cont.split('<div class="col-xs-6 col-md-3">')[1:]
        for c in cont:
            url = c.split("<a href='https://www.costco.com")[1].split("'")[0]
            scan_all_page(url, res)
    for item in items:
        try:
            name = item.split('value="')[1].split('" />')[0]
            price = item.split('<div class="price" id="price-')[1].split('$')[1].split('\n')[0]
            if run_deals and price[-3:] == '.99': continue
            url = item.split('<a href="')[1].split('"')[0]
            res[name] = (price, url)
        except Exception as e:
            print('\t>> ERROR running scan_one_page: ', e)
            print('\t>> logfile: {}'.format(error_log(item)))

def scan_all_page(url, res):
    page = request_page(url)
    scan_one_page(page, res)
    if '<li class="forward">' in page:
        url_raw = page.split('<li class="forward">')[1]
        try:
            url = url_raw.split('<a href="https://www.costco.com')[1].split('"')[0]
            scan_all_page(url, res)
        except Exception as e:
            print('\t>> ERROR running scan_all_page: ', e)
            print('\t>> logfile: {}'.format(error_log(url_raw)))

def scan_one_cat(urls, outf='deals.txt'):
    res = {}
    for url in urls:
        print('> getting {}'.format(url))
        scan_all_page(url, res)
    with open(outf, 'a+') as f:
        for i in res:
            f.write('name: {0}\n\t price: {1}\n\t url: {2}\n\n'.format(i, res[i][0], res[i][1]))

def scan_all_cat(url):
    page = request_page(url)
    raw_cat = page.split('<a class="h2-style-guide" href="')[1:-1]
    ref_dict = []
    for n, cont in enumerate(raw_cat):
        key = cont.split('>')[1][:-3]
        val = {i.split('"')[0] for i in cont.split('<a class="body-copy-link" href="')[1:]}
        ref_dict.append(val)
        print("\t{0}: {1}".format(n, key))
    if all_category: return ref_dict
    ref_id = int(input('Select the index of the category for deals: '))
    return [ref_dict[ref_id]]

if __name__ == '__main__':
    if len(sys.argv) > 1:
        run_deals = ('ALL_PRICE' not in sys.argv)
        all_category = ('ALL_CATEGORY' in sys.argv)
        if not run_deals: print("WARNING: ALL_PRICE enabled.")
        if all_category: print("WARNING: ALL_CATEGORY enabled.")
        fnames = [i[13:] for i in sys.argv if 'OUT_FILENAME=' in i]
        if fnames: fname = fnames[-1]
    outf = output_dir + fname + '.txt'
    os.makedirs(output_dir, exist_ok=True)
    os.system('rm -f {}'.format(outf))
    refs = scan_all_cat('/SiteMapDisplayView')
    for r in refs: scan_one_cat(r, outf)
    
