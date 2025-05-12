import os
import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_brand_info(brand_name):
    try:
        # Create a detailed prompt for the OpenAI API
        prompt = f"""Analyze the brand "{brand_name}" and provide information in the following JSON format:
        {{
            "domain": "Official website domain",
            "description": "A detailed paragraph about the brand, its history, market position, and current trends",
            "product_lines": ["List of main product lines or categories"]
        }}
        Please ensure the description is detailed and includes information about the brand's market position and current trends."""

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a brand analysis expert providing detailed information about brands."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        # Parse the response
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        return {"error": str(e)}

def get_topics(brand_name, product_line):
    try:
        prompt = f"""You are a marketing strategist with deep empathy for customers. Think like a potential buyer who has a specific pain point that {brand_name}'s {product_line} solves. The user may or may not know about this brand and is only concerned with their issue. Generate 10 search-style conversation topics or customer questions.

The topics should be in the style of search queries or discussion titles, focusing on solutions to real customer needs. Each topic should be concise and natural, as if typed into a search engine.

Example format:
best wireless computer mouse for productivity
ergonomic wireless mice for office work
affordable Bluetooth mice for laptops
advanced AI-enabled mice for gaming
ergonomic computer accessories for reducing wrist strain
top-rated wireless mice for professionals
lightweight travel mice for business trips
comparison of wireless mice with multi-device capabilities
best value wireless keyboards and mice bundle
user-friendly mice for hybrid meeting setups

Make sure each topic:
- Focuses on solving a specific customer pain point
- Uses natural search language
- Is relevant to {product_line}
- Is concise and focused

Format the response as a JSON array of strings."""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a marketing strategist who deeply understands customer pain points and search behavior."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )

        # Parse the response
        topics = json.loads(response.choices[0].message.content)
        return topics
    except Exception as e:
        return {"error": str(e)}

def respond(message, history):
    # If there's no history, this is the first message (brand name)
    if not history:
        # Get brand information
        brand_info = get_brand_info(message)
        
        if "error" in brand_info:
            return f"Sorry, I encountered an error analyzing the brand: {brand_info['error']}"
        
        # Store brand name in the first message for later use
        response = f"""Here's what I found about {message}:

Domain: {brand_info['domain']}

Description:
{brand_info['description']}

Product Lines:
{chr(10).join('- ' + line for line in brand_info['product_lines'])}

Please select one of the product lines above to analyze further."""
        
        return response
    
    # For subsequent messages (product line selection)
    if len(history) == 1:
        brand_name = history[0][0]  # Get the brand name from the first interaction
        product_line = message
        
        # Get topics for the selected product line
        topics = get_topics(brand_name, product_line)
        
        if "error" in topics:
            return f"Sorry, I encountered an error generating topics: {topics['error']}"
        
        response = f"""Here are 10 search-style conversation topics that customers might use when looking for solutions that {brand_name}'s {product_line} provides:

{chr(10).join('1. ' + topics[0] if i == 0 else str(i+1) + '. ' + topic for i, topic in enumerate(topics))}

These topics represent real search queries that could lead customers to discover your brand's solutions.

Click "Continue" when you're ready to move on to the next step."""
        
        return response
    
    return "Let's proceed with the next step of the analysis."

# Create the Gradio interface
chat_interface = gr.ChatInterface(
    respond,
    title="Brand Perception Analysis",
    description="Hi, I am your AI search assistant that can help you understand how your brand is perceived by AI LLM models. Please provide me with your brand name.",
    theme="soft"
)

if __name__ == "__main__":
    chat_interface.launch()