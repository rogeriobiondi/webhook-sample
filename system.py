import hashlib
from datetime import datetime

from art import text2art

from app import kafka


class Temperature(object):
    """
    Temperature Event Description
    """
    def __init__(self, 
                 city: str, 
                 reading: float, 
                 unit: str, 
                 timestamp: datetime):
        self.city = city
        self.reading = reading
        self.unit = unit
        self.timestamp = timestamp  
        self.id = hashlib.md5(
            (city + str(reading) + unit + timestamp.isoformat())\
                .encode('utf-8')).hexdigest()

if __name__ == '__main__':
    print(text2art("System"))
    print("producing system message...\n")

    # Create events 
    temp1 = Temperature('São Paulo', 18, 'C', datetime.now())
    temp2 = Temperature('New York', 16, 'C', datetime.now())
    temp3 = Temperature('Tokyo', 23, 'C', datetime.now())
    temp4 = Temperature('Roma', 8, 'C', datetime.now())
    temp5 = Temperature('Paris', 6, 'C', datetime.now())
    kafka.produce_message(temp1.__dict__)
    kafka.produce_message(temp2.__dict__)
    kafka.produce_message(temp3.__dict__)
    kafka.produce_message(temp4.__dict__)
    kafka.produce_message(temp5.__dict__)
