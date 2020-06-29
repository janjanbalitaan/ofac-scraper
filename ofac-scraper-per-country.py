import requests
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup as bs
import csv
import sys

#USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0"
USER_AGENT = "Mozilla/5.0"
HIDDEN_FIELD = ";;AjaxControlToolkit, Version=3.5.40412.0, Culture=neutral, PublicKeyToken=28f01b0e84b6d53e:en-US:1547e793-5b7e-48fe-8490-03a375b13a33:475a4ef5:5546a2b:d2e10b12:497ef277:effe2a26"
URL = "https://sanctionssearch.ofac.treas.gov/"

def ofac_search(sdn_type, name, id_number, program, min_score, address, city, state, country, list_type):
    with requests.session() as s:
        result = list()
        json_data = {
                "ctl00_ctl03_HiddenField": HIDDEN_FIELD,
                "ctl00$MainContent$ddlType": sdn_type,
                "ctl00$MainContent$txtLastName": name,
                "ctl00$MainContent$txtID": id_number,
                "ctl00$MainContent$lstPrograms": program,
                "ctl00$MainContent$Slider1": min_score,
                "ctl00$MainContent$txtAddress": address,
                "ctl00$MainContent$txtCity": city,
                "ctl00$MainContent$txtState": state,
                "ctl00$MainContent$ddlCountry": country,
                "ctl00$MainContent$ddlList": list_type,
                "ctl00$MainContent$Slider1_Boundcontrol": 50,

            }
        s.headers.update({
            'user-agent': USER_AGENT
            })

        r = s.get(URL)
        html = get_html(r.content)
        # unsupported CSS Selector 'input[name^=ctl00][value]'
        data = { tag['name']: tag['value'] 
            for tag in html.select('input[name^=ctl00]') if tag.get('value')
        }
        state = { tag['name']: tag['value'] 
            for tag in html.select('input[name^=__]')
        }

        data.update(state)
        data.update(json_data)
        try:
            data.pop('ctl00$MainContent$btnReset', None)  
        except KeyError:
            print("Key not found") 
        r = s.post(URL, data=data)
        html = get_html(r.content)
        result_table = html.find("table", {"id": "gvSearchResults"})
        if result_table != None:
            table_rows = result_table.select("tr")
            for row in table_rows:
                table_columns = row.select("td")
                name = str(table_columns[0].find("a").text)
                address = str(table_columns[1].text)
                sdn_type = str(table_columns[2].text)
                programs = str(table_columns[3].text)
                list_type = str(table_columns[4].text)
                min_score = str(table_columns[5].text)
                if "," in name:
                    splitted_full_name = name.split(",")
                    first_name = splitted_full_name[1].strip()
                    last_name = splitted_full_name[0].strip()
                    name = first_name + " " + last_name
                result.append([name, address, sdn_type, programs, list_type, min_score, country])

                link = table_columns[0].find("a").get('href')
                splitted_link = link.split(",")
                path = splitted_link[4].replace(" ", "").replace("\"", "")
                r = s.get(URL + path)
                html = get_html(r.content)
                #main_table = html.find("table", {"id": "MainTable"})
                #aliases_table = html.find("table", {"id": "ctl00_MainContent_gvAliases"})
                #address_table = html.find("table", {"id": "ctl00_MainContent_gvAliases"})
                try:
                    aliases_table = html.find("table", {"id": "ctl00_MainContent_gvAliases"})
                    aliases_rows = aliases_table.select('tr')
                    ctr = 0
                    for aliases_columns in aliases_rows:
                        if ctr > 0:
                            columns = aliases_columns.find_all('td')
                            full_name = columns[2].text
                            if "," in full_name:
                                splitted_full_name = full_name.split(",")
                                first_name = splitted_full_name[1].strip()
                                last_name = splitted_full_name[0].strip()
                                name = first_name + " " + last_name
                            else:
                                name = full_name
                            result.append([name, address, sdn_type, programs, list_type, min_score, country])
                        ctr += 1
                except:
                    pass                    
                #result.append([name, address, sdn_type, programs, list_type, min_score])
    return result

def get_ofac_sdn_type():

    return None

def get_ofac_countries():
    
    r = requests.get(URL)
    html = get_html(r.content)
    countries = set()
    country_list = html.find("select", {"id": "ctl00_MainContent_ddlCountry"})
    country_options = country_list.findAll("option")
    for country in country_options:
        if country['value'] != "":
            countries.add(country['value'])
    return countries

def get_html(response):
    html = bs(response, 'html.parser')

    return html

def write_list_to_csv(country, result):
    with open("pc_sanctionlist/" + country + '.csv', 'w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(result)
    writeFile.close()

if __name__ == "__main__":
    sdn_type = "All"
    min_score = 50
    countries = get_ofac_countries()
    country = sys.argv[1]
    result = ofac_search(sdn_type, "", "", "", min_score, "", "", "", country, "")
    if len(result) > 0:
        write_list_to_csv(country, result)
