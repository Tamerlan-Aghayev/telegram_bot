# WeatherBot Telegram Bot

A Telegram bot that provides weather forecasts for any city using natural language queries. The bot uses OpenAI's GPT models to understand user requests and OpenWeatherMap API to fetch accurate weather data.

## Features

- Natural language processing to understand city and date from user queries
- Weather forecasts for today, tomorrow, or specific days ahead
- Detailed weather information including:
  - Temperature and feels-like temperature
  - Weather description
  - Humidity levels
  - Wind speed
- Personalized clothing recommendations based on weather conditions
- All forecasts are provided for 1:00 PM local time

## How It Works

1. User sends a message like "What's the weather in Paris tomorrow?"
2. The bot uses GPT to extract the city name and date from the query
3. Weather data is fetched from OpenWeatherMap API
4. GPT processes the forecast data to select the most relevant time slot
5. The bot returns a formatted weather report with a clothing suggestion

## Setup Instructions

### Prerequisites

- Python 3.8+
- Telegram Bot Token
- OpenWeatherMap API Key
- OpenAI API Key

### Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd weather-telegram-bot
   ```

2. Install required dependencies:
   ```
   pip install python-telegram-bot openai requests
   ```

3. Create a `.env` file in the project root with your API keys:
   ```
   TELEGRAM_API_TOKEN=your_telegram_token_here
   OPENWEATHER_API_KEY=your_openweather_api_key_here
   GPT_API_KEY=your_openai_api_key_here
   ```

### Configuration

Edit the main script to configure:
- Logging level
- GPT model selection (currently using gpt-4o-mini and gpt-4o-mini-2024-07-18)
- Temperature units (currently set to metric)

## Usage

### Starting the Bot

Run the bot with:
```
python main.py
```

### User Commands

- `/start` - Displays welcome message and usage instructions

### Example Queries

Users can ask for weather information in various ways:
- "Weather in London"
- "What's the weather in Tokyo tomorrow?"
- "New York weather in 3 days"
- "How's the weather looking in Berlin?"

## Technical Details

### API Integrations

- **Telegram Bot API**: Handles messaging interface
- **OpenWeatherMap API**: Provides weather forecast data
- **OpenAI API**: Powers natural language understanding and data processing

### Key Components

- `extract_query_details()`: Parses natural language queries using GPT
- `fetch_forecast()`: Retrieves weather data from OpenWeatherMap
- `process_forecast_with_gpt()`: Selects relevant forecast data based on query
- `format_weather_message()`: Creates human-readable weather reports

## Future Improvements

- Support for multiple languages
- Historical weather data
- Weather alerts and notifications
- User preferences (default city, temperature units)
- Extended forecast range (up to 7 days)


## Acknowledgements

- [OpenWeatherMap](https://openweathermap.org/) for weather data
- [OpenAI](https://openai.com/) for GPT models
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) library
