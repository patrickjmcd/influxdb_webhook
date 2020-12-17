
from os import getenv
import sys
import json
from flask import Flask
from flask import request
from influx_client import InfluxClient

app = Flask(__name__)

influx_address = getenv('INFLUXDB_ADDRESS')
influx_port = getenv('INFLUXDB_PORT') or 8086
influx_port = int(influx_port)
influx_database = getenv('INFLUXDB_DB') or "webhook"
influx_user = getenv('INFLUXDB_USER')
influx_password = getenv('INFLUXDB_PASSWORD')
influx_ssl = bool(getenv('INFLUXDB_SSL'))
influx_verify_ssl = bool(getenv('INFLUXDB_VERIFYSSL'))

influx = InfluxClient(influx_address, influx_database, influx_user,
                      influx_password, influx_port, influx_ssl, influx_verify_ssl)


@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello, World!'


@app.route('/particle', methods=['POST'])
def particle_post():
    try:
        data = request.get_json()
        if not data:
            raise Exception("invalid JSON body")

        app.logger.info(data)
        sent_data = json.loads(data['data'])

        influx_data_point = [
            {
                "measurement": sent_data['tags']['location'],
                "fields": sent_data['values'],
                "time": data['published_at']
            }
        ]
        return influx.write(influx_data_point)

    except Exception as e:
        app.logger.error("Unable to parse message")
        app.logger.error(e)
        return "{}".format(e)


@app.route('/ttn', methods=['POST'])
def thingsnetwork_post():
    #     {
    #   "app_id": "my-app-id",              // Same as in the topic
    #   "dev_id": "my-dev-id",              // Same as in the topic
    #   "hardware_serial": "0102030405060708", // In case of LoRaWAN: the DevEUI
    #   "port": 1,                          // LoRaWAN FPort
    #   "counter": 2,                       // LoRaWAN frame counter
    #   "is_retry": false,                  // Is set to true if this message is a retry (you could also detect this from the counter)
    #   "confirmed": false,                 // Is set to true if this message was a confirmed message
    #   "payload_raw": "AQIDBA==",          // Base64 encoded payload: [0x01, 0x02, 0x03, 0x04]
    #   "payload_fields": {},               // Object containing the results from the payload functions - left out when empty
    #   "metadata": {
    #     "time": "1970-01-01T00:00:00Z",   // Time when the server received the message
    #     "frequency": 868.1,               // Frequency at which the message was sent
    #     "modulation": "LORA",             // Modulation that was used - LORA or FSK
    #     "data_rate": "SF7BW125",          // Data rate that was used - if LORA modulation
    #     "bit_rate": 50000,                // Bit rate that was used - if FSK modulation
    #     "coding_rate": "4/5",             // Coding rate that was used
    #     "gateways": [
    #       {
    #         "gtw_id": "ttn-herengracht-ams", // EUI of the gateway
    #         "timestamp": 12345,              // Timestamp when the gateway received the message
    #         "time": "1970-01-01T00:00:00Z",  // Time when the gateway received the message - left out when gateway does not have synchronized time
    #         "channel": 0,                    // Channel where the gateway received the message
    #         "rssi": -25,                     // Signal strength of the received message
    #         "snr": 5,                        // Signal to noise ratio of the received message
    #         "rf_chain": 0,                   // RF chain where the gateway received the message
    #         "latitude": 52.1234,             // Latitude of the gateway reported in its status updates
    #         "longitude": 6.1234,             // Longitude of the gateway
    #         "altitude": 6                    // Altitude of the gateway
    #       },
    #       //...more if received by more gateways...
    #     ],
    #     "latitude": 52.2345,              // Latitude of the device
    #     "longitude": 6.2345,              // Longitude of the device
    #     "altitude": 2                     // Altitude of the device
    #   },
    #   "downlink_url": "https://integrations.thethingsnetwork.org/ttn-eu/api/v2/down/my-app-id/my-process-id?key=ttn-account-v2.secret"
    # }
    # try:
    sent_data = request.get_json()
    if not sent_data:
        raise Exception("invalid JSON body")

    app.logger.info(sent_data)

    influx_data_point = [
        {
            "measurement": sent_data['app_id'],
            "fields": {
                "moisture_value": sent_data['payload_fields']['soilMoisture'],
                "status": sent_data['payload_fields']['status']
            },
            "tags": {
                "device_id": sent_data['dev_id'],
                "hardware_serial": sent_data['hardware_serial'],
                "port": sent_data['port'],
                "frequency": sent_data['metadata']['frequency'],
                "gateway_id": sent_data['metadata']['gateways'][0]['gtw_id'],
                "gateway_channel": sent_data['metadata']['gateways'][0]['channel'],
                "gateway_rssi": sent_data['metadata']['gateways'][0]['rssi'],
                "gateway_snr": sent_data['metadata']['gateways'][0]['snr']
            },
            "time": sent_data['metadata']['time']
        }
    ]
    return influx.write(influx_data_point)

    # except Exception as e:
    #     app.logger.error("Unable to parse message")
    #     app.logger.error(e)
    #     return "{}".format(e)
