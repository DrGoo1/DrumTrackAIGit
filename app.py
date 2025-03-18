from drumtrackkit import create_app

app = create_app()

if __name__ == '__main__':
    # Using host='0.0.0.0' is essential for Docker to expose the app outside the container
    app.run(host='0.0.0.0', debug=True)