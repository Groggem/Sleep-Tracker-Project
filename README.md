# Sleep Cycle Tracker

A lightweight desktop GUI application built with Python and Tkinter for logging, analyzing, and visualizing personal sleep patterns. The application uses structured JSON storage to track sleep/wake intervals and renders custom canvas charts for sleep duration trends.

## Features

- **Intuitive GUI Interface**: Built with Tkinter featuring modal dialogs, date pickers, and scrolling history views.
- **JSON Data Persistence**: Automatically loads and saves structured time-series entries (`sleep_data.json`).
- **Sleep & Wake Interval Pairings**: Handles multi-day tracking, unmatched sleep logs, and edge-case date conversions.
- **Averages & Filtering**: Calculates average sleep duration across predefined ranges (Last Week, Last Month, All Time) or custom date windows.
- **Custom Native Canvas Plotting**: Draws sleep duration trends over time using native Tkinter Canvas lines and nodes—no external heavy plotting dependencies required.
- **History Management**: Monthly dropdown filtering and manual record deletion directly from the UI.

## Tech Stack

- **Language**: Python 3
- **GUI Framework**: Tkinter (Standard Library)
- **Data Format**: JSON
- **Libraries Used**: `json`, `datetime`, `tkinter`

## Getting Started

### Prerequisites
Python 3.x installed on your system (Tkinter is included by default with most Python distributions).

### Installation & Execution

1. Clone the repository:
   ```bash
   git clone [https://github.com/Groggem/Sleep-Tracker-Project.git](https://github.com/Groggem/Sleep-Tracker-Project.git)
   cd Sleep-Tracker-Project
2. Run the application:
   ```bash
   python main.py 
