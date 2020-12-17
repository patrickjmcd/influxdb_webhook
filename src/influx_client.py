from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError, InfluxDBServerError
from requests import ConnectTimeout, ConnectTimeout
import sys


class InfluxClient(object):
    def __init__(self, address, database, username, password, port=8086, ssl=False, verify_ssl=False, timeout=5):
        self.database = database
        influx = InfluxDBClient(
            address,
            port,
            database=database,
            ssl=ssl,
            verify_ssl=verify_ssl,
            username=username,
            password=password,
            timeout=timeout
        )
        try:
            print('Testing connection to InfluxDb using provided credentials')
            influx.get_list_users()  # TODO - Find better way to test connection and permissions
            print('Successful connection to InfluxDb')
        except (ConnectTimeout, InfluxDBClientError, ConnectionError) as e:
            if isinstance(e, ConnectTimeout):
                print(
                    'Unable to connect to InfluxDB at the provided address (%s)', address)
            elif e.code == 401:
                print(
                    'Unable to connect to InfluxDB with provided credentials')
            else:
                print(
                    'Failed to connect to InfluxDB for unknown reason')
                print(e)

            sys.exit(1)

        self.client = influx

    def write(self, data):
        try:
            self.client.write_points(data)
        except (InfluxDBClientError, ConnectionError, InfluxDBServerError) as e:
            if hasattr(e, 'code') and e.code == 404:
                print(
                    'Database %s Does Not Exist.  Attempting To Create', self.database)
                self.client.create_database(self.database)
                self.client.write_points(data)
                return

            print('Failed To Write To InfluxDB')
            print(e)
            return "error writing to InfluxDB: {}".format(e)

        print('Data written to InfluxDB')
        return('Data written to InfluxDB')
