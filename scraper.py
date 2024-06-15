import os
import sys
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

HEADERS = {
    "Host": "",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
    "DNT": "1",
    "Sec-GPC": "1",
    "Priority": "u=1",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "TE": "trailers"
}

def make_api_url(base_url):
    """
    Follows redirects to get the final URL for the WordPress API.

    Args:
        base_url (str): The initial base URL of the WordPress site.

    Returns:
        str: The final URL for the WordPress API.
    """
    parsed_url = urlparse(base_url)
    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError("Invalid URL provided.")
    
    if not base_url.endswith('/'):
        base_url += '/'
    
    api_url = urljoin(base_url, 'wp-json/wp/v2/posts')
    return api_url


def load_progress():
    """
    Loads the last processed page number from the progress file.

    Returns:
        int: The last processed page number (defaults to 1 if file doesn't exist).
    """
    if not os.path.exists(PROGRESS_FILE):
        return 1

    try:
        with open(PROGRESS_FILE, 'r') as file:
            data = json.load(file)
            page = data.get('page', 1)  # Default to 1 if 'page' key is missing
            print(f"Resuming scraping from page: {page}")
            return page
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error loading progress file. Starting from page 1.")
        return 1


def save_progress(page_number):
    """
    Saves the current processing page number to the progress file.

    Args:
        page_number (int): The current page number.
    """
    data = {'page': page_number}
    with open(PROGRESS_FILE, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Progress saved. Current page: {page_number}")


def create_output_folder(folder_path):
    """
    Creates the specified folder if it doesn't already exist.

    Args:
        folder_path (str): The path to the folder to create.
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created output folder: {folder_path}")


def save_article_to_json(article, folder):
    """
    Saves an article dictionary as a JSON file.

    Args:
        article (dict): The dictionary containing article data.
        folder (str): The folder path to save the JSON file.
    """
    json_file_path = os.path.join(folder, f'{article["id"]}.json')
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(article, json_file, ensure_ascii=False, indent=4)
    print(f"Saved article {article['id']} to {json_file_path}")


def clean_html(html_content):
    """
    Removes HTML tags and extra whitespace from a string.

    Args:
        html_content (str): The HTML content to clean.

    Returns:
        str: The cleaned text content.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text(separator=' ', strip=True)


def get_all_articles(api_url, output_folder):
    """
    Fetches articles from a WordPress website API and saves them as JSON files.

    Args:
        api_url (str): The base URL of the WordPress website API.
    """
    page = load_progress()
    per_page = 100  # Maximum allowed posts per page

    while True:
        print(f"Fetching page {page}...")
        parsed_url = urlparse(api_url)
        domain = parsed_url.netloc
        HEADERS['Host'] = domain
        response = requests.get(api_url, params={'page': page, 'per_page': per_page}, headers=HEADERS)
        if response.status_code != 200:
            print(f"API request failed with status code: {response.status_code}")
            break

        posts = response.json()
        if not posts:
            print(f"No more articles found on page {page}")
            break

        for post in posts:
            article = {
                'id': post['id'],
                'date': post['date'],
                'title': post['title']['rendered'],
                'link': post['link'],
                'content': clean_html(post['content']['rendered'])
            }
            save_article_to_json(article, output_folder)
            print(f"Processing article '{article['title']}'")

        page += 1
        save_progress(page)
    print("Scraping completed.")


def combine_json_files(input_directory, output_file):
    """
    Combines multiple JSON files into one JSON file.

    Args:
        input_directory (str): The directory containing the JSON files.
        output_file (str): The file path for the combined JSON output.
    """
    json_list = []

    for filename in os.listdir(input_directory):
        if filename.endswith('.json'):
            file_path = os.path.join(input_directory, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                json_content = json.load(file)
                json_list.append(json_content)

    with open(output_file, 'w', encoding='utf-8') as output:
        json.dump(json_list, output, ensure_ascii=False, indent=4)
    print(f"Combined JSON saved to {output_file}")


def main():
    """
    The main function that starts the script to retrieve and save articles.
    """
    if len(sys.argv) != 2:
        print("Usage: python script.py <base_url>")
        sys.exit(1)

    base_url = sys.argv[1]
    api_url = make_api_url(base_url)
    print(f"Final API URL: {api_url}")

    parsed_url = urlparse(api_url)
    domain = parsed_url.netloc
    output_folder = domain + '_articles'
    create_output_folder(output_folder)
    get_all_articles(api_url, output_folder)
    print(f'Articles saved to {output_folder}.')

    combined_output_file = os.path.join(output_folder, f'{domain}_articles.json')
    combine_json_files(output_folder, combined_output_file)

    if os.path.exists(PROGRESS_FILE):
        print("All articles processed. Removing progress.json")
        os.remove(PROGRESS_FILE)


if __name__ == '__main__':
    PROGRESS_FILE = 'progress.json'
    main()
