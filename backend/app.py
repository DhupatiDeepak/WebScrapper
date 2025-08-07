from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

@app.route('/api/scrape', methods=['POST'])
def scrape():
    try:
        data = request.get_json()
        url = data.get('url')
        include_images = data.get('includeImages', False)

        if not url:
            return jsonify({'success': False, 'message': 'URL is required'}), 400

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return jsonify({'success': False, 'message': 'Failed to fetch website content'}), 400

        soup = BeautifulSoup(response.content, 'html.parser')

        # Get the page title
        title = soup.title.string.strip() if soup.title else "No Title"

        # Try to find meaningful content
        main_content = soup.find('main') or soup.find('article') or soup.body
        if not main_content:
            return jsonify({'success': False, 'message': 'No readable content found'}), 400

        # Allowed tags for structured clean data
        allowed_tags = ['h1', 'h2', 'h3', 'p', 'ul', 'ol', 'li']
        cleaned = ''

        for tag in main_content.find_all(allowed_tags):
            cleaned += str(tag)

        # Handle images
        images = []
        if include_images:
            for img in main_content.find_all('img'):
                src = img.get('src')
                if src and src.startswith('http'):
                    images.append(src)

        return jsonify({
            'success': True,
            'title': title,
            'content': cleaned,
            'images': images
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
