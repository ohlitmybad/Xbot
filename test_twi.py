import time
import random
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from requests_oauthlib import OAuth1
from selenium.webdriver.chrome.options import Options
import os

# Your credentials
API_KEY = 'cw0P0n0oJcpzb4iA2NQm0kWod'
API_KEY_SECRET = '2XwwsJokAPGhYPBTjqTzVwLBK3u7jxTI8oRWaqmWWEDYjbKTVs'
ACCESS_TOKEN = '1670542627257589761-23tNDvYcX2SUTt7ucclcDpbci5XdyW'
ACCESS_TOKEN_SECRET = '1MHEaYkipURtIRT7d1daNRAIkrTlIPdnrBOGxhOCp27FX'


class TestUntitled:
    def setup_method(self, method):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options=chrome_options)

    def teardown_method(self):
        self.driver.quit()
        

    def test_untitled(self):
        urls_and_metrics = {
            "https://datamb.football/proplotgk24/": [
                "Shots against per 90", "xG against per 90", 
                "Prevented goals per 90", "Save rate %", "Accurate passes %", 
                "Accurate progressive passes %", "Accurate short / medium passes %", 
                "Accurate long passes %", "Accurate passes to final third %", 
                "Progressive passes per 90", "Passes to final third per 90", "Passes per 90", 
                "Forward passes per 90", "Long passes per 90", "Short / medium passes per 90", 
                "Successful defensive actions per 90", "Defensive duels per 90", 
                "Aerial duels per 90"
            ],
            "https://datamb.football/proplotcb24/": [
                "Successful defensive actions per 90", "Defensive duels per 90", 
        "Aerial duels per 90", "Sliding tackles per 90", "PAdj Sliding tackles", 
        "Interceptions per 90", "PAdj Interceptions", "Dribbles per 90", 
        "Progressive runs per 90", "Passes per 90", "Forward passes per 90", 
        "Long passes per 90", "Key passes per 90", "Passes to final third per 90", 
        "Passes to penalty area per 90", "Through passes per 90", 
        "Progressive passes per 90", "Defensive duels won %", 
        "Aerial duels won %", "Accurate passes %", "Accurate forward passes %", 
        "Accurate progressive passes %"
            ],
            "https://datamb.football/proplotfb24/": [
                "Successful defensive actions per 90","Defensive duels per 90","Aerial duels per 90","Sliding tackles per 90","PAdj Sliding tackles","Interceptions per 90","PAdj Interceptions","Successful attacking actions per 90","xG per 90", "Goals per 90", "Assists per 90", "Shots per 90","Crosses per 90","Dribbles per 90","Offensive duels per 90","Touches in box per 90","Progressive runs per 90","Accelerations per 90","Fouls suffered per 90","Passes per 90","Forward passes per 90","Long passes per 90","xA per 90","Shot assists per 90","Key passes per 90","Passes to final third per 90","Passes to penalty area per 90","Through passes per 90","Deep completions per 90","Progressive passes per 90","Defensive duels won %","Aerial duels won %","Accurate crosses %","Successful dribbles %","Offensive duels won %","Accurate passes %","Accurate forward passes %","Accurate progressive passes %"
            ],
            "https://datamb.football/proplotcm24/": [
                "Successful defensive actions per 90","Defensive duels per 90","Aerial duels per 90","Sliding tackles per 90","PAdj Sliding tackles","Interceptions per 90","PAdj Interceptions","Successful attacking actions per 90","xG per 90","Shots per 90", "Goals per 90", "Assists per 90", "Crosses per 90","Dribbles per 90","Offensive duels per 90","Touches in box per 90","Progressive runs per 90","Accelerations per 90","Fouls suffered per 90","Passes per 90","Forward passes per 90","Long passes per 90","xA per 90","Shot assists per 90","Key passes per 90","Passes to final third per 90","Passes to penalty area per 90","Through passes per 90","Deep completions per 90","Progressive passes per 90","Defensive duels won %","Aerial duels won %","Accurate passes %","Accurate forward passes %","Accurate progressive passes %","Successful dribbles %","Offensive duels won %"
            ],
            "https://datamb.football/proplotfw24/": [
                "Shots on target %","Goal conversion %","Accurate crosses %","Successful dribbles %","Offensive duels won %","Defensive duels won %","Aerial duels won %","Successful defensive actions per 90","Successful attacking actions per 90","xG per 90","Goals per 90", "Assists per 90", "Shots per 90","Crosses per 90","Dribbles per 90","Offensive duels per 90","Touches in box per 90","Progressive runs per 90","Accelerations per 90","Fouls suffered per 90","Passes per 90","xA per 90","Shot assists per 90","Key passes per 90","Passes to final third per 90","Passes to penalty area per 90","Through passes per 90","Deep completions per 90","Progressive passes per 90"
            ],
            "https://datamb.football/proplotst24/": [
                "Successful defensive actions per 90","Aerial duels per 90","Successful attacking actions per 90","xG per 90","Shots per 90","Crosses per 90","Dribbles per 90","Offensive duels per 90","Touches in box per 90","Progressive runs per 90","Goals per 90", "Assists per 90", "Accelerations per 90","Fouls suffered per 90","xA per 90","Shot assists per 90","Key passes per 90","Passes to penalty area per 90","Through passes per 90","Deep completions per 90","Aerial duels won %","Shots on target %","Goal conversion %","Successful dribbles %","Offensive duels won %","Accurate passes %"
            ]
        }

        url_to_position = {
            "https://datamb.football/proplotgk24/": "Goalkeepers",
            "https://datamb.football/proplotcb24/": "Centre-backs",
            "https://datamb.football/proplotfb24/": "Full-backs",
            "https://datamb.football/proplotcm24/": "Midfielders",
            "https://datamb.football/proplotfw24/": "Wingers",
            "https://datamb.football/proplotst24/": "Strikers"
        }

        selected_url = random.choice(list(urls_and_metrics.keys()))
        self.driver.get(selected_url)
        time.sleep(1)
        self.driver.set_window_size(1080, 840)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "eml"))
        ).send_keys("tombolivier@gmail.com")
        
        self.driver.find_element(By.NAME, "pwd").send_keys("password")
        self.driver.find_element(By.CSS_SELECTOR, ".SFmfllog:nth-child(3) button").click()

        circles = self.driver.find_elements(By.TAG_NAME, 'circle')
        for circle in circles:
            self.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true, view: window}));", circle)

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "select-x"))
        )
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "select-y"))
        )

        metric_options = urls_and_metrics[selected_url]
        selected_metric_x = random.choice(metric_options)
        metric_options.remove(selected_metric_x)
        selected_metric_y = random.choice(metric_options)

        league_options = [
            "?? Top 5 Leagues","?? Top 7 Leagues","? All Leagues", "??????? Premier League","?? La Liga", "?? Bundesliga", "?? Serie A", "?? Ligue 1","? Outside Top 7", "?? Liga Portugal", "?? Eredivisie","?? Belgium", "??????? Scotland", "?? Austria", "?? Switzerland", "?? T?rkiye", "?? Denmark", "?? Sweden", "?? Norway", "?? Croatia", "?? Serbia", "?? Czech Republic", "?? Poland", "?? Ukraine", "?? Russia", "?? Greece", "?? Japan", "?? Korea", "?? Saudi Arabia", "?? United States",  "?? Mexico", "?? Brazil", "?? Argentina", "?? Uruguay", "?? Chile", "?? Colombia", "?? Ecuador",  "?? Paraguay", "??????? Championship", "?? Spain Segunda", "?? Serie B", "?? 2. Bundesliga", "?? Ligue 2"
        ]

        weights = [
            0.25, 0.20, 0.09, 0.09, 0.06, 0.05, 0.05, 0.04, 0.03, 0.03, 0.03, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025
        ]

        assert len(weights) == len(league_options), "Weights length must match the league options length"
        selected_league = random.choices(league_options, weights=weights, k=1)[0]

        if selected_league in ["?? Top 7 Leagues", "?? Top 5 Leagues", "? All Leagues", "? Outside Top 7"]:
            age_options = ["Age", "U21", "U22", "U23", "U24"]
            selected_age = random.choice(age_options)
        else:
            selected_age = "Age"

        dropdown_x = self.driver.find_element(By.ID, "select-x")
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//select[@id='select-x']/option[. = '{selected_metric_x}']"))
        ).click()

        dropdown_y = self.driver.find_element(By.ID, "select-y")
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//select[@id='select-y']/option[. = '{selected_metric_y}']"))
        ).click()

        dropdown = self.driver.find_element(By.ID, "select-age")
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//option[. = '{selected_age}']"))
        ).click()

        dropdown = self.driver.find_element(By.ID, "select-league")
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//option[. = '{selected_league}']"))
        ).click()

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "toggle-median-lines"))
        ).click()        

        

        self.driver.find_element(By.CSS_SELECTOR, ".toggle-icon").click()

        self.driver.execute_script("""
    document.documentElement.style.overflow = 'hidden';  // Hide horizontal and vertical scroll bars
    document.body.style.overflow = 'hidden';  // Hide scroll bars on body
""")
        time.sleep(4)
        self.driver.save_screenshot('screenshot.png')


        # Upload the screenshot to Twitter
        upload_url = "https://upload.twitter.com/1.1/media/upload.json"
        auth = OAuth1(API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        
        with open('screenshot.png', 'rb') as image_file:
            files = {'media': image_file}
            response = requests.post(upload_url, files=files, auth=auth)
        
        if response.status_code != 200:
            print("Failed to upload media:", response.status_code, response.text)
            return
        
        media_id = response.json()['media_id_string']
        selected_position = url_to_position[selected_url]
        selected_age = selected_age.replace("Age", "")


        


        # Create the tweet text dynamically
        tweet_text = f"{selected_league} : {selected_age} {selected_position}\n? {selected_metric_x} vs {selected_metric_y}\n\n? datamb.football"
        tweet_text = tweet_text.replace("  ", " ")

        # Create the tweet with the media attached
        tweet_url = "https://api.twitter.com/2/tweets"
        payload = {
            "text": tweet_text,
            "media": {
                "media_ids": [media_id]
            }
        }
        
        response = requests.post(tweet_url, json=payload, auth=auth)
        
        if response.status_code == 201:
            print("Tweet successfully sent!")
        else:
            print("Failed to send tweet:", response.status_code, response.text)



if __name__ == "__main__":
    pytest.main()
 