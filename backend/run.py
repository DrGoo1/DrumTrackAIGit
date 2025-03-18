from app import app

if __name__ == '__main__':
    # Print out all routes when starting
    print("\nRegistered Routes:")
    for rule in app.url_map.iter_rules():
        print(f"Endpoint: {rule.endpoint}")
        print(f"Route: {rule.rule}")
        print(f"Methods: {list(rule.methods)}")
        print("---")

    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)