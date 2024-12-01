import paho.mqtt.client as mqtt
import json

print('**********Deteksi Phishing**********')
print('***************Client1**************')
# Fungsi callback saat terhubung ke server
def on_connect(client, userdata, flags, rc):
    print("Client1 terhubung.")
    client.subscribe("chat/client1")

# Fungsi callback saat menerima pesan
def on_message(client, userdata, msg):
    message_data = json.loads(msg.payload.decode("utf-8"))
    sender = message_data['sender']
    message = message_data['message']
    warning = message_data.get('warning', False)

    if warning:
        print(f"[PERINGATAN] Pesan dari {sender}: {message}")
    else:
        print(f"[INFO]Pesan dari {sender}: {message}")

# Fungsi untuk mengirim pesan
def send_message(client):
    while True:
        message = input("")
        payload = json.dumps({"sender": "Client1", "message": message})
        client.publish("chat/general", payload)

# Inisialisasi MQTT Client
client = mqtt.Client("Client1")
client.on_connect = on_connect
client.on_message = on_message

broker_address = "broker.emqx.io"
client.connect(broker_address, 1883, 60)

# Mulai loop dan antarmuka pengiriman pesan
client.loop_start()
send_message(client)
