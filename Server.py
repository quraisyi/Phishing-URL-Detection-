import paho.mqtt.client as mqtt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import json
import re

# load dataset
csv_path = "Dataset/phishing_site_urls.csv"
data = pd.read_csv(csv_path)

# Pra-pemrosesan dataset
data = data[['URL', 'Label']]
data.columns = ['url', 'label']
data['label'] = data['label'].map({'bad': 1, 'good': 0})  # Label: 1 untuk phishing, 0 untuk aman

# Ekstrak fitur dan latih model
X = data['url']
y = data['label']

# CountVectorizer untuk ekstraksi fitur berbasis karakter n-gram
vectorizer = CountVectorizer(analyzer="char", ngram_range=(3, 3))  # Menggunakan N-gram berbasis karakter
X_vectorized = vectorizer.fit_transform(X)

# Bagi dataset menjadi data latih dan uji
X_train, X_test, y_train, y_test = train_test_split(X_vectorized, y, test_size=0.2, random_state=42)

# Latih Logistic Regression
model = LogisticRegression()
model.fit(X_train, y_train)

# Evaluasi model
accuracy = model.score(X_test, y_test)
#print(f"Akurasi model: {accuracy:.2f}")

print('**********Deteksi Phishing**********')
print('***************Server***************')
# Fungsi untuk mendeteksi phishing URL
def is_phishing(url):
    try:
        # Membersihkan URL
        clean_url = re.sub(r'[^\w:/.\-]', ' ', url)  # Pertahankan karakter penting
        url_vectorized = vectorizer.transform([clean_url])
        return model.predict(url_vectorized)[0] == 1
    except Exception as e:
        print(f"Error memproses URL: {url}, Error: {e}")
        return False

# Implementasi server mqtt
def on_connect(client, userdata, flags, rc):
    print(f"Server terhubung dengan kode hasil: {rc}")
    client.subscribe("chat/general")

def on_message(client, userdata, msg):
    message_data = json.loads(msg.payload.decode("utf-8"))
    sender = message_data['sender']
    message = message_data['message']
    print(f"Pesan diterima dari {sender}: {message}")

    # Deteksi URL phishing
    urls = re.findall(r'(https?://[^\s]+|www\.[^\s]+)', message)  # Cari URL dalam pesan
    print(f"URL yang ditemukan: {urls}")

    if not urls:
        warning = False
    else:
        warning = any(is_phishing(url) for url in urls)

    # Format pesan respons
    if warning:
        response = {
            "sender": "Server",
            "message": f"Peringatan: Pesan dari {sender} mengandung URL phishing!",
            "warning": True
        }
    else:
        response = {
            "sender": sender,
            "message": message,
            "warning": False
        }

    # Kirim pesan ke klien penerima
    if sender == "Client1":
        client.publish("chat/client2", json.dumps(response))
        print(f"Pesan dikirim ke Client2: {response}")
    elif sender == "Client2":
        client.publish("chat/client1", json.dumps(response))
        print(f"Pesan dikirim ke Client1: {response}")

# Inisialisasi MQTT server
server = mqtt.Client("Server1")
server.on_connect = on_connect
server.on_message = on_message

broker_address = "broker.emqx.io"
server.connect(broker_address, 1883, 60)
server.loop_forever()
