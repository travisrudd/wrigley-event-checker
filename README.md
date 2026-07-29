# Wrigley Events Bot

A Python application that retrieves upcoming Wrigley Field events, classifies them, adds weather forecasts, and generates daily event summaries.

## Features

- Retrieves Wrigley Field events from Ticketmaster
- Classifies event types
- Adds hourly weather forecasts from Open-Meteo
- Generates summaries for today and tomorrow
- Saves structured event data as JSON
- Saves a human-readable daily report

## Project Structure

```text
wrigley_events/
├── app.py
├── classifier.py
├── config.py
├── logger.py
├── models.py
├── storage.py
├── summary.py
├── ticketmaster.py
├── weather.py
├── requirements.txt
└── output/