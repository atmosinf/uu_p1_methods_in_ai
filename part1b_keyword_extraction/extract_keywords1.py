import re

# all possible options from the database
pricerange_options = {'cheap', 'moderate', 'expensive', 'dontcare'}
area_options = {'north', 'south', 'east', 'west', 'centre', 'dontcare'}
food_options = {'italian','british','french','indian','chinese','japanese','thai','korean',
    'vietnamese','mediterranean','spanish','portuguese','greek','turkish',
    'american','mexican','european','bistro','gastropub','asian oriental','venetian',
    'dontcare'}

# mapping from keywords to possible options
pricerange_keyword_map = {
    "moderately": "moderate",
    "moderately priced": "moderate",
    "mid": "moderate",
	"midrange": "moderate",
	"mid-range": "moderate",
    "affordable": "moderate",
    "budget": "cheap",
	"low": "cheap",
	"inexpensive": "cheap",
    "pricey": "expensive",
	"high end": "expensive",
	"high-end": "expensive",
    "any": "dontcare",
	"any price": "dontcare",
    "dont care": "dontcare",
	"don't care": "dontcare",
    "doesnt matter": "dontcare",
	"doesn't matter": "dontcare",
}

area_keyword_map = {
    "center": "centre",
	"city center": "centre",
	"city centre": "centre",
	"downtown": "centre",
    "north part of town": "north",
	"south part of town": "south",
    "east part of town": "east",
	"west part of town": "west",
    "any": "dontcare",
	"anywhere": "dontcare",
    "dont care": "dontcare",
	"don't care": "dontcare",
    "doesnt matter": "dontcare",
	"doesn't matter": "dontcare",
}

food_keyword_map = {
    "europe": "european",
	"britain": "british",
	"portugese": "portuguese",
    "gastro pub": "gastropub",
	"asian-oriental": "asian oriental",
	"asian/oriental": "asian oriental",
    "any": "dontcare",
	"any food": "dontcare",
    "dont care": "dontcare",
	"don't care": "dontcare",
    "doesnt matter": "dontcare",
	"doesn't matter": "dontcare",
}

def clean_text(text: str):
    '''
    convert to lowercase and remove special characters and extra spaces
    '''
    s = text.lower() # converts the string to lowercase
    s = re.sub(r"[^\w\s'&/-]+", " ", s) # replaces all characters that are not alphanumeric, _, ', &, /, - with a space
    s = re.sub(r"\s+", " ", s).strip() # removes one or more spaces with a single space
    
    return s

def make_regex_patterns(keywords):
    '''
    instead of using for loops to cycle over each word in the keyword dictionary and try to
    match it with each word in the input, we can use regex patterns to find a match.
    this also prevents issues like finding a match on 'high' instead of 'high end'
    '''
    cleaned = sorted({clean_text(k) for k in keywords if k}, key=len, reverse=True) # clean and sort the keywords in descending order, so that for example, 'high end' is checked before 'high'
    patterns = [(c, re.compile(rf'\b{re.escape(c)}\b')) for c in cleaned] # make a list of tuples of (keyword, regex pattern with the keyword)

    return patterns

def first_match(patterns, text):
    '''
    return the first match found in the text using the list of regex patterns
    '''
    for keyword, pattern in patterns:
        if pattern.search(text): # if a match is found
            return keyword # return the keyword

    return None # if no match is found, return None

def map_keyword_to_option(keyword, keyword_map, options):
    '''
    map the keyword to the corresponding option using the keyword_map. for example, map 'high end' to 'expensive'.
    if the keyword is not in the map, return the keyword itself if it is a valid option
    otherwise, return None
    '''
    if not keyword:
        return None

    mapped = keyword_map.get(keyword, keyword) # get the mapped value from the keyword_map, or the keyword itself if not found

    if mapped in options:
        return mapped
    else:
        return None

def extract_keywords(text: str):
    text = text.lower() # convert input to lowercase
    output = {"pricerange": None,
              "area": None,
              "food": None} # initialize an empty dict

    #
    price_patterns = make_regex_patterns(set(pricerange_keyword_map.keys()))
    area_patterns = make_regex_patterns(set(area_keyword_map.keys()))
    food_patterns = make_regex_patterns(set(food_keyword_map.keys()))

    # get first match for each category
    price_match = first_match(price_patterns, text)
    area_match = first_match(area_patterns, text)
    food_match = first_match(food_patterns, text)

    # map the matched keyword to the corresponding option
    output["pricerange"] = map_keyword_to_option(price_match, pricerange_keyword_map, pricerange_options)
    output["area"] = map_keyword_to_option(area_match, area_keyword_map, area_options)
    output["food"] = map_keyword_to_option(food_match, food_keyword_map, food_options)

    return output

if __name__ == "__main__":
    # some quick tests
    tests = [   "I'm looking for world food",
        "I want a restaurant that serves world food",
        "I want a restaurant serving Swedish food",
        "I'm looking for a restaurant in the center",
        "I would like a cheap restaurant in the west part of town",
        "I'm looking for a moderately priced restaurant in the west part of town",
        "I'm looking for a restaurant in any area that serves Tuscan food",
        "Can I have an expensive restaurant",
        "I'm looking for an expensive restaurant and it should serve international food",
        "I need a Cuban restaurant that is moderately priced",
        "I'm looking for a moderately priced restaurant with Catalan food",
        "What is a cheap restaurant in the south part of town",
        "What about Chinese food",
        "I wanna find a cheap restaurant",
        "I'm looking for Persian food please",
        "Find a Cuban restaurant in the center"
    ]
    for test in tests:
        print(f"Input: {test}")
        print(f"Output: {extract_keywords(test)}")
        print()