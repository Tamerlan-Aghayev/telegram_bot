import logging
from openai import OpenAI
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
    CommandHandler,
)
import json

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
TELEGRAM_API_TOKEN = "xxxxxx"
OPENWEATHER_API_KEY = "xxxxxx"
GPT_API_KEY = "xxxxxx"


def extract_query_details(query):
    """
    Use GPT to extract city name and date from the query
    """
    client = OpenAI(api_key=GPT_API_KEY)

    extraction_prompt = f"""
    Analyze this weather query: "{query}"
    Extract the city name and date (relative to today).
    Reply in JSON format:
    {{
        "city": "city_name or NONE if not found",
        "days_ahead": "number (0 for today, 1 for tomorrow, etc.) or -1 if unclear"
    }}
    Examples:
    - "Weather in London tomorrow" → {{"city": "London", "days_ahead": 1}}
    - "Weather in Paris in 3 days" → {{"city": "Paris", "days_ahead": 3}}
    - "How's the weather in Tokyo" → {{"city": "Tokyo", "days_ahead": 0}}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a weather query analysis tool."},
                {"role": "user", "content": extraction_prompt}
            ],
            max_tokens=150,
            temperature=0
        )

        cleaned_response = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()

        # Then parse the cleaned JSON string
        return json.loads(cleaned_response)
    except Exception as e:
        logger.error(f"Error extracting query details: {str(e)}")
        return None


def process_forecast_with_gpt(forecast_data, query_details):
    """
    Use GPT to process and select the most relevant forecast data
    Always targeting 13:00:00 time slot
    """
    client = OpenAI(api_key=GPT_API_KEY)

    # Add fixed hour (13) to query details
    query_details["hour"] = 13

    processing_prompt = f"""
    Given these weather forecasts and query details, select the most relevant forecast entry.
    Query details: {json.dumps(query_details)}
    Forecast data: {json.dumps(forecast_data)}

    Return only the single most relevant JSON forecast entry that is closest to the given date at 13:00:00.
    For example if it is 1 day ahead, the dt_txt of the json should be tomorrow 13:00:00.
    Also, add another parameter to json called "suggestion", which will contain a suggestion for clothes choice, in a funny way can be better
    Do not return any explanation or any ending, just json, that is it, I am parsing it, any other text gonna cause error.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": "You are a weather data processing tool."},
                {"role": "user", "content": processing_prompt}
            ],
            max_tokens=4000,
            temperature=0
        )

        cleaned_response = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()

        # Then parse the cleaned JSON string
        return json.loads(cleaned_response)
    except Exception as e:
        logger.error(f"Error processing forecast: {str(e)}")
        print(e)
        return None


def fetch_forecast(city_name):
    """Fetch weather forecast data for a given city"""
    import requests

    url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city_name,
        "units": "metric",
        "appid": OPENWEATHER_API_KEY,
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching forecast data: {e}")
        return None


def format_weather_message(weather_data, city_name):
    """Format weather data into a readable message"""
    suggestion = weather_data.get('suggestion', 'N/A')
    temp = weather_data.get('main', {}).get('temp', 'N/A')
    feels_like = weather_data.get('main', {}).get('feels_like', 'N/A')
    description = weather_data.get('weather', [{}])[0].get('description', 'N/A')
    humidity = weather_data.get('main', {}).get('humidity', 'N/A')
    wind_speed = weather_data.get('wind', {}).get('speed', 'N/A')

    return (
        f"🌤 *Weather Forecast for {city_name}*\n"
        f"*Description:* {description.capitalize()}\n"
        f"*Temperature:* {temp}°C\n"
        f"*Feels Like:* {feels_like}°C\n"
        f"*Humidity:* {humidity}%\n"
        f"*Wind Speed:* {wind_speed} m/s\n\n"
        f"Friendly recommendation: {suggestion}\n"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when the command /start is issued"""
    welcome_message = (
        "👋 *Welcome to WeatherBot!*\n\n"
        "I can provide you with weather forecasts for any city around the world.\n\n"
        "Simply ask me something like:\n"
        "• What's the weather in Paris?\n"
        "• Weather in Tokyo tomorrow\n"
        "• New York weather in 3 days\n\n"
        "I'll provide you with temperature, feels-like temperature, humidity, and wind speed information.\n"
        "All forecasts are provided for 1:00 PM local time. 🕐"
    )
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages and respond with weather information"""
    message_text = update.message.text

    # Extract query details
    query_details = extract_query_details(message_text)
    if not query_details or query_details['city'] == 'NONE':
        await update.message.reply_text(
            "I couldn't identify a city in your message. Please try again with a city name.\n"
            "Example: What's the weather in Paris tomorrow?"
        )
        return

    # Fetch and process forecast
    forecast_data = fetch_forecast(query_details['city'])
    if not forecast_data:
        await update.message.reply_text(
            f"Sorry, I couldn't retrieve the forecast for {query_details['city']}."
        )
        return

    # Process forecast with GPT (always targeting 13:00)
    relevant_forecast = process_forecast_with_gpt(forecast_data['list'], query_details)
    if relevant_forecast:
        message = format_weather_message(relevant_forecast, query_details['city'])
    else:
        message = f"Sorry, I couldn't process the forecast data for {query_details['city']}."

    await update.message.reply_text(message, parse_mode='Markdown')


def main():
    """Main function to run the bot"""
    app = ApplicationBuilder().token(TELEGRAM_API_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()