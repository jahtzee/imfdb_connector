# Author: Jan Zimmer
# Last revision: 2023-04-18
# 
# This script is an attempt to extract data from the Internet Movie Firearms Database project, which is a MediaWiki based collaborative effort
# to catalogue appearences of firearms in movies and television. Extracted data is stored in a PostgreSQL database server.
#

# Imports
import psycopg2
import requests
import os
import re
from bs4 import BeautifulSoup
import pandas as pd #1.20 or above required
import time
import csv

# Establish a connection to the database
cnx = psycopg2.connect(
    host="localhost",
    user="imfdb",
    password=os.environ.get("PG_IMFDB_PASSWORD"),
    database="imfdb"
)

# Create a cursor object
cursor = cnx.cursor()

def api_request(url):
    # Makes a get request to the specified API endpoint. A JSON response is expected.

    # Make a GET request to the IMFDB API endpoint
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Get the JSON data from the response
        return response.json()
    else:
        # Handle the error
        print(f"ERROR: api_request(): Request failed with status code: {response.status_code}")
        return None
    
def parse_page_by_id(pageid, prop, format):
    # Example: parse_page_by_id("215875","text", "json") to parse the wiki text of Weird Al Yankovic as json

    data = api_request(f"https://www.imfdb.org/api.php?action=parse&pageid={pageid}&prop={prop}&format={format}")

    # Error Handling
    if data is None:
        print("ERROR: parse_page_by_id(): Data is None!")
        return None
    
    return data

def get_page_id_by_url(url, format):
    # url must take the form of '/wiki/Elke_Sommer'
    if url is None:
        print(f"ERROR: get_page_id_by_url(): url was None!")
        return None
    title = None
    match = re.match(r"^(\/wiki\/)(.*)$", url)
    if match:
        title = match.group(2)
        if "#" in title: # HTML anchors need to be stripped
            title = title.split("#")[0].strip()

    if title is None:
        print(f"ERROR: get_page_id_by_url(): No title could be found for url '{url}'!")
        return None
    data = api_request(f"https://www.imfdb.org/api.php?action=query&titles={title}&format={format}")
    if data is None:
        print(f"ERROR: get_page_id_by_url(): Data is None for url '{url}'!")
        return None
    if (len(data["query"]["pages"]) > 1):
        print(f"ERROR: get_page_id_by_url(): More than one page was returned for '{url}'!")
        return None
    for value in data["query"]["pages"]:
        pageid = value
    return pageid

def get_page_text_by_id(pageid): 
    # This used to be an API call, but due to issues with the HTML the API responds with (which doesn't match the actual page structure),
    # we are now receiving it by GET request.
    #    data = parse_page_by_id(pageid, "text", "json")
    #    return str(data["parse"]["text"]["*"])
    response = requests.get(f"https://www.imfdb.org/index.php?curid={pageid}")
    return str(response.text)

def query_categorymembers(cmtitle, format):
    # Example: query_categorymembers("Category:Actor", "json") to query all actor pages as json.

    # Make a GET request to the IMFDB API endpoint
    data = api_request(f"https://www.imfdb.org/api.php?action=query&list=categorymembers&cmtitle={cmtitle}&format={format}")

    # Error Handling
    if data is None:
        print("ERROR: query_categorymembers(): Data is None!")
        return None

    #Initialize list
    categorymembers = []

    # Loop through the first batch of category members
    for member in data["query"]["categorymembers"]:
        print(f"DEBUG: query_categorymembers(): Adding {member['title']}")
        categorymembers.append(member)

    # Continue fetching while there is something to be fetched
    while "continue" in data:
        data = api_request(f"https://www.imfdb.org/api.php?action=query&list=categorymembers&cmtitle={cmtitle}&format={format}&cmcontinue={data['continue']['cmcontinue']}")
        
        # Error Handling
        if data is None:
            print(f"ERROR: query_categorymembers(): Data is None in continuation batch {data['continue']['cmcontinue']}")
            return None
            
        # Loop through continuation batch:
        for member in data["query"]["categorymembers"]:
            print(f"DEBUG: query_categorymembers(): Adding {member['title']}")
            categorymembers.append(member)

    return categorymembers

def populate_actors_table():
    actors = query_categorymembers("Category:Actor", "json")

    for actor in actors:

        actorpageid = str(actor['pageid'])
        actorurl = f"https://www.imfdb.org/index.php?curid={actorpageid}"
        actorpagecontent = get_page_text_by_id(actorpageid)
        actorname = str(actor['title'])
        if "Category:" in actorname:
            continue
        print(f"INSERTing: {actorname}, {actorpageid}")
        statement = "INSERT INTO actors (actorurl, actorpageid, actorpagecontent, actorname) VALUES (%s, %s, %s, %s)"
        cursor.execute(statement, (actorurl, actorpageid, actorpagecontent, actorname))
    
    cnx.commit()

def populate_movies_table():
    movies = query_categorymembers("Category:Movie", "json")

    for movie in movies:

        moviepageid = str(movie['pageid'])
        movieurl = f"https://www.imfdb.org/index.php?curid={moviepageid}"
        moviepagecontent = get_page_text_by_id(moviepageid)
        movietitle = str(movie['title'])
        if "Category:" in movietitle:
            continue
        print(f"DEBUG: populate_movies_table(): INSERTing {movietitle}, {moviepageid}")
        statement = "INSERT INTO movies (movieurl, moviepageid, moviepagecontent, movietitle) VALUES (%s, %s, %s, %s)"
        cursor.execute(statement, (movieurl, moviepageid, moviepagecontent, movietitle))
    
    cnx.commit()

def populate_tvseries_table():
    tvseries = query_categorymembers("Category:Television", "json")

    for series in tvseries:

        tvseriespageid = str(series['pageid'])
        tvseriesurl = f"https://www.imfdb.org/index.php?curid={tvseriespageid}"
        tvseriespagecontent = get_page_text_by_id(tvseriespageid)
        tvseriestitle = str(series['title'])
        if "Category:" in tvseriestitle:
            continue
        print(f"INSERTing: {tvseriestitle}, {tvseriespageid}")
        statement = "INSERT INTO tvseries (tvseriesurl, tvseriespageid, tvseriespagecontent, tvseriestitle) VALUES (%s, %s, %s, %s)"
        cursor.execute(statement, (tvseriesurl, tvseriespageid, tvseriespagecontent, tvseriestitle))
    
    cnx.commit()

def populate_firearms_table_minimally():
    # Populates the table with a rough skeleton only, not including singles extracted from multi articles
    firearms = query_categorymembers("Category:Gun", "json")

    for firearm in firearms:

        firearmpageid = str(firearm['pageid'])
        firearmurl = f"https://www.imfdb.org/index.php?curid={firearmpageid}"
        firearmpagecontent = get_page_text_by_id(firearmpageid)
        firearmtitle = str(firearm['title'])
        if "Category:" in firearmtitle:
            continue
        print(f"DEBUG: populate_firearms_table_minimally(): INSERTing {firearmtitle}, {firearmpageid}")
        statement = "INSERT INTO firearms (firearmurl, firearmpageid, firearmpagecontent, firearmtitle) VALUES (%s, %s, %s, %s)"
        cursor.execute(statement, (firearmurl, firearmpageid, firearmpagecontent, firearmtitle))
    
    cnx.commit()

def update_firearm_html_by_uuid(uuid):
    # Use with care! This will break multis because it pulls html from the online article in IMFDB! 
    statement = "SELECT firearmpageid FROM firearms WHERE firearmid = %s"
    cursor.execute(statement, (uuid,))
    if cursor.rowcount == 1:
        firearmpageid = cursor.fetchone()[0]
        firearmpagecontent = get_page_text_by_id(firearmpageid)
        print(f"DEBUG: update_firearm_html_by_uuid(): UPDATING html for {uuid}")
        statement = "UPDATE firearms SET firearmpagecontent = %s WHERE firearmid = %s"
        cursor.execute(statement, (firearmpagecontent, uuid,))
        cnx.commit()
    else:
        print(f"ERROR: update_firearm_html_by_uuid(): Can not update. Unexpected number of rows returned for {uuid}!")

def get_redirects_by_pageid(pageid):
    # Some pageids are merely redirects others. Since movie or tvseries appearances may link to a redirect, we have
    # to grab those and store them in a table to check whether any given pageid is a redirect.
    data = api_request(f"https://www.imfdb.org/api.php?action=query&prop=redirects&pageids={pageid}&format=json")

    redirects = {}

    for page in data["query"]["pages"]:
        if "redirects" not in data["query"]["pages"][page]:
            return None
        for redirect in data["query"]["pages"][page]["redirects"]:
            redirects[redirect["pageid"]] = redirect["title"]

    return redirects 

def is_disambiguation_page(link):
    # Rudimentary check for whether a given page is a disambiguation page. We want to avoid parsing those.
    # There may be exceptions and corner cases where this doesn't give the correct response!
    response = requests.get(f"https://www.imfdb.org/{link}")
    soup = BeautifulSoup(str(response.text), 'html.parser')

    # This logic didn't work in several cases and has been improved upon below.
    #catlinks = soup.find_all('div', class_='mw-normal-catlinks')
    #if catlinks is not None:
    #    for child in catlinks[0].children:
    #        # check if the child element is an <ul>
    #        if child.name == 'ul':
    #            # loop through each <li> in the <ul>
    #            for li in child.find_all('li'):
    #                # check if the <li> contains an <a> with href = '/wiki/Category:Disambiguation_pages'
    #                if li.find('a', href='/wiki/Category:Disambiguation_pages'):
    #                    return True

    h1 = soup.find_all('h1')
    if h1 is not None:
        if "(disambiguation)" in h1[0].text:
            return True
        else:
            return False
    else:
        print(f"ERROR: is_disambiguation_page(): Page does not contain an h1 element.")
    print(f"ERROR: is_disambiguation_page(): Check failed.")
    #print(response.text)
    return None

# Dicts and lists

# Wiki tables may sometimes use the terms in this list in their 'Actor' column.
# To avoid registering them as actual actors in our database, we avoid them.
actor_false_positives = ["","(uncredited)", "(Uncredited)", "Uncredited", "uncredited", ".", "various", "Various", "Unknown", "unknown", "various", "Various", "multiple","multiple",
                         "—", "Multiple actors", "-", "varios actors", "multiple actors", "Various others", "Varios Actors", "Various thugs", "Various extras", "Curtis Taylor, Various actors",
                         "Various Actors", "Various actors", "Various characters", "Various", "various actors", "Multiple actors", "uncredited actor"]

# The index which corresponds to a database column when fetching all columns from the firearms table
firearms_dict = {
    "firearmid" : 0,
    "firearmurl" : 1,
    "parentfirearmid" : 2,
    "firearmpageid" : 3,
    "firearmpagecontent" : 4,
    "specificationid" : 5,
    "firearmtitle" : 6,
    "firearmversion" : 7,
    "isfamily" : 8,
    "isfictional" : 9
}

def get_page_content_from_db(pageid, table):
    # Use with care! When used in conjunction with firearms, this only works with firearms that are NOT children
    # In most cases, it is advisable to fetch content by uuid with get_page_content_from_db_by_uuid()
    if table in ["tvseries"]:
        content = f"{table}pagecontent"
        id = f"{table}id"
    elif table in ["actors", "movies", "firearms"]:
        singular = table.rstrip("s")
        content = f"{singular}pagecontent"
        id = f"{singular}pageid"
    else:
        print(f"ERROR: get_page_content_from_db(): {table} is not a valid table!")
        return None
    print(f"DEBUG: get_page_content_from_db(): Fetching {content} from {table} where {id} equals '{pageid}'.")
    statement = "select {} from {} where {} = '{}';".format(content, table, id, pageid)
    if table == "firearms": # If the firearms table is queried, filter out child firearm rows
        statement = "select {} from firearms where {} = '{}' and parentfirearmid is null;".format(content, id, pageid)
    cursor.execute(statement)
    return cursor.fetchone()[0]

def get_page_content_from_db_by_uuid(uuid, table):
    # This works with all pages, including firearm children, but requires the uuid as key
    if table in ["tvseries"]:
        content = f"{table}pagecontent"
        id = f"{table}id"
    elif table in ["actors", "movies", "firearms"]:
        singular = table.rstrip("s")
        content = f"{singular}pagecontent"
        id = f"{singular}id"
    else:
        print(f"ERROR: get_page_content_from_db(): {table} is not a valid table!")
        return None

    statement = "select {} from {} where {} = '{}';".format(content, table, id, uuid)
    cursor.execute(statement)
    return cursor.fetchone()[0]

def update_firearms_isfictional():
    # Sets the boolean flag for fictional firearms for all firearms
    statement = "UPDATE firearms SET isfictional = FALSE WHERE NOT firearmtitle LIKE '(%) -%';"
    cursor.execute(statement)
    statement = "UPDATE firearms SET isfictional = TRUE WHERE firearmtitle LIKE '(%) -%';"
    cursor.execute(statement)
    cnx.commit()

def is_multi_gun_page(pageid):
    # Check to determine whether a given page is a multi gun page composed of singles
    # Exceptions
    if (pageid == "464719" or pageid == "314208"): #Both of these have a table of contents despite being singles
        return False

    # If there are multiple h1s in an article, which are not See Also or Specification, it's a multi-gun page
    soup = soup = BeautifulSoup(get_page_content_from_db(pageid, "firearms"), 'html.parser')

    toctitle = soup.find("div", class_="toctitle") #If there is no table of contents, we don't need to check further, it's not multi-gun
    if toctitle is None:
        return False

    see_also = soup.find(id = "See_Also")
    if see_also is not None:
        if see_also.parent.name == "h1":
            see_also.parent.extract()

    spec = soup.find(id = "Specifications")
    if spec is not None:
        if spec.parent.name == "h1":
            spec.parent.extract()

    h1_tags = soup.find_all("h1")
    count = len(h1_tags)

    if count > 1:
        return True
    else:
        return False
    
def update_firearms_isfamily():
    # We assume a firearm is a family when it is named 'series' or is a multi-gun page
    keyword1 = "series"
    keyword2 = "Series"
    statement = "UPDATE firearms set isfamily = FALSE WHERE NOT (firearmtitle LIKE '%%%s%%' OR firearmtitle LIKE '%%%s%%' OR firearmtitle = 'Air Guns')" % (keyword1, keyword2)
    cursor.execute(statement)
    statement = "UPDATE firearms set isfamily = TRUE WHERE (firearmtitle LIKE '%%%s%%' OR firearmtitle LIKE '%%%s%%' OR firearmtitle = 'Air Guns')" % (keyword1, keyword2)
    cursor.execute(statement)

    statement = "SELECT * FROM firearms"
    cursor.execute(statement)
    firearms = cursor.fetchall()
    for firearm in firearms:
        if (is_multi_gun_page(pageid=firearm[3]) and firearm[8] == False): # If we have determined the article is multi-gun, it's a family
            statement = "UPDATE firearms set isfamily = TRUE WHERE firearmid = '%s'" % (firearm[0])
            cursor.execute(statement)
        if firearm[2] is not None: # Child firearms are never families 
            statement = "UPDATE firearms set isfamily = FALSE WHERE firearmid = '%s'" % (firearm[0])
            cursor.execute(statement)

    cnx.commit()

def get_number_of_specifications(html_content):
    # Returns the number of firearm specifications found in the provided html
    soup = BeautifulSoup(html_content, 'html.parser')
    
    spec_tags = soup.find_all(id=lambda value: value and value.startswith("Specifications"))
    spec_count = len(spec_tags)

    print("The number of h2 tags with 'Specifications' is:", spec_count)
    return spec_count

def strip_spec_list_item(item):
    # Strip the : character from a specification list item
    index = item.index(":")
    return item[index + 1:].strip()

def get_single_specification(html_content, pageid=None):
    # Finds the first specification within any given html

    spec_dict = {
        "production":None,
        "type":None,
        "caliber":None,
        "capacity":None,
        "fire_modes":None
    }

    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all h1 headers in the content
    headers = soup.find_all("h1")

    if (headers is None or len(headers) == 0):
        if pageid is not None:
            print(f"ERROR: get_first_specification(): {pageid} does not contain any headers!")
            return

    # Page Title
    title = headers[0].text

    # Find the first Element with the Specifications id
    span = soup.find(id = "Specifications")
    if span is None:
        print("ERROR: get_first_specification(): No <span> tag with id = 'Specifications' was found!")
        return

    spec_lists = span.parent.find_next_siblings("ul")

    # Each spec row is its own unordered list with only a single list item
    if spec_lists is None:
        print("ERROR: get_first_specification(): No <ul> tags were found!")
        return

    specifications = [li.text for ul in spec_lists for li in ul.find_all('li')]

    if specifications is None:
        print("ERROR: get_first_specification(): No <li> tags were found!")
        return

    # Iterate through the list items and set a dict for each
    for item in specifications:
        if "Type:" in item:
            spec_dict["type"] = strip_spec_list_item(item)
        elif "Caliber:" in item:
            spec_dict["caliber"] = strip_spec_list_item(item)
        elif "Feed System" in item:
            spec_dict["capacity"] = strip_spec_list_item(item)
        elif "Capacity:" in item:
            spec_dict["capacity"] = strip_spec_list_item(item)
        elif "Fire Modes:" in item:
            spec_dict["fire_modes"] = strip_spec_list_item(item)
    
    # Initialize with None so we can check later if a value was extracted from the HTML
    production = None

    # Determine whether a <p> tag containing a date exists
    possible_p_tag = span.parent.find_next_sibling()
    if possible_p_tag is not None:
        if possible_p_tag.name == "p" and re.match(r"\(\.*\d{4}.*\)",str(possible_p_tag.text)):
            production = possible_p_tag.text
            match = re.search(r"\(.*(\d{4})s?\s*(-\s|–\s)(\d{4}|Present)s?.*\)", production)
            if match is not None:
                production_year = match.group(1).strip()
                production_end_year = match.group(3).strip()
                production = f"({production_year} - {production_end_year})"
            # Add it to the specification
            spec_dict["production"] = production.rstrip("\n")
        
    return spec_dict

def articles_has_h1_variants(soup):
# Some firearm pages have variants ("Military, Civilian, etc.") as their h1, instead of different models
    if soup.find(id = "Specifications") is not None:
        first_specification_header = soup.find(id = "Specifications").parent
        if first_specification_header.name == "h3":
            return True
        else:
            return False
    else: # If the table of contents has a depth of 3 or more, we also assume variants
        toctitle = soup.find("div", class_="toctitle")
        if toctitle is not None:
            toc = toctitle.find_next_sibling("ul")
            regex = re.compile(r'(\d\.){2,}\d')
            for li in toc.find_all('li'):
                if regex.search(li.text):
                    return True
            return False
    return None

def generate_firearms_from_multi(html_content, url, pageid, parentuuid):
    # This function splits multi-gun pages at every h1, if it doesn't use h1s as variants, and at every h2, if it does.

    soup = BeautifulSoup(html_content, 'html.parser')

    firearmtitle = None
    content = ""
    version = None

    see_also = soup.find(id = "See_Also")
    if see_also is not None:
        if see_also.parent.name == "h1":
            see_also.parent.extract()

    spec = soup.find(id = "Specifications")
    if spec is not None:
        if spec.parent.name == "h1":
            h1spec= spec.parent.extract()

    if articles_has_h1_variants(soup): # If it has variants in h1...
        headers = soup.find_all("h1")
        headers.pop(0) #Skip the first one, since its the page heading
        for h1 in headers:
            version = h1.text
            headers2 = h1.find_next_siblings("h2")
            for h2 in headers2:
                slices = []
                slices.append(h2)
                firearmtitle = h2.text
                content = ""
                for slice in h2.find_next_siblings():
                    if (slice.name == "h2" or slice.name == "h1"):
                        break
                    slices.append(slice.extract())
                # Now that we have built up our slices of html, it's time to insert
                for slice in slices:
                    content = content+str(slice)
                if (content == "" or firearmtitle is None or version is None):
                    print(f"ERROR: generate_firearm_from_multi(): {pageid} produced empty version, content or title!")
                    continue
                if firearmtitle in ["Video Games", "Film", "Television", "Anime"]:
                    print(f"ERROR: generate_firearm_from_multi(): Version check failed for {pageid}!")
                    continue
                print(f"DEBUG: generate_firearms_from_multi: INSERTing {firearmtitle}, {pageid}, {parentuuid}")
                statement = "INSERT INTO firearms (firearmurl, parentfirearmid, firearmpageid, firearmpagecontent, firearmtitle, isfamily, firearmversion) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(statement, (url, parentuuid, pageid, content,  firearmtitle, 'FALSE', version))
                
    else: # If it doesn't have variants in h1...
        headers = soup.find_all("h1")
        headers.pop(0) # Skip the first one
        for h1 in headers:
            slices = []
            slices.append(h1)
            firearmtitle = h1.text
            content = ""
            for slice in h1.find_next_siblings():
                if slice.name == "h1":
                    break
                slices.append(slice.extract())
            # Now that we have built up our slices of html, it's time to insert
            for slice in slices:
                content = content+str(slice)
            if (content == "" or firearmtitle is None):
                print(f"ERROR: generate_firearm_from_multi(): {pageid} produced empty content or title!")
                continue
            if firearmtitle in ["Video Games", "Film", "Television", "Anime"]:
                print(f"ERROR: generate_firearm_from_multi(): Version check failed for {pageid}!")
                continue
            print(f"DEBUG: generate_firearms_from_multi(): INSERTing {firearmtitle}, {pageid}, {parentuuid}")
            statement = "INSERT INTO firearms (firearmurl, parentfirearmid, firearmpageid, firearmpagecontent, firearmtitle, isfamily) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(statement, (url, parentuuid, pageid, content,  firearmtitle, 'FALSE'))

    if articles_has_h1_variants(soup) is None:
        print(f"ERROR: generate_firearm_from_multi(): Version check failed for {pageid}!")

def generate_firearms_from_multis():
    # Generates single firearm table entries from all the multi-gun pages and families
    statement = "SELECT * FROM firearms WHERE isfamily = 'True' AND parentfirearmid IS NULL;"
    cursor.execute(statement)
    firearms = cursor.fetchall()

    for firearm in firearms:
        generate_firearms_from_multi(html_content=firearm[4], url=firearm[1], pageid=firearm[3], parentuuid=firearm[0])
    cnx.commit()

def check_for_family_candidates():
# Debugging function to check on potential is_Family candidates
    statement = "SELECT * FROM firearms"
    cursor.execute(statement)
    firearms = cursor.fetchall()
    
    with open('candidates.txt', 'w') as writer:
        for firearm in firearms:
            if (is_multi_gun_page(pageid=firearm[3]) and firearm[8] == False):
                writer.write(f"{firearm[3]}\n")

def populate_specs_for_singles():
    # Populates the specifications table for single gun entries
    statement = "SELECT * FROM firearms WHERE isfamily = 'False';"
    cursor.execute(statement)
    firearms = cursor.fetchall()

    for firearm in firearms:
        print(f"Fetching spec for: {firearm[3]}")
        spec = get_single_specification(html_content=firearm[4], pageid=firearm[3])
        if spec is not None:
            print(f"INSERTing: {firearm[3]} specification")
            statement = "INSERT INTO specifications (firearmid, type, caliber, capacity, firemode, productiontimeframe) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(statement, (firearm[0], spec["type"], spec["caliber"], spec["capacity"], spec["fire_modes"], spec["production"]))

def populate_specs_for_multies():
    # Populates the specification table for multi-gun entries
    # We handle family rows first, trying to determine whether there is a single spec in an h1 tag for the entire page
    statement = "SELECT * FROM firearms WHERE isfamily = 'True' and parentfirearmid IS NULL"
    cursor.execute(statement)
    firearms = cursor.fetchall()

    for firearm in firearms:
        html_content = firearm[4]
        soup = BeautifulSoup(html_content, "html.parser")
        spec_tag = soup.find_next(id = "Specifications") # Find the first spec
        if spec_tag is not None:
            if spec_tag.parent.name == "h1": # If it's nested in an h1...
                print(f"DEBUG: populate_specs_for_multies(): Fetching spec for {firearm[3]}")
                spec = get_single_specification(html_content=firearm[4], pageid=firearm[3])
                if spec is not None:
                    print(f"DEBUG: populate_specs_for_multies(): INSERTing {firearm[3]} specification")
                    statement = "INSERT INTO specifications (firearmid, type, caliber, capacity, firemode, productiontimeframe) VALUES (%s, %s, %s, %s, %s, %s)"
                    cursor.execute(statement, (firearm[0], spec["type"], spec["caliber"], spec["capacity"], spec["fire_modes"], spec["production"]))
    # Same procedure for the child rows
    statement = "SELECT * FROM firearms WHERE parentfirearmid IS NOT NULL"
    cursor.execute(statement)
    firearms = cursor.fetchall()

    for firearm in firearms:
        print(f"Fetching spec for: {firearm[3]}")
        spec = get_single_specification(html_content=firearm[4], pageid=firearm[3])
        if spec is not None:
            print(f"INSERTing: {firearm[3]} specification")
            statement = "INSERT INTO specifications (firearmid, type, caliber, capacity, firemode, productiontimeframe) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(statement, (firearm[0], spec["type"], spec["caliber"], spec["capacity"], spec["fire_modes"], spec["production"]))

def populate_specifications_table():
    # Do both with a single function call
    populate_specs_for_singles()
    populate_specs_for_multies()
    cnx.commit()

def extract_dataframe_from_html_table(html_content, table_name, uuid):
    # This is used to find and extract the first table (valid names are 'Film' and 'Television' on any given page) and return it as a data frame
    if table_name not in ["Film", "Television"]:
        print(f"ERROR: extract_dataframe_from_html(): table {table_name} not found in list of valid table names!")
        return
    soup = BeautifulSoup(html_content, "html.parser")
    regex = re.compile(fr'^{table_name}(_\d*)?')
    span = soup.find('span', {'id': regex})
    if span is None:
        print(f"WARNING: extract_dataframe_from_html_table(): No span with id {table_name} was found in the html content of {uuid}!")
        return None
    table = span.parent.find_next_sibling("table")
    if table is None:
        print(f"ERROR: extract_dataframe_from_html_table(): No table was found in the html content of {uuid}!")
        return None
    just_the_table = str(table)
    df = pd.read_html(just_the_table, extract_links='body')
    return df[0]

def get_uuid_by_pageid(pageid, table):
    # This only works with tables where the pageid is unique, ie. not with firearms
    if table in ["tvseries"]:
        uuid = f"{table}id"
        id = f"{table}pageid"
    elif table in ["actors", "movies"]:
        singular = table.rstrip("s")
        uuid = f"{singular}id"
        id = f"{singular}pageid"
    else:
        print(f"ERROR: get_page_content_from_db(): {table} is not a valid table (actors, movies, tvseries)!")
        return None

    statement = f"select {uuid} from {table} where {id} = '{pageid}';"
    cursor.execute(statement)
    print(f"DEBUG: get_uuid_by_pageid(): Fetching uuid for page with id {pageid} from {table}") # DEBUG
    if cursor.rowcount == 1:
        return cursor.fetchone()[0]
    else:
        print(f"ERROR: get_uuid_by_pageid(): Unexpected number of rows ({cursor.rowcount}) returned while fetching pageid {pageid} from {table}!")
        return None
    
def populate_redirects_table():
    # Populate the redirects table with entries showing to and from
    statement = "SELECT * FROM movies WHERE moviepageid != '0'"
    cursor.execute(statement)
    movies = cursor.fetchall()

    for movie in movies:
        redirects = get_redirects_by_pageid(movie[3])
        print(f"DEBUG: populate_redirects_table(): Currently working on redirects for {movie[3]}:{movie[1]}")

        time.sleep(0.1)

        if redirects is not None:
            for key,value in redirects.items():
                statement = "INSERT INTO redirects (topageid, totitle, frompageid, fromtitle) VALUES (%s, %s, %s, %s)"
                cursor.execute(statement, (movie[3], movie[1], key, value))

    cnx.commit()
    
    statement = "SELECT * FROM tvseries WHERE tvseriespageid != '0'"
    cursor.execute(statement)
    tvseries = cursor.fetchall()

    for series in tvseries:
        redirects = get_redirects_by_pageid(series[3])
        print(f"DEBUG: populate_redirects_table(): Currently working on redirects for {series[3]}:{series[1]}")

        time.sleep(0.1)

        if redirects is not None:
            for key,value in redirects.items():
                statement = "INSERT INTO redirects (topageid, totitle, frompageid, fromtitle) VALUES (%s, %s, %s, %s)"
                cursor.execute(statement, (series[3], series[1], key, value))
    cnx.commit()

    statement = "SELECT * FROM actors WHERE actorpageid != '0'"
    cursor.execute(statement)
    actors = cursor.fetchall()

    for actor in actors:
        redirects = get_redirects_by_pageid(actor[2])
        print(f"DEBUG: populate_redirects_table(): Currently working on redirects for {actor[2]}:{actor[4]}")

        time.sleep(0.1)

        if redirects is not None:
            for key,value in redirects.items():
                statement = "INSERT INTO redirects (topageid, totitle, frompageid, fromtitle) VALUES (%s, %s, %s, %s)"
                cursor.execute(statement, (actor[2], actor[4], key, value))

    cnx.commit()

    # For some actors the MW API does not return redirect pages, so we insert those manually:
    statements = ["INSERT INTO public.redirects (totitle, topageid, fromtitle, frompageid) VALUES('André Holland', '130821', 'Andre Holland', '324440');",
                "INSERT INTO public.redirects (totitle, topageid, fromtitle, frompageid) VALUES('Ramón Rodríguez', '112054', 'Ramon Rodriguez', '326018');",
                "INSERT INTO public.redirects (totitle, topageid, fromtitle, frompageid) VALUES('Ramón Franco', '15039', 'Ramon Franco', '146100');",
                "INSERT INTO public.redirects (totitle, topageid, fromtitle, frompageid) VALUES('Téa Leoni', '90060', 'Tea Leoni', '184140');",
                "INSERT INTO public.redirects (totitle, topageid, fromtitle, frompageid) VALUES('Kari Wührer', '66589', 'Kari Wuhrer', '202040');",
                "INSERT INTO public.redirects (totitle, topageid, fromtitle, frompageid) VALUES(NULL, 'Alexander Skarsgård', '56680', 'Alexander Skarsgard', '80196');"]
    
    for statement in statement:
        cursor.execute(statement)
    cnx.commit()

def write_to_skip_file(uuid):
    # Since populating the junction tables takes a long time and may result in a timeout because we are locked out of the API for making
    # too many requests, we keep track of entries we finished working on in case we need to restart.
    with open('skip.csv', 'a', newline='') as file:
        # Create a CSV writer object
        csv_writer = csv.writer(file)

        # Write some rows to the CSV file
        csv_writer.writerow([uuid])

def clear_skip_file():
    # We clear the skip file list when we're done.
    with open('skip.csv', 'w', newline='') as file:
        file.write('')

def read_from_skip_file(uuid):
    # Checks whether a uuid appears in the skip list because it has already been covered
    with open('skip.csv', 'r') as file:
        csv_reader = csv.reader(file)
        
        for row in csv_reader:
        # Check if the search string is in any of the fields
            if any(uuid in field for field in row):
                return True
        return False
    
def insert_dummy_actor():
    # If a firearm appearance is not clearly linked to a single and/or named actor, we associate it with a dummy entry instead 
    statement = "select actorid from actors where actorpageid = '0' and actorname = 'Dummy / Uncredited Extra';"
    cursor.execute(statement)
    if cursor.rowcount > 0:
        return cursor.fetchone()[0] # Check for possible duplicate, if it already exists, we return the uuid

    statement = "INSERT INTO actors (actorpageid, actorname) VALUES ('0', 'Dummy / Uncredited Extra')"
    cursor.execute(statement)
    cnx.commit()
    statement = "select actorid from actors where actorpageid = '0' and actorname = 'Dummy / Uncredited Extra';"
    cursor.execute(statement)
    return cursor.fetchone()[0]

def insert_actor_without_page(name):
    # Some actors don't have a wiki page yet. In this case we insert them into the actors table as needed.
    statement = "select actorid from actors where actorpageid = '0' and actorname = %s;"
    cursor.execute(statement, (name,))
    if cursor.rowcount > 0:
        return cursor.fetchone()[0] # Check for possible duplicate, if it already exists, we return the uuid

    statement = "INSERT INTO actors (actorpageid, actorname) VALUES ('0', %s)"
    cursor.execute(statement, (name,))
    cnx.commit()
    statement = "select actorid from actors where actorpageid = '0' and actorname = %s;"
    cursor.execute(statement, (name,))
    print(f"DEBUG: insert_actor_without_page(): INSERTing actor {name}.")
    return cursor.fetchone()[0]

def insert_movie_without_page(title):
    # See avove. Same is true for some movies.
    statement = "select movieid from movies where moviepageid = '0' and movietitle = %s;"
    cursor.execute(statement, (title,))
    if cursor.rowcount > 0:
        return cursor.fetchone()[0] # Check for possible duplicate, if it already exists, we return the uuid

    statement = "INSERT INTO movies (moviepageid, movietitle) VALUES ('0', %s)"
    cursor.execute(statement, (title,))
    cnx.commit()
    statement = "select movieid from movies where moviepageid = '0' and movietitle = %s;"
    cursor.execute(statement, (title,))
    print(f"DEBUG: insert_movie_without_page(): INSERTing movie {title}.")
    return cursor.fetchone()[0]

def insert_tvseries_without_page(title):
    # See above. ... and television shows.
    statement = "select tvseriesid from tvseries where tvseriespageid = '0' and tvseriestitle = %s;"
    cursor.execute(statement, (title,))
    if cursor.rowcount > 0:
        return cursor.fetchone()[0] # Check for possible duplicate, if it already exists, we return the uuid

    statement = "INSERT INTO tvseries (tvseriespageid, tvseriestitle) VALUES ('0', %s)"
    cursor.execute(statement, (title,))
    cnx.commit()
    statement = "select tvseriesid from tvseries where tvseriespageid = '0' and tvseriestitle = %s;"
    cursor.execute(statement, (title,))
    print(f"DEBUG: insert_tvseries_without_page(): INSERTing tvseries {title}.")
    return cursor.fetchone()[0]

def get_redirect_pageid(pageid):
    # Look up whether the pageid is a redirect to a different pageid. If not, return it unchanged
    statement = "SELECT topageid FROM redirects WHERE frompageid = %s"
    cursor.execute(statement, (pageid,))
    if cursor.rowcount == 1:
        return cursor.fetchone()[0]
    else:
        return pageid
    
def handle_disambiguation_page(title, date):
    # Attempt to make sense of disambiguation pages in order to find the page they correspond with
    # url must take the form of '/wiki/Elke_Sommer'
    title = title.replace(" ", "_")
    url = f"/wiki/{title}_({date})"
    return get_page_id_by_url(url, "json")

def populate_movies_actors_firearms_table(dummy_uuid):
    # Populate the junction table linking appearances of firearms in movies to their actors

    statement = "SELECT * FROM firearms ORDER BY firearmpageid ASC"
    cursor.execute(statement)
    firearms = cursor.fetchall()

    for firearm in firearms:
        uuid = firearm[0]
        html = get_page_content_from_db_by_uuid(uuid, "firearms")
        df = extract_dataframe_from_html_table(html, "Film", uuid)
        if df is None:
            continue
        
        print(f"DEBUG: populate_movies_actors_firearms_table(): Currently working on appearances of {uuid}")
        if read_from_skip_file(uuid):
            print("Skipping...")
            continue

        # Columns don't have consistent naming, so we have do go through this and match them with regex
        title_col_name = actor_col_name = character_col_name = note_col_name = date_col_name = None

        title_regex = re.compile('.*(Title|Film|Movie|Titla).*', re.IGNORECASE)
        actor_regex = re.compile('.*Actor.*', re.IGNORECASE)
        character_regex = re.compile('.*(Character|Charcter).*', re.IGNORECASE)
        note_regex = re.compile('.*(Note|Notation).*', re.IGNORECASE)
        date_regex = re.compile('.*(Date|Year).*', re.IGNORECASE)

        for col_name in df.columns:
            if title_regex.match(col_name):
                title_col_name = col_name
            elif actor_regex.match(col_name):
                actor_col_name = col_name
            elif character_regex.match(col_name):
                character_col_name = col_name
            elif note_regex.match(col_name):
                note_col_name = col_name
            elif date_regex.match(col_name):
                date_col_name = col_name
        
        if any(var is None for var in [title_col_name, actor_col_name, character_col_name, note_col_name, date_col_name]):
            print(f"WARNING: populate_movies_actors_firearms_table(): The html content in '{uuid}' has one or more unmatched columns in its 'Film' table")

        # Extract the row values and INSERT them
        for i in range(len(df.index)):
            title = actor = character = note = date = "NULL"
            title = (df[title_col_name][i])[0]
            title_link = (df[title_col_name][i])[1]
            if actor_col_name is not None:
                actor = (df[actor_col_name][i])[0]
                actor_link = (df[actor_col_name][i])[1]
            character = (df[character_col_name][i])[0]
            if note_col_name is not None:
                note = (df[note_col_name][i])[0]
            if type(df[date_col_name][i]) == float: # This applies if the page author used rowspan but forgot to include an empty note column
                match = re.match(r"\d{4}", note)
                if match:
                    date = note
            else:
                date = (df[date_col_name][i])[0]

            # Page id's can be assigned using the second element of each tuple, which may contain an html link found in each cell.
            # This is only attempted when the actor and title columns actually contain a valid title or actor.
            if (not(pd.isna(actor) or actor is None)) and (actor not in actor_false_positives): # Actor name is valid
                if (actor_link is not None and actor_link != "" and "redlink=1" not in actor_link): # Actor name is linked to an IMFDB wiki page
                    actor_pageid = get_page_id_by_url(actor_link,"json")
                    actor_pageid = get_redirect_pageid(actor_pageid) # Check for redirect page id
                    actor_uuid = get_uuid_by_pageid(actor_pageid, "actors")
                else: # If we have a valid actor name, but it is not linked to a page, we insert the actor into the database with pageid 0
                    actor_uuid = insert_actor_without_page(actor)
            
            if not (pd.isna(title) or title == "" or title is None): # Movie title is not blank
                if (title_link is not None and title_link != "" and "redlink=1" not in title_link): # Movie title is linked to an IMFDB wiki page
                    title_pageid = get_page_id_by_url(title_link,"json") 
                    title_pageid = get_redirect_pageid(title_pageid) # Check for redirect page id        
                    title_uuid = get_uuid_by_pageid(title_pageid, "movies")
                else: # If we have a movie title that's not blank, but it is not linked to a page, we insert the movie into the database with pageid 0
                    title_uuid = insert_movie_without_page(title)

            # Check if the title_uuid points to a disambiguation page
            if is_disambiguation_page(title_link):
                title_uuid = get_uuid_by_pageid(handle_disambiguation_page(title, date), "movies")
            
            # Some of the values may be NaN. We set those to NULL
            if pd.isna(title) or title == "" or title is None:
                title_uuid = None
            if pd.isna(actor) or actor == "" or actor is None or actor in actor_false_positives:
                actor_uuid = dummy_uuid
            if pd.isna(character) or character == "":
                character = None
            if pd.isna(note) or note == "":
                note = None
            if pd.isna(date) or date == "":
                date = None
            else:
                date = int(date)

            # If after error handling the the title_uuid is can still not be determined, we skip the table row
            if title_uuid == "" or title_uuid is None:
                print(f"WARNING: populate_movies_actors_firearms_table(): Skipping entire table row {firearm[3]} appearence in {title} used by {actor}!")
                continue

            print(f"DEBUG: INSERTing populate_movies_actors_firearms_table(): {firearm[3]} appearence in {title} used by {actor} in {date}")
            statement = "INSERT INTO movies_actors_firearms (movieid, firearmid, character, note, year, actorid) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(statement, (title_uuid, uuid, character, note, date, actor_uuid))
        cnx.commit()
        write_to_skip_file(uuid)
    cnx.commit()
    clear_skip_file()
    return

def populate_tvseries_actors_firearms_table(dummy_uuid):
    # See above. Do the same for TV shows.

    statement = "SELECT * FROM firearms ORDER BY firearmpageid ASC"
    cursor.execute(statement)
    firearms = cursor.fetchall()

    for firearm in firearms:
        uuid = firearm[0]
        print(f"DEBUG: populate_tvseries_actors_firearms_table(): Currently working on appearances of {uuid}")
        html = get_page_content_from_db_by_uuid(uuid, "firearms")
        df = extract_dataframe_from_html_table(html, "Television", uuid)
        if df is None:
            continue
        
        if read_from_skip_file(uuid):
            print("Skipping...")
            continue

        # Columns don't have consistent naming, so we have do go through this and match them with regex
        title_col_name = actor_col_name = character_col_name = note_col_name = date_col_name = None

        title_regex = re.compile('.*(Title|Series|Show|Serie|Titla).*', re.IGNORECASE)
        actor_regex = re.compile('.*Actor.*', re.IGNORECASE)
        character_regex = re.compile('.*(Character|Charcter).*', re.IGNORECASE)
        note_regex = re.compile('.*(Note|Notation|Episode|Episodes).*', re.IGNORECASE)
        date_regex = re.compile('.*(Date|Year|Air|Run|Release).*', re.IGNORECASE)

        for col_name in df.columns:
            if title_regex.match(col_name):
                title_col_name = col_name
            elif actor_regex.match(col_name):
                actor_col_name = col_name
            elif character_regex.match(col_name):
                character_col_name = col_name
            elif note_regex.match(col_name):
                note_col_name = col_name
            elif date_regex.match(col_name):
                date_col_name = col_name
        
        if any(var is None for var in [title_col_name, actor_col_name, character_col_name, note_col_name, date_col_name]):
            print(f"WARNING: populate_tvseries_actors_firearms_table(): The html content in '{uuid}' has one or more unmatched columns in its 'Television' table")

        # Extract the row values and INSERT them
        for i in range(len(df.index)):
            title = actor = character = note = date = "NULL"
            title = (df[title_col_name][i])[0]
            title_link = (df[title_col_name][i])[1]
            if actor_col_name is not None:
                actor = (df[actor_col_name][i])[0]
                actor_link = (df[actor_col_name][i])[1]
            character = (df[character_col_name][i])[0]
            if note_col_name is not None:
                note = (df[note_col_name][i])[0]
            if type(df[date_col_name][i]) == float: # This applies if the page author used rowspan but forgot to include an empty note column
                match = re.match(r"\d{4}", note)
                if match:
                    date = note
            else:
                date = (df[date_col_name][i])[0]

            # Page id's can be assigned using the second element of each tuple, which may contain an html link found in each cell.
            # This is only attempted when the actor and title columns actually contain a valid title or actor.
            if (not(pd.isna(actor) or actor is None)) and (actor not in actor_false_positives): # Actor name is valid
                if (actor_link is not None and actor_link != "" and "redlink=1" not in actor_link): # Actor name is linked to an IMFDB wiki page
                    actor_pageid = get_page_id_by_url(actor_link,"json")
                    actor_pageid = get_redirect_pageid(actor_pageid) # Check for redirect page id
                    actor_uuid = get_uuid_by_pageid(actor_pageid, "actors")
                else: # If we have a valid actor name, but it is not linked to a page, we insert the actor into the database with pageid 0
                    actor_uuid = insert_actor_without_page(actor)
            
            if not (pd.isna(title) or title == "" or title is None): # Series title is not blank
                if (title_link is not None and title_link != "" and "redlink=1" not in title_link): # Series title is linked to an IMFDB wiki page
                    title_pageid = get_page_id_by_url(title_link,"json") 
                    title_pageid = get_redirect_pageid(title_pageid) # Check for redirect page id        
                    title_uuid = get_uuid_by_pageid(title_pageid, "tvseries")
                else: # If we have a series title that's not blank, but it is not linked to a page, we insert the series into the database with pageid 0
                    title_uuid = insert_tvseries_without_page(title)

            # Check if the title_uuid points to a disambiguation page
            if is_disambiguation_page(title_link):
                title_uuid = get_uuid_by_pageid(handle_disambiguation_page(title, date), "tvseries")
            
            # Some of the values may be NaN. We set those to NULL
            if pd.isna(title) or title == "" or title is None:
                title_uuid = None
            if pd.isna(actor) or actor == "" or actor is None or actor in actor_false_positives:
                actor_uuid = dummy_uuid
            if pd.isna(character) or character == "":
                character = None
            if pd.isna(note) or note == "":
                note = None
            if pd.isna(date) or date == "":
                date = None

            # If after error handling the the title_uuid can still not be determined, we skip the table row
            if title_uuid == "" or title_uuid is None:
                print(f"WARNING: populate_tvseries_actors_firearms_table(): Skipping entire table row {firearm[3]} appearence in {title} used by {actor}!")
                continue
            
            #print(f"Link: {actor_link}\npageid: {actor_pageid}\nuuid: {actor_uuid}")
            #print(actor_link)
            #print(actor_pageid)
            #print(actor_uuid)
            print(f"DEBUG: INSERTing populate_tvseries_actors_firearms_table(): {firearm[3]} appearence in {title} used by {actor} in {date}")
            statement = "INSERT INTO tvseries_actors_firearms (tvseriesid, firearmid, character, note, year, actorid) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(statement, (title_uuid, uuid, character, note, date, actor_uuid))
        cnx.commit()
        write_to_skip_file(uuid)
    cnx.commit()
    clear_skip_file()
    return

def extract_images_from_html(html):
    # Returns a list of URLs of all image tags in the given HTML
    soup = BeautifulSoup(html, 'html.parser')
    image_urls = [img['src'] for img in soup.find_all('img')]
    return image_urls

def populate_actor_images_table():
    statement = "SELECT * FROM actors"
    cursor.execute(statement)
    actors = cursor.fetchall()

    for actor in actors:
        uuid = actor[0]
        print(f"DEBUG: populate_actor_images_table(): Currently working on images in {uuid}")
        html = get_page_content_from_db_by_uuid(uuid, "actors")
        if html is None:
            continue
        urls = extract_images_from_html(html)
        if urls is None:
            continue
        for url in urls:
            if url in ("/images/thumb/4/4b/Discord-logo.jpg/20px-Discord-logo.jpg", "/resources/assets/poweredby_mediawiki_88x31.png"):
                continue
            print(f"DEBUG: populate_actor_images_table: INSERTING image with url '{url}' appearing in actor {uuid}")
            statement = "INSERT INTO actorimages (imageurl, actorid) VALUES (%s, %s)"
            cursor.execute(statement, (f"https://imfdb.org{url}", uuid))
    cnx.commit()
    return

def populate_actor_images_table():
    statement = "SELECT actorid FROM actors"
    cursor.execute(statement)
    actors = cursor.fetchall()

    for actor in actors:
        uuid = actor[0]
        print(f"DEBUG: populate_actor_images_table(): Currently working on images in {uuid}")
        html = get_page_content_from_db_by_uuid(uuid, "actors")
        if html is None:
            continue
        urls = extract_images_from_html(html)
        if urls is None:
            continue
        for url in urls:
            if url in ("/images/thumb/4/4b/Discord-logo.jpg/20px-Discord-logo.jpg", "/resources/assets/poweredby_mediawiki_88x31.png"):
                continue
            print(f"DEBUG: populate_actor_images_table: INSERTING image with url '{url}' appearing in actor {uuid}")
            statement = "INSERT INTO actorimages (imageurl, actorid) VALUES (%s, %s)"
            cursor.execute(statement, (f"https://imfdb.org{url}", uuid))
    cnx.commit()
    return

def populate_firearm_images_table():
    statement = "SELECT firearmid FROM firearms"
    cursor.execute(statement)
    firearms = cursor.fetchall()

    for firearm in firearms:
        uuid = firearm[0]
        print(f"DEBUG: populate_firearm_images_table(): Currently working on images in {uuid}")
        html = get_page_content_from_db_by_uuid(uuid, "firearms")
        if html is None:
            continue
        urls = extract_images_from_html(html)
        if urls is None:
            continue
        for url in urls:
            if url in ("/images/thumb/4/4b/Discord-logo.jpg/20px-Discord-logo.jpg", "/resources/assets/poweredby_mediawiki_88x31.png"):
                continue
            print(f"DEBUG: populate_firearm_images_table: INSERTING image with url '{url}' appearing in firearm {uuid}")
            statement = "INSERT INTO firearmimages (imageurl, firearmid) VALUES (%s, %s)"
            cursor.execute(statement, (f"https://imfdb.org{url}", uuid))
    cnx.commit()
    return

def populate_movie_images_table():
    statement = "SELECT movieid FROM movies"
    cursor.execute(statement)
    movies = cursor.fetchall()

    for movie in movies:
        uuid = movie[0]
        print(f"DEBUG: populate_movie_images_table(): Currently working on images in {uuid}")
        html = get_page_content_from_db_by_uuid(uuid, "movies")
        if html is None:
            continue
        urls = extract_images_from_html(html)
        if urls is None:
            continue
        for url in urls:
            if url in ("/images/thumb/4/4b/Discord-logo.jpg/20px-Discord-logo.jpg", "/resources/assets/poweredby_mediawiki_88x31.png"):
                continue
            print(f"DEBUG: populate_movie_images_table: INSERTING image with url '{url}' appearing in movie {uuid}")
            statement = "INSERT INTO movieimages (imageurl, movieid) VALUES (%s, %s)"
            cursor.execute(statement, (f"https://imfdb.org{url}", uuid))
    cnx.commit()
    return

def populate_tvseries_images_table():
    statement = "SELECT tvseriesid FROM tvseries"
    cursor.execute(statement)
    tvseries = cursor.fetchall()

    for series in tvseries:
        uuid = series[0]
        print(f"DEBUG: populate_tvseries_images_table(): Currently working on images in {uuid}")
        html = get_page_content_from_db_by_uuid(uuid, "tvseries")
        if html is None:
            continue
        urls = extract_images_from_html(html)
        if urls is None:
            continue
        for url in urls:
            if url in ("/images/thumb/4/4b/Discord-logo.jpg/20px-Discord-logo.jpg", "/resources/assets/poweredby_mediawiki_88x31.png"):
                continue
            print(f"DEBUG: populate_tvseries_images_table: INSERTING image with url '{url}' appearing in movie {uuid}")
            statement = "INSERT INTO tvseriesimages (imageurl, tvseriesid) VALUES (%s, %s)"
            cursor.execute(statement, (f"https://imfdb.org{url}", uuid))
    cnx.commit()
    return

# Main - This is where the magic happens.

#Populate the database skeleton (~250min Runtime):
populate_actors_table()
populate_movies_table()
populate_tvseries_table()
populate_firearms_table_minimally()

#Finalize the firearms table (~2min Runtime):
update_firearms_isfictional()
update_firearms_isfamily()
generate_firearms_from_multis()

# Populate the specifications table (~2min Runtime): 
populate_specifications_table() 

# Collect redirects (~202min Runtime):
populate_redirects_table()

# Populate junction tables (~950min Runtime):
dummy_uuid = insert_dummy_actor()
populate_movies_actors_firearms_table(dummy_uuid)
populate_tvseries_actors_firearms_table(dummy_uuid)

# Populate image tables (~9 min Runtime):
populate_actor_images_table()
populate_firearm_images_table()
populate_movie_images_table()
populate_tvseries_images_table()

# Keeping track of edge and corner cases:
# Solved - X
# Unsolved - !

# X HK416 second variant has full html for some reason
# X Author of Flammenwerfer 35 page can't spell table headers right
# X Same for DefTech 37mm GL
# X Notes column seems to be optional in Film and TV tables
# X Film and TV table columns may sometimes be in Spanish
# X The notes column may be called "Note", "Notes", "Notation" or "Notations"
# X Actors appear as NaN in dataframe if unable to be determined.
# X https://www.imfdb.org/index.php?curid=62 has just a single Spec at the beginning of the page
# X Child guns are currently NULL in isfictional column. -> isfictional should default to false
# X https://www.imfdb.org/index.php?curid=464719 Sage BML-37 has a table of contents despite being a single
# ! https://www.imfdb.org/index.php?curid=348107 HK AG Grenade Launchers are a weird mix of versioned and non-versioned, ie. live-fire models are non-versioned, non-firing replicas are versioned
# X https://www.imfdb.org/index.php?curid=3564 SIG P210 has its Video Game table nested in the Television segment
# X https://www.imfdb.org/index.php?curid=314208 Flintlock Musket has a table of contents despite being a single
# X Firearms may appear in a medium, but used by an unnamed actor or extra. Solution: Unnamed extra dummy actor
# X Movie pages may have redirects example: https://www.imfdb.org/index.php?curid=14246 (pageid in DB), https://www.imfdb.org/index.php?curid=26085 (pageid in html table)
# X TVSeries and movie may not have a linked page or may have a redlink, despite being valid titles
# X Actors also have redirects. See Brandon Faser
# X https://www.imfdb.org/index.php?curid=397370 The movie Weekend leads to a disambiguation page
# X https://www.imfdb.org/index.php?curid=10193 The Modern Family (series) entries are listed in the Film table
# X There are a metric crap-ton of movie pages that are a) missing in the movies category and therefore don't exist in the local database b) lead to disambiguation pages and are therefore resolved to an
# incorrect page id. Solution: Rewrite the junction table function to commit after every gun, write uuids of finished guns into a file and skip them during next execution.
# X skip csv should be deleted between populating junction tables
# X "False positive" missing actors: '.', 'Various', 'Uncredited', 'Danish nazis and resistance fighters' to be added to both junction table checks
# X Some deceased actors are not in the actors category
# X Some redirect pages are not provided by the API and have to be added manually
# ! https://www.imfdb.org/index.php?title=Heckler_%26_Koch_P7 is not formatted according to the template (no h1)
# ! Refactor population functions to extract functions that take just a single object as parameter