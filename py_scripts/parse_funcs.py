import csv

def parse_product_list(file, name):
    print(type(file))
    productList_string = file.read().decode('utf-8') #request.form.get('productListFile')
    productList = [{k: v for k, v in row.items()} for row in csv.DictReader(productList_string.splitlines(), skipinitialspace=True)]
    print(productList)
    return productList
