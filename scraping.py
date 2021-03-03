# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt


# Set the executable path and initialize the chrome browser in splinter
executable_path = {'executable_path': 'chromedriver'}

def scrape_all():
    # Initializes a headless driver for deployment
    # headless means we don't see the script working as it runs (silent)
    browser = Browser('chrome', executable_path="chromedriver", headless=True)
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store in a dictionary
    data = {
            "news_title": news_title,
            "news_paragraph": news_paragraph,
            "featured_image": featured_image(browser),
            "facts": mars_facts(),
            "last_modified": dt.datetime.now()
    }
    # end browser session
    browser.quit()
    return data

# Define the mars_news function, passing in the browser initialized above to run the function
def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Optional delay for loading the page in case the page is resource heavy and takes a while to load
    # Look for ul and li HTML tags, specifically the item_list and slide attributes
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)


    # Scraping NASA website ------------------
    # Create our scraping environment and parse our text to news_soup
    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:
        # search our parsed html for lists with class = slide, THEN unordered lists with class = item_list. CSS works RIGHT TO LEFT IN ORDER
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        # Use the parent element to find the first `a` tag and save it as `news_title`
        # Use the get_text() method to ONLY RETURN TEXT FROM THE OVERALL HTML OUTPUT OF OUR SCRAPE
        news_title = slide_elem.find("div", class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_paragraph = slide_elem.find('div', class_="article_teaser_body").get_text()
    # Python will return nothing if it encounters an AttributeError, such as in the instance that the website's format has changed    
    except AttributeError:
         return None, None

    return news_title, news_paragraph

# Define the featured image scrape
def featured_image(browser):
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    # Index [1] indicates that we want to store the SECOND RESULT of the find_by_tag('button') search. IE the second button that we find
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')
    try:
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'
    
    return img_url

# Scraping facts about Mars
# We can use pandas' read_html() function
def mars_facts():
    try:
        # read_html() reads the given url for any tables and returns a DataFrame object if possible. Chaining index 0 means we save the FIRST table to variable df
        df = pd.read_html('http://space-facts.com/mars/')[0]
    # Return a BaseException, which is a catchall exception for many types of errors

    except BaseException:
        return None

    # Provide labels for the dataframe's columns
    df.columns = ['description','value']
    # Set the index column to = the description column, inplace means it happens to the existing dataframe instead of creating a new object
    df.set_index('description', inplace=True)
    # use pandas' to_html() function to convert the dataframe to HTML, which can be passed into a website for display
    return df.to_html()

# If this script is running as a script (and not an import), print results of scrape_all (scraped data)
if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())




