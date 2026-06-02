# neshan-geocode-batch

Batch geocode Persian addresses stored in an Excel file using the [Neshan Geocoding API](https://platform.neshan.org/).  
The script automatically cleans hyphen‑separated addresses into natural Persian format, processes them one by one, and saves progress after every address so you can stop and resume at any time without losing results.

## Features

- Reads addresses from an Excel (`.xlsx`) file
- Cleans hyphen‑separated strings (e.g. `Tehran-تهران-خیابان-انقلاب`) into proper Persian format (`Tehran، تهران، خیابان، انقلاب`)
- Calls the Neshan **Geocoding API v1/plus** to obtain latitude/longitude
- Saves results along with original data, status, and error messages
- **Resume support** – writes a progress file (`geocoded_progress.xlsx`) after each geocode, so you can stop at any point and later continue from where you left off
- Built‑in delay between requests to respect API rate limits
- Simple configuration via variables at the top of the script

## Prerequisites

- Python 3.7 or later
- A valid [Neshan API key](https://platform.neshan.org/) (free tier available)

## Installation

1. Clone the repository or download the script.
2. Install the required packages:
   ```bash
   pip install pandas requests openpyxl
