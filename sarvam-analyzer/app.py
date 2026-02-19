from flask import Flask, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load Environment Variables
load_dotenv()

from routes.main import main_bp

def create_app():
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    CORS(app)

    # Register Blueprints
    app.register_blueprint(main_bp, url_prefix='/api')

    @app.route('/')
    def index():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
