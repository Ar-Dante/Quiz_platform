import csv
import json
from abc import ABC, abstractmethod


class AbstractDataLoader(ABC):
    @abstractmethod
    def load(self, file_path):
        pass

    @abstractmethod
    def save(self, data, file_path):
        pass


class JSONDataLoader(AbstractDataLoader):
    def load(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data

    def save(self, data, file_path):
        with open(file_path, 'w') as file:
            if len(data) > 0:
                json.dump(data, file, indent=4)


class CSVDataLoader(AbstractDataLoader):
    def load(self, file_path):
        data = []
        with open(file_path, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
        return data

    def save(self, data, file_path):
        with open(file_path, 'w', newline='') as file:
            if len(data) > 0:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
