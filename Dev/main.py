from flask import Flask, request, redirect, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import shortuuid


# Initialize Flask app
app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate('sa_firebase.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Reference to the URLs collection
urls_collection = db.collection('urls')


@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.json
    original_url = data.get('originalUrl')
    short_url = shortuuid.ShortUUID().random(length=6)

    urls_collection.document(short_url).set({
        'originalUrl': original_url,
        'shortUrl': short_url,
        'createdAt': firestore.SERVER_TIMESTAMP,
        'clicks': 0
    })

    return jsonify({'originalUrl': original_url, 'shortUrl': short_url})


@app.route('/<short_url>', methods=['GET'])
def redirect_url(short_url):
    url_doc = urls_collection.document(short_url).get()

    if not url_doc.exists:
        return jsonify({'error': 'URL not found'}), 404

    url_data = url_doc.to_dict()
    urls_collection.document(short_url).update({
        'clicks': firestore.Increment(1)
    })

    return redirect(url_data['originalUrl'])


if __name__ == '__main__':
    app.run(debug=True)