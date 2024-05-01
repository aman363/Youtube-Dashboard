# YouTube Data Analytics

This repository contains a Python script for analyzing and visualizing YouTube data obtained from Google Takeout. We have generated a comprehensive analysis that provides insights into our YouTube usage habits.

## Steps to Run

### 1. Install Python 3+

If you don't already have Python 3+ installed on your computer, download it from [here](https://www.python.org/downloads/).

### 2. Clone This Repository

1. **Clone Repository**: Visit the repository [here](https://github.com/aman363/Youtube-Dashboard).
2. **Download ZIP**: Click the green "Clone or Download" button and select "Download ZIP".
3. **Extract ZIP**: Extract the downloaded ZIP file to a location on your computer.

### 3. Install Dependencies

1. **Open Terminal**: Open a command prompt or Terminal window in the repository folder.
2. **Install Dependencies**: Execute the following command:
   ```
   pip install -r requirements.txt
   ```
### 4. Run the Script

1. **Execute Script**: In the same command prompt or Terminal window, execute the following command:
   ```
   python report.py
   ```
### 5. Results

Once the script completes, one can open the **dashboard.html** in the browser. Additionally, all the plots used in the report can be found in the **Images** folder.

## Process Overview

1. **Download YouTube Data**: We have obtained YouTube data from Google Takeout.
2. **Parse HTML Files**: The script parses the HTML files provided by Google Takeout to generate CSV files containing relevant data.
3. **Visualization**: Various visualizations are created based on the parsed data, providing insights into our YouTube usage habits.
4. **API Integration**: The YouTube Data API is used to map videos to different genres and languages.
5. **Comparative Analysis**: The script includes visualizations comparing watching patterns among different users.

## Deployed Dashboard

Check out the deployed dashboard [here](https://aman363.github.io/Youtube-Dashboard/).
