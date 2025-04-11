from app import app

def list_routes():
    """List all routes in the Flask app"""
    print("Available routes:")
    print("=" * 30)
    
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods))
        print(f"{rule} ({methods})")
    
    print("=" * 30)

if __name__ == "__main__":
    print("Debugging Flask routes")
    list_routes()
    
    print("\nMake sure to check that the routes include:")
    print("- /")
    print("- /api/health")
    print("- /api/documents")
    print("- /api/tags")
