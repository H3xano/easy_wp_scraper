# WordPress Article Scraper

This Python script scrapes articles from a specified WordPress site, saves each article as a JSON file, and combines all JSON files into a single JSON file.

## Features

- Follows redirects to find the final API endpoint of the WordPress site.
- Fetches articles from the WordPress REST API and saves them as JSON files.
- Combines individual JSON files into one comprehensive JSON file.
- Resumes scraping from the last processed page in case of interruptions.

## Prerequisites

- Python 3.x
- `requests` library
- `beautifulsoup4` library

You can install the required libraries using pip:

```sh
pip install requests beautifulsoup4
```

## Usage

1. Clone this repository or download the script.
2. Navigate to the directory containing the script.
3. Run the script with the base URL of the WordPress site you want to scrape.

```sh
python scraper.py <base_url>
```

Replace `<base_url>` with the actual base URL of the WordPress site you want to scrape.

### Example

```sh
python scraper.py https://example.com/
```

## Script Details

### Headers

The script uses specific HTTP headers for the requests to mimic a regular browser request. These headers are defined at the beginning of the script.

### Functions

- **make_api_url(base_url)**: Constructs the API URL for the WordPress REST API.
- **load_progress()**: Loads the last processed page number from the progress file.
- **save_progress(page_number)**: Saves the current processing page number to the progress file.
- **create_output_folder(folder_path)**: Creates the specified folder if it doesn't already exist.
- **save_article_to_json(article, folder)**: Saves an article dictionary as a JSON file.
- **clean_html(html_content)**: Removes HTML tags and extra whitespace from a string.
- **get_all_articles(api_url, output_folder)**: Fetches articles from the WordPress API and saves them as JSON files.
- **combine_json_files(input_directory, output_file)**: Combines multiple JSON files into one JSON file.

### Output

- The script saves individual JSON files for each article in a folder named after the domain of the WordPress site.
- After scraping, it combines all individual JSON files into a single file named `combined_articles.json` in the same folder.

### Resuming Progress

- The script saves its progress in a file named `progress.json`. If the script is interrupted, it will resume scraping from the last saved page when run again.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Commit your changes.
5. Push to the branch.
6. Open a pull request.

## Contact

For any questions or suggestions, please open an issue or contact the project maintainers.
