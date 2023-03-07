from bs4 import BeautifulSoup
from requests_html import HTMLSession
import pandas as pd
import time
import random


def sleep(seconds: int): 
    """
    sleep timer that will sleep for random intervals 
    between 0 and the inputted seconds. Needs to be randomised 
    to prevent timeouts on the website

    :param seconds: max amount of seconds to sleep for
    :return time.sleep: time.sleep function with randomised sleep interval
    """
    return time.sleep(random.randint(0, seconds))

def get_league_url(base_url: str, league: str) -> str:
    """
    Finds the league page url 

    :param base_url: url for the baseball reference homepage
    :param league: the name of the league we want the url for
    :return league_url: full league url
    """
    leagues_url = base_url + '/register/'

    s = HTMLSession()
    page = s.get(leagues_url)
    soup = BeautifulSoup(page.content, "html.parser")
    league_link = soup.find('a', text=league)['href']

    return base_url + league_link


def get_team_urls(base_url: str, league_url: str, year=2022) -> dict:
    """
    Finds the urls for each team page and saves to a dictionary 

    :param base_url: url for the baseball reference homepage
    :param league_url: full url for the league page
    :return team_dict: dictionary with team name as the key and 
                        team page url as the value 

    """

    # TO DO: Add a year variable rather than hard code 2022

    s = HTMLSession()
    page = s.get(league_url)
    soup = BeautifulSoup(page.content, "html.parser")

    # Find start and end links so we can get all the links in between
    start_link = soup.find_all('a', text=f"{year}")[-2]
    end_link = soup.find_all('a', text=f"{year-1}")[-2]

    team_dict = {}
    current_link = start_link.find_next('a') 
    while current_link != end_link:
        team_name = current_link.text  # loop through links until the ending link is reached
        full_url = base_url + current_link['href']
        team_dict[team_name] = full_url
        current_link = current_link.find_next('a')
    
    return team_dict


def get_stats_table(url: str, team: str, id: str) -> None:  
    """
    Scrapes the pitching and batting table depending on the ID provided
    
    :param url: full team url 
    :param id: used to determine which table to scrape (batting or pitching)
    """
    
    s = HTMLSession()
    page = s.get(url)
    stats_div = BeautifulSoup(page.content, "html.parser")

    # Pitching table is in a comment for some reason so have to do some 
    # cleaning before converting to DF
    if id == "team_pitching":
        s = str(stats_div.find("div", id="all_team_pitching"))
        start_len, end_len = s.find('<table'), s.rfind('</table>')
        cleaned_page = s[start_len:end_len + len('</table>')]
        stats_div = BeautifulSoup(cleaned_page, "html.parser")  
        
    stats_table = stats_div.find("table", id=id)

    stats_df = pd.DataFrame()
    for row in stats_table.tbody.find_all("tr"):
        columns = row.find_all("td")
        
        if(columns != []):
            stats_dict = {}
            for i in range(0, len(columns)):
                stats_dict[columns[i]["data-stat"]] = columns[i].text.strip()
            stats_df = stats_df.append(stats_dict, ignore_index=True)

    # Creating a local file name to export to
    team_norm = team.lower()
    team_norm = team_norm.replace(" ", "_")
    local_filename = f"{team_norm}_{id}.csv"

    stats_df.to_csv(f"resources/{local_filename}")

    return 


def main(base_url):

    # Get league url for each league
    jpl_url = get_league_url(base_url, "Japan Pacific League")
    jcl_url = get_league_url(base_url, "Japan Central League")
    sleep(3)

    # Get team url and save as dict
    pacfic_teams_dict = get_team_urls(base_url, jpl_url)
    central_teams_dict = get_team_urls(base_url, jcl_url)
    sleep(3)

    # Loop through pacific teams and save result locally to CSV
    for team in pacfic_teams_dict:
        print(team)
        batting_stats = get_stats_table(pacfic_teams_dict[team], team, "team_batting")
        sleep(3)
        pitching_stats = get_stats_table(pacfic_teams_dict[team], team, "team_pitching")
        sleep(3)
        print("*"*10)

    # Loop through central teams and save result locally to CSV
    for team in central_teams_dict:
        print(team)
        batting_stats = get_stats_table(central_teams_dict[team], team, "team_batting")
        sleep(3)
        pitching_stats = get_stats_table(central_teams_dict[team], team, "team_pitching")
        sleep(3)
        print("*"*10)
    
    return 


base_url = "https://www.baseball-reference.com" 
if __name__ == "__main__":
    try:
        main(base_url)
    except Exception:
        print(Exception)
        raise