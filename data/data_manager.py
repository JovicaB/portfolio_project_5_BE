import json

from collections import Counter
from datetime import date


CONFIG_DATA = "data/mrs_config.json"
USERS_DATA = "data/mrs_users.json"


class JSONData:
    def __init__(self, filename) -> None:
        self.filename = filename

    def read_json(self, key=None):
        """
        Read data from the JSON file based on a specified key.

        This method reads the JSON file, retrieves the value associated with the provided key, and returns it.
        If no key is provided, return 1. If the key is not found, return 1. If the key is found, return 2.

        Parameters:
        - key (str, optional): The key used to retrieve the data from the JSON file.

        Returns:
        The value associated with the specified key in the JSON file if the key is present, else 1.

        Example:
        >>> json_data = JSONData("data.json")
        >>> result = json_data.read_json("my_key")
        >>> print(result)

        """
        try:
            with open(self.filename, 'r') as json_file:
                data = json.load(json_file)

                if key is not None and key in data:
                    result = data[key]
                    return result
                else:
                    return data

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading data from {self.filename}: {e}")
            return None

    def write_json(self, keys, value):
        """
        Write data to the JSON file using a specified set of keys.

        This method reads the JSON file, modifies the value associated with the specified set of keys, and updates the JSON file with the new data.

        Parameters:
        - keys (list): A list of keys to navigate through the JSON structure to locate the target value.
        - value: The new value to be written to the JSON file.

        Returns:
        A message indicating the successful update of the JSON file.

        Example:
        >>> json_data = JSONData("data.json")
        >>> result = json_data.write_json(["my", "nested", "key"], "new_value")
        >>> print(result)

        """
        try:
            with open(self.filename, 'r+') as json_file:
                data = json.load(json_file)
                nested_dict = data
                for key in keys[:-1]:
                    nested_dict = nested_dict.setdefault(key, {})
                nested_dict[keys[-1]] = value
                json_file.seek(0)
                json.dump(data, json_file, indent=4)
                json_file.truncate()
            return f"'{'/'.join(keys)}' updated in the JSON file"
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading or writing data: {e}")
            return None

    def write_to_interview_sessions(self, main_key, value):
        """
        Update data in the 'interview_sessions' key in the JSON file.

        This method updates the provided key with the new value in the 'interview_sessions' key of the JSON file.

        Parameters:
        - main_key: The key to update in the 'interview_sessions' key.
        - value: The new value to be associated with the key.

        Returns:
        A message indicating the successful update of the JSON file.

        Example:
        >>> json_data = JSONData("data.json")
        >>> result = json_data.write_to_interview_sessions("existing_key", "new_value")
        >>> print(result)

        """
        try:
            with open(self.filename, 'r+') as json_file:
                data = json.load(json_file)

                # if 'interview_sessions' in data and isinstance(data['interview_sessions'], dict):
                #     data["interview_sessions"][main_key] = value
                # else:
                #     data["interview_sessions"] = {main_key: value}

                data["interview_sessions"] = value

                json_file.seek(0)
                json.dump(data, json_file, indent=4)
                json_file.truncate()

            return f"'{main_key}' updated in the 'interview_sessions' key of the JSON file"
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading or writing data: {e}")
            return None


class DateEncoder(json.JSONEncoder):
    """
        Convert date objects to ISO format when encoding to JSON.

        This method is used as part of the JSON encoding process to handle date objects.

        Parameters:
        - obj: The object being encoded.

        Returns:
        If the object is a date, its ISO format representation; otherwise, the default JSON encoding.

        Example:
        >>> json_data = {"date": date(2023, 11, 8)}
        >>> json_string = json.dumps(json_data, cls=DateEncoder)
        >>> print(json_string)

        """

    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


class DataExtractor:
    def __init__(self) -> None:
        self.config_data = JSONData(CONFIG_DATA)
        self.users_data = JSONData(USERS_DATA)

    def get_songs_probabilities_data(self, set):
        '''Get complete config data from JSON object'''
        key = 'songs_probabilities_set' + str(set)
        return self.config_data.read_json(key)

    def get_users_data(self):
        '''Get complete users data from JSON object'''
        user_data = self.users_data.read_json()
        return user_data

    def get_user_count(self):
        '''Get complete users data from JSON object'''
        user_data = self.users_data.read_json()
        return len(user_data)

    def get_songs_data(self):
        '''Get complete songs data from JSON object'''
        return self.users_data.read_json()

    def get_song_count(self):
        '''Get complete users data from JSON object'''
        user_data = self.users_data.read_json()
        random_user = None
        for user in user_data:
            random_user = user
            break

        return len(user_data[random_user]['played_songs'])

    def get_inner_data(self, data_type: str, key: str):
        ''' 
        Get inner data from one of the three JSON objects.

        Parameters:
            data_type (str): Type of data ('users', 'songs', 'genres').
            key (str): The key to access the inner data within the selected JSON object.

        Returns:
            dict/list or None: The inner data for the selected JSON object, or None if data_type is not recognized.
        '''
        if data_type not in ('users', 'songs', 'genres'):
            raise ValueError(
                "Invalid data_type. Must be one of 'users', 'songs', or 'genres'.")

        data = None

        if data_type == 'users':
            data = self.get_users_data()
        elif data_type == 'songs':
            data = self.get_songs_data()

        return data

    def get_similar_bpm_songs(self, song_id) -> list:
        '''Retrieves songs with similar BPM values and the same genre as the given song_id

        Parameters:
            song_id: (str) The unique song identifier of currently played song.

        Returns: A list of song IDs with similar BPM values and the same genre as the given song_id.
        '''

        songs_data = self.get_songs_data()
        song_bpm = songs_data[song_id]['BPM']
        song_genre = songs_data[song_id]['genre']

        song_list = {}

        for id, genre_bpm in songs_data.items():
            if genre_bpm['genre'] == song_genre and song_id != id:
                song_list[id] = genre_bpm['BPM']

        sorted_data = dict(
            sorted(song_list.items(), key=lambda item: abs(item[1] - song_bpm)))
        song_list = [key for key in sorted_data.keys()]

        return song_list

    def get_similar_bpm_songs(self, song_id) -> list:
        '''Retrieves songs with similar BPM values and the same genre as the given song_id

        Parameters:
            song_id: (str) The unique song identifier of currently played song.

        Returns: A list of song IDs with similar BPM values and the same genre as the given song_id.
        '''

        songs_data = self.get_songs_data()
        song_bpm = songs_data[song_id]['BPM']
        song_genre = songs_data[song_id]['genre']

        song_list = {}

        for id, genre_bpm in songs_data.items():
            if genre_bpm['genre'] == song_genre and song_id != id:
                song_list[id] = genre_bpm['BPM']

        sorted_data = dict(
            sorted(song_list.items(), key=lambda item: abs(item[1] - song_bpm)))
        song_list = [key for key in sorted_data.keys()]

        return song_list

    def get_most_played_songs(self, song_id):
        '''
        Retrieves the most played songs [based on users data] after given song_id.
        Only songs that are actively played after song_id are included.
        Songs that are suggested by different part of algorithm are ignored.

        Parameters:
            song_id: (str) The unique song identifier of currently played song.

        Returns:
            list: A list of the three most played song IDs that are similar to the given song_id sorted by most frequently played.
        '''
        next_songs = []

        users_data = self.get_users_data()
        for k, v in users_data.items():
            for song, next_song in v['played_songs'].items():
                if song == song_id:
                    next_songs.append(next_song[0])

        counter = Counter(next_songs)
        most_common = counter.most_common(3)

        return [most_common[0][0], most_common[1][0], most_common[2][0]]

    def get_mfc_users_data(self, song_id, first_recomendation, second_recomendation):
        users_set_1, users_set_2 = [
            first_recomendation], [second_recomendation]
        song_1_count, song_2_count = 0, 0

        for k, v in self.users_data.read_json().items():
            if v['played_songs'][song_id][0] == first_recomendation:
                song_1_count += 1
            elif v['played_songs'][song_id][0] == second_recomendation:
                song_2_count += 1

        users_set_1.append(song_1_count)
        users_set_2.append(song_2_count)

        result = {'song_1': users_set_1, 'song_2': users_set_2}

        return result



class DataSaver:
    def __init__(self) -> None:
        # self.song_id = song_id
        # self.user_id = user_id
        # self.next_song_id = next_song_id
        self.data = JSONData(USERS_DATA)

    def __format_data(self):
        self.user_id = "user_id_" + str(self.user_id)
        self.song_id = "song_id_" + str(self.song_id)

        return None

    @staticmethod
    def format_user_id(user_id: int):
        ''' converts user id int to proper user id e.g. user_id_1'''
        return "user_id_" + str(user_id)

    @staticmethod
    def format_song_id(song_id: int):
        ''' converts song id int to proper song id e.g. song_id_1'''
        return "song_id_" + str(song_id)

    def set_new_song(self, user_id, song_id, next_song_id):

        keys = [user_id, 'played_songs', song_id]
        self.data.write_json(keys, [next_song_id])

        return 'new song saved to json file'
