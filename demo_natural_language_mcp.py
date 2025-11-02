"""
Simple demonstration of natural language query processing with MCP wrapper concept
This shows how an AI agent would interpret user requests and call the MCP wrapper
without making actual API calls to avoid rate limits
"""
import json

def interpret_natural_language_query(query):
    """
    Simulate AI interpretation of natural language queries to financial symbols
    """
    query_lower = query.lower()
    
    # Simple mapping for demonstration
    interpretations = {
        "what is the price of apple stock": {"method": "av.function.global_quote", "params": {"symbol": "AAPL"}},
        "how much is bitcoin": {"method": "av.function.currency_exchange_rate", "params": {"from_currency": "BTC", "to_currency": "USD"}},
        "eur to usd exchange rate": {"method": "av.function.currency_exchange_rate", "params": {"from_currency": "EUR", "to_currency": "USD"}},
        "historical data for google": {"method": "av.function.time_series_daily", "params": {"symbol": "GOOGL", "outputsize": "compact"}},
    }
    
    # Try exact match first
    if query_lower in interpretations:
        return interpretations[query_lower]
    
    # Try partial match
    for key_phrase, interpretation in interpretations.items():
        if key_phrase in query_lower:
            return interpretation
    
    return None

def demonstrate_mcp_call(method, params):
    """
    Demonstrate what an MCP call would look like without actually making the API call
    """
    print(f"   MCP Wrapper Call:")
    print(f"     Method: {method}")
    print(f"     Parameters: {params}")
    print(f"     URL: http://localhost:5001/api/mcp_wrapper")
    print(f"     Protocol: JSON-RPC 2.0")
    
    # Show what the JSON-RPC request would look like
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    
    print(f"     Request Body: {json.dumps(payload, indent=6)}")
    
    # Show what a typical response would look like
    if method == "av.function.global_quote":
        sample_response = {
            "jsonrpc": "2.0",
            "result": {
                "Global Quote": {
                    "01. symbol": params.get("symbol", "UNKNOWN"),
                    "02. open": "150.0000",
                    "03. high": "155.0000",
                    "04. low": "149.0000",
                    "05. price": "153.2500",
                    "06. volume": "1000000",
                    "07. latest trading day": "2025-11-02",
                    "08. previous close": "152.0000",
                    "09. change": "1.2500",
                    "10. change percent": "0.8224%"
                }
            },
            "id": 1
        }
    elif method == "av.function.currency_exchange_rate":
        sample_response = {
            "jsonrpc": "2.0",
            "result": {
                "Realtime Currency Exchange Rate": {
                    "1. From_Currency Code": params.get("from_currency", "FROM"),
                    "2. From_Currency Name": "From Currency Name",
                    "3. To_Currency Code": params.get("to_currency", "TO"),
                    "4. To_Currency Name": "To Currency Name",
                    "5. Exchange Rate": "1.2345",
                    "6. Last Refreshed": "2025-11-02 10:00:00",
                    "7. Time Zone": "UTC",
                    "8. Bid Price": "1.2340",
                    "9. Ask Price": "1.2350"
                }
            },
            "id": 1
        }
    else:
        sample_response = {
            "jsonrpc": "2.0",
            "result": {
                "Information": "Sample data for demonstration purposes"
            },
            "id": 1
        }
    
    print(f"     Sample Response: {json.dumps(sample_response, indent=6)}")
    
    return sample_response

def format_response_for_user(method, result):
    """
    Format the MCP response into a user-friendly message
    """
    if not result or "result" not in result:
        return "Sorry, I couldn't retrieve the requested information."
    
    data = result["result"]
    
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
    
    else:
        return f"Data would be retrieved successfully."

def demonstrate_natural_language_mcp_flow():
    """
    Demonstrate the complete flow: natural language query -> AI interpretation -> MCP call -> User response
    """
    print("=" * 80)
    print("NATURAL LANGUAGE QUERY DEMONSTRATION WITH MCP WRAPPER")
    print("=" * 80)
    print("This demonstrates how an AI agent would process user requests and use the MCP wrapper")
    print("without making actual API calls to avoid rate limits.")
    print()
    
    # Test queries that simulate user natural language input
    test_queries = [
        "What is the price of Apple stock?",
        "How much is Bitcoin?",
        "EUR to USD exchange rate",
        "Historical data for Google"
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
            
            # Step 2: Call the MCP wrapper (demonstration only)
            print(f"   Calling MCP Wrapper...")
            result = demonstrate_mcp_call(method, params)
            
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
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)
    print()
    print("Key Benefits of This Approach:")
    print("1. Natural Language Processing: Users can ask questions in plain English")
    print("2. Standardized Interface: Uses MCP protocol for AI agent compatibility")
    print("3. Flexible Interpretation: Handles various phrasings of the same request")
    print("4. Extensible Design: Easy to add new interpretations and methods")
    print("5. Error Handling: Graceful handling of unrecognized queries")

if __name__ == "__main__":
    demonstrate_natural_language_mcp_flow()