from app import app,port,init_db

if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=port)
