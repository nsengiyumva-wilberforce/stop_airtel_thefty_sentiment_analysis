# Uganda Mobile Money Complaints Tracker

A Python script that collects and analyzes mobile money-related complaints from Twitter in Uganda, focusing on major providers like MTN Mobile Money (MoMo) and Airtel Money.

## Features

- **Targeted Search**: Uses specialized queries to find mobile money complaints in Uganda
- **Complaint Detection**: Identifies genuine complaints using keyword matching
- **Categorization**: Automatically categorizes complaints by type and mobile network
- **Data Export**: Saves results to CSV with comprehensive complaint details
- **Rate Limit Handling**: Implements intelligent delays and error recovery

## Requirements

- Python 3.7+
- Twitter account credentials
- Required Python packages (install via `pip install -r requirements.txt`):
  - twikit
  - configparser

## Installation

1. Clone the repository:
```bash
git clone https://github.com/nsengiyumva-wilberforce/stop_airtel_thefty_sentiment_analysis.git
cd stop_airtel_thefty_sentiment_analysis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up configuration:
   - Create a `config.ini` file with your Twitter credentials:
   ```
   [X]
   auth_info_1 = your_auth_info_1
   auth_info_2 = your_auth_info_2
   password = your_password
   ```

## Usage

Run the script with:
```bash
python main.py
```

The script will:
1. Authenticate with Twitter using provided credentials
2. Search for mobile money complaints using predefined queries
3. Process and categorize the complaints
4. Save results to `uganda_mobile_money_complaints.csv`

## Output

The CSV file contains the following columns:
- Tweet_ID: Unique identifier for the tweet
- Date: When the tweet was posted
- Username: Twitter handle of the user
- Text: Full text of the tweet
- Complaint_Type: Categorized type of complaint
- Mobile_Network: Detected mobile money provider
- Retweets: Number of retweets
- Likes: Number of likes
- Replies: Number of replies

## Complaint Categories

The script categorizes complaints into:
- Failed Transaction
- Money Not Received
- Unauthorized Deduction
- Poor Customer Service
- System/Network Issue
- High Charges/Fees
- General Complaint

## Supported Mobile Networks

- MTN (MoMo)
- Airtel (Airtel Money)
- Africell
- UTL
- Unknown (when not specified)

## Important Notes

- The script implements rate limiting to respect Twitter's API policies
- Authentication cookies are saved for future sessions
- The script handles common errors and automatically retries failed requests
- Date ranges can be modified in the code to search different time periods

## Disclaimer

This tool is for research purposes only. Users should comply with Twitter's Terms of Service and applicable laws when collecting and using tweet data.

# running the analysis notebook  

Open Airtel_thefty _analysis.ipynb in your favorite editor and run the cells according, you will need to install some packages using pip.