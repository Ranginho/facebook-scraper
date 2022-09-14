from time import time
from pathlib import Path
from itertools import cycle
from helper_functions import *
from datetime import datetime, timedelta
from facebook_scraper import get_posts

import requests
import warnings

# TODO: get_profiles(... friends = True) - Optimize get_friends() - try scroll
# TODO: add the same logic for friends as we have for reactors (search here - "maybe silent ban so changing account")
warnings.filterwarnings("ignore")

# %load_ext autoreload
# %autoreload 2

ACCOUNTS_PATH = "accounts.xlsx"
profile_ids = read_accounts(ACCOUNTS_PATH)

'''
("mamukagrigolia16@gmail.com", "mamukaN123"),
                            ("tocomaglakelidze@gmail.com", "tocoN123"),
                            ("qvilitaiaalex@gmail.com", "alexN123")
'''
'''
("jarjimagla@gmail.com", "Nn123456"),
                            ("tocomaglakelidze@gmail.com", "tocoN123"),
                            ("qvilitaiaalex@gmail.com", "alexN123")
'''
facebook_accounts = cycle([("jarjimagla@gmail.com", "Nn123456")])
len_accounts = 1

sleep_times = generate_sleep_time_dist()

# to handle callbacks
search_page_persistor = SearchPagePersistor()  # could be inited with a specific search page URL

last_post_date = latest_post_date = datetime.today() - timedelta(days=180)


def scrape_posts(curr_profile_posts, profiles_dir, profile_id, num_posts):
    for i, post in enumerate(curr_profile_posts):
        if i == 6:
            return True, num_posts
        if post['shared_post_id'] is None and post['video'] is None and post['image'] is not None and \
                (post['shared_text'] is None or post['shared_text'] == ''):
            save_image(post, profiles_dir / profile_id / "images")
        print(post['text'])
        save_post(post, profiles_dir / profile_id / "posts")

        if (post["reactors"] is not None) and (post["reaction_count"] - len(post["reactors"]) > 10):
            print("maybe silent ban so changing account")
            return False, num_posts

        num_posts += 1

        time.sleep(random.choice(sleep_times))
    else:
        return True, num_posts


def profile_scraper(profile_ids: list,
                    facebook_accounts: list,
                    search_page_persistor: SearchPagePersistor,
                    profiles_dir: Path,
                    last_post_date: datetime,
                    len_accounts: int) -> None:

    headers = requests.utils.default_headers()
    headers.update(
        {
            'User-Agent': 'My User Agent 1.0',
        }
    )

    for profile_id in profile_ids:
        print(f"\nprofile {profile_id} scrapping info ....")

        # fb_acc = next(facebook_accounts)
        # _scraper.login(fb_acc[0], fb_acc[1])
        #
        # profile_info = get_profile(profile_id, friends=True, allow_extra_requests=False)
        # save_profile_info(profile_info, profiles_dir / profile_id)

        print(f"profile {profile_id} scrapping info DONE")

        num_posts = 0

        # Post Ids, Images
        while True:
            try:
                print(f"profile {profile_id} scrapping posts ....")

                curr_fb_account = next(facebook_accounts)
                curr_profile_posts = get_posts(
                    account=profile_id,
                    credentials=curr_fb_account,
                    start_url=search_page_persistor.get_current_search_page(),
                    request_url_callback=search_page_persistor.set_search_page,
                    options={"allow_extra_requests": True,
                             "comments": True,
                             "reactors": True,
                             "sharers": True},
                    timeout=120,
                    # latest_date=last_post_date,
                    headers=headers)

                success, num_posts = scrape_posts(curr_profile_posts, profiles_dir, profile_id, num_posts)

                if num_posts == 0:
                    raise ZeroDivisionError  # just for testing sth

                if success or num_posts > 150:
                    break

            except CallBackException:
                print("CallBackException")
                time.sleep(random.choice(sleep_times))

            except Exception as e:
                print(e)

                accounts = []
                for _ in range(len_accounts):
                    accounts.append(next(facebook_accounts))

                accounts.remove(curr_fb_account)
                print("removed account: ", curr_fb_account)
                len_accounts -= 1
                facebook_accounts = cycle(accounts)

                if len(accounts) < 3:
                    return

                print("sleeping for 2 hours")
                time.sleep(7200)

        print(f"profile {profile_id} scrapping posts DONE")
        time.sleep(random.choice(sleep_times))
    return


profile_scraper(profile_ids, facebook_accounts, search_page_persistor, Path("profiles"), last_post_date, len_accounts)
