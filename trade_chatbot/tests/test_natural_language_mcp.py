"""
Test script demonstrating natural language query processing with MCP wrapper
This shows how an AI agent can interpret user requests and call the MCP wrapper
"""
import requests
import json

def interpret_natural_language_query(query):
    """
    Simulate AI interpretation of natural language queries to financial symbols
    In a real implementation, this would use an LLM to interpret the query
    """
    query_lower = query.lower()
    
    # Simple mapping for demonstration purposes
    # In reality, this would be much more sophisticated using an LLM
    interpretations = {
        "what is the price of apple stock": {"method": "av.function.global_quote", "params": {"symbol": "AAPL"}},
        "how much is microsoft": {"method": "av.function.global_quote", "params": {"symbol": "MSFT"}},
        "price of tesla": {"method": "av.function.global_quote", "params": {"symbol": "TSLA"}},
        "what's the price of gold": {"method": "av.function.currency_exchange_rate", "params": {"from_currency": "XAU", "to_currency": "USD"}},
        "how much is bitcoin": {"method": "av.function.currency_exchange_rate", "params": {"from_currency": "BTC", "to_currency": "USD"}},
        "price of ethereum": {"method": "av.function.currency_exchange_rate", "params": {"from_currency": "ETH", "to_currency": "USD"}},
        "eur to usd exchange rate": {"method": "av.function.currency_exchange_rate", "params": {"from_currency": "EUR", "to_currency": "USD"}},
        "jpy to usd": {"method": "av.function.currency_exchange_rate", "params": {"from_currency": "JPY", "to_currency": "USD"}},
        "historical data for google": {"method": "av.function.time_series_daily", "params": {"symbol": "GOOGL", "outputsize": "compact"}},
        "find companies like tesla": {"method": "av.function.symbol_search", "params": {"keywords": "Tesla"}},
        "search for apple companies": {"method": "av.function.symbol_search", "params": {"keywords": "Apple"}},
        # Additional test cases
        "what is the price of amazon": {"method": "av.function.global_quote", "params": {"symbol": "AMZN"}},
        "google stock price": {"method": "av.function.global_quote", "params": {"symbol": "GOOGL"}},
        "btc usd": {"method": "av.function.currency_exchange_rate", "params": {"from_currency": "BTC", "to_currency": "USD"}},
        "eth usd": {"method": "av.function.currency_exchange_rate", "params": {"from_currency": "ETH", "to_currency": "USD"}},
        "usd jpy": {"method": "av.function.currency_exchange_rate", "params": {"from_currency": "USD", "to_currency": "JPY"}},
        "what is the price of tesla": {"method": "av.function.global_quote", "params": {"symbol": "TSLA"}},
        "amazon stock": {"method": "av.function.global_quote", "params": {"symbol": "AMZN"}},
        "microsoft price": {"method": "av.function.global_quote", "params": {"symbol": "MSFT"}},
    }
    
    # Try exact match first
    if query_lower in interpretations:
        return interpretations[query_lower]
    
    # Try partial match for more flexibility
    for key_phrase, interpretation in interpretations.items():
        if key_phrase in query_lower:
            return interpretation
    
    # Handle generic stock/crypto symbol queries
    # Extract potential symbols from the query
    import re
    # Look for potential stock/crypto symbols (uppercase letters, 1-5 chars)
    potential_symbols = re.findall(r'\b[A-Z]{1,5}\b', query)
    
    if potential_symbols:
        # Filter out common words that aren't symbols
        common_words = {'USD', 'EUR', 'JPY', 'GBP', 'BTC', 'ETH', 'XAU', 'XAG', 'THE', 'AND', 'FOR', 'TO', 'OF', 'IN', 'ON', 'AT', 'BY'}
        valid_symbols = [sym for sym in potential_symbols if sym not in common_words]
        
        if valid_symbols:
            symbol = valid_symbols[0]  # Take the first valid symbol
            return {"method": "av.function.global_quote", "params": {"symbol": symbol}}
    
    # Default fallback for unrecognized queries
    return None

def call_mcp_wrapper(method, params):
    """
    Call our MCP wrapper with the specified method and parameters
    """
    url = 'http://localhost:5001/api/mcp_wrapper'
    
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: HTTP {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error calling MCP wrapper: {str(e)}")
        return None

def format_response_for_user(method, result):
    """
    Format the MCP response into a user-friendly message
    """
    if not result or "result" not in result:
        return "Sorry, I couldn't retrieve the requested information."
    
    data = result["result"]
    
    # Handle error responses from Alpha Vantage API
    if "Error Message" in data:
        error_msg = data["Error Message"]
        return f"API Error: {error_msg}"
    
    if "Information" in data:
        info_msg = data["Information"]
        return f"Information: {info_msg}"
    
    if method == "av.function.global_quote" and "Global Quote" in data:
        quote = data["Global Quote"]
        symbol = quote.get("01. symbol", "Unknown")
        price = quote.get("05. price", "N/A")
        change = quote.get("09. change", "N/A")
        change_pct = quote.get("10. change percent", "N/A")
        return f"The current price of {symbol} is ${price}. Change: {change} ({change_pct})"
    
    elif method == "av.function.currency_exchange_rate" and "Realtime Currency Exchange Rate" in data:
        rate_data = data["Realtime Currency Exchange Rate"]
        from_curr = rate_data.get("1. From_Currency Code", "N/A")
        to_curr = rate_data.get("3. To_Currency Code", "N/A")
        rate = rate_data.get("5. Exchange Rate", "N/A")
        last_refresh = rate_data.get("6. Last Refreshed", "N/A")
        return f"1 {from_curr} = {rate} {to_curr} (Last updated: {last_refresh})"
    
    elif method == "av.function.time_series_daily" and "Time Series (Daily)" in data:
        meta = data.get("Meta Data", {})
        symbol = meta.get("2. Symbol", "Unknown")
        ts = data["Time Series (Daily)"]
        latest_date = sorted(ts.keys())[-1] if ts.keys() else "N/A"
        if latest_date != "N/A":
            latest_data = ts[latest_date]
            close_price = latest_data.get("4. close", "N/A")
            volume = latest_data.get("5. volume", "N/A")
            return f"Historical data for {symbol} on {latest_date}: Close price ${close_price}, Volume {volume}"
        else:
            return f"Historical data for {symbol} is available."
    
    elif method == "av.function.symbol_search" and "bestMatches" in data:
        matches = data["bestMatches"]
        if matches:
            response = f"I found {len(matches)} matches:\n"
            for i, match in enumerate(matches[:3]):  # Show top 3 matches
                symbol = match.get("1. symbol", "N/A")
                name = match.get("2. name", "N/A")
                response += f"{i+1}. {symbol} - {name}\n"
            return response.strip()
        else:
            return "No matches found for your search."
    
    else:
        # Try to provide a more helpful response for unexpected data
        if isinstance(data, dict) and data:
            first_key = list(data.keys())[0] if data.keys() else "Unknown"
            return f"Data retrieved successfully. Main data type: {first_key}"
        elif isinstance(data, dict) and not data:
            return "No data available for this request."
        else:
            return f"Data retrieved successfully."

def test_natural_language_mcp_integration():
    """
    Test the complete flow: natural language query -> AI interpretation -> MCP call -> User response
    """
    print("=" * 80)
    print("NATURAL LANGUAGE QUERY TESTING WITH MCP WRAPPER")
    print("=" * 80)
    print("This demonstrates how an AI agent would process user requests and use the MCP wrapper")
    print()
    
    # Test queries that simulate user natural language input
    test_queries = [
        "What is the price of Apple stock?",
        "How much is Microsoft?",
        "What's the price of gold?",
        "How much is Bitcoin?",
        "Price of Ethereum",
        "EUR to USD exchange rate",
        "Historical data for Google",
        "Find companies like Tesla",
        "Search for Apple companies",
        # Additional test cases
        "What is the price of Amazon?",
        "Google stock price",
        "BTC USD",
        "ETH USD"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"{i}. User Query: \"{query}\"")
        
        # Step 1: AI interprets the natural language query
        interpretation = interpret_natural_language_query(query)
        
        if interpretation:
            method = interpretation["method"]
            params = interpretation["params"]
            print(f"   AI Interpretation:")
            print(f"     Method: {method}")
            print(f"     Parameters: {params}")
            
            # Step 2: Call the MCP wrapper with interpreted method and parameters
            print(f"   Calling MCP Wrapper...")
            result = call_mcp_wrapper(method, params)
            
            # Step 3: Format response for user
            if result:
                user_response = format_response_for_user(method, result)
                print(f"   User Response: {user_response}")
            else:
                print(f"   User Response: Sorry, I couldn't retrieve the data.")
        else:
            print(f"   AI Interpretation: Unable to interpret query")
            print(f"   User Response: I'm not sure what you're asking for. Could you please be more specific?")
        
        print()  # Blank line between queries
    
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

def demo_interactive_mode():
    """
    Demo an interactive mode where users can enter their own queries
    """
    print("\n" + "=" * 80)
    print("INTERACTIVE DEMO MODE")
    print("=" * 80)
    print("Enter natural language queries (type 'quit' to exit):")
    print("Examples:")
    print("  - What is the price of Apple stock?")
    print("  - How much is Bitcoin?")
    print("  - EUR to USD exchange rate")
    print("  - Find companies like Tesla")
    print("-" * 80)
    
    while True:
        try:
            query = input("\nEnter your query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not query:
                continue
                
            print(f"\nProcessing: \"{query}\"")
            
            # Interpret the query
            interpretation = interpret_natural_language_query(query)
            
            if interpretation:
                method = interpretation["method"]
                params = interpretation["params"]
                print(f"Interpreted as: {method} with params {params}")
                
                # Call MCP wrapper
                result = call_mcp_wrapper(method, params)
                
                # Format response
                if result:
                    user_response = format_response_for_user(method, result)
                    print(f"Response: {user_response}")
                else:
                    print("Sorry, I couldn't retrieve the data.")
            else:
                print("I'm not sure what you're asking for. Could you please be more specific?")
                print("Try queries like:")
                print("  - What is the price of Apple stock?")
                print("  - How much is Bitcoin?")
                print("  - EUR to USD exchange rate")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Run the test suite
    test_natural_language_mcp_integration()
    
    # Uncomment the line below to run interactive demo
    # demo_interactive_mode()