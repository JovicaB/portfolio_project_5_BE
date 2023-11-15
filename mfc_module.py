import random

from abc import ABC, abstractmethod
from data.data_manager import DataExtractor, DataSaver


class RecomendationModule(ABC):
    """
    Abstract Base Class for Recommendation Modules.
    """
    @abstractmethod
    def get_next_song(self, song_id):
        raise NotImplementedError("Must be implemented in child class")


class MFC(RecomendationModule):
    """Most Frequent Choice
    first three songs that most users played after the current song, randomized by default at 50/30/20
    New songs are recorded in the dataset only if the user selects a new song after completing the current song.
    """

    def __init__(self) -> None:
        self.data = DataExtractor()
        super().__init__()

    def get_next_songs(self, song_id):
        """
        Retrieves the first three songs that most users played after the current song.
        
        Parameters:
        - song_id (str): ID of the current song.
        
        Returns:
        - List[str]: List of song IDs.
        """
        songs = self.data.get_most_played_songs(song_id)
        return songs
    
    def get_next_song(self, song_id):
        """
        Implements the abstract method from the base class, returning the next suggested song using the MFC strategy.
        
        Parameters:
        - song_id (str): ID of the current song.
        
        Returns:
        - str: ID of the next suggested song.
        """
        songs = self.get_next_songs(song_id)
        songs = self.data.get_most_played_songs(song_id)
        songs_len = len(songs)
        if songs_len > 2:
            songs = songs[:songs_len]

        probabilities = self.data.get_songs_probabilities_data(songs_len)
        result = random.choices(songs, probabilities)[0]
        return result


class BPM:
    """
    Beats Per Minute (BPM) Recommendation Module.
    """
    def __init__(self) -> None:
        self.data = DataExtractor()
        super().__init__()

    def get_next_song(self, song_id):
        """
        Returns a song with similar BPM to the current song.
        
        Parameters:
        - song_id (str): ID of the current song.
        
        Returns:
        - str: ID of the next suggested song.
        """
        songs = self.data.get_similar_bpm_songs(song_id)
        songs_len = len(songs)
        if songs_len > 2:
            songs[:songs_len]

        probabilities = self.data.get_songs_probabilities_data(songs_len)
        result = random.choices(songs, probabilities)[0]
        result = result.split("_")[-1]
        return result
    

class UAS:
    """
    User Activity Simulator (UAS) for simulating user behavior.
    """
    def __init__(self, song_id) -> None:
        self.song_id = song_id
        self.active_users = set() 
        self.saver = DataSaver()
        self.mfc = MFC()

    def generate_active_users(self):
        """
        Generates a random number of active users and returns them as a list.
        
        Returns:
        - List[int]: List of active user IDs.
        """
        count = random.choice(range(10, 25)) 
        self.active_users = set() 
        while len(self.active_users) < count:
            self.active_users.add(random.randint(1, 50))
        return list(self.active_users)
    
    def generate_inactive_users(self):
        """
        Generates a list of inactive users based on the active users.
        
        Returns:
        - List[int]: List of inactive user IDs.
        """
        active_users = self.generate_active_users()
        result = [inactive_user for inactive_user in range(1, 511) if inactive_user not in active_users]
        return result

    def active_users_behaviour(self):
        """
        Simulates the behavior of active users by obtaining MFC recommendations for the given song.
        
        Returns:
        - int: Number of active users.
        """
        active_users = self.generate_active_users()

        for user in active_users:
            user_id = self.saver.format_user_id(user)
            next_song = self.mfc.get_next_song(self.song_id)
            self.saver.set_new_song(user_id, self.song_id, next_song)

            return len(active_users)


class MFCInterfaceBase(ABC):
    """
    Abstract Base Class for the MFC Interface.
    """

    @abstractmethod
    def current_song():
        raise NotImplementedError("Must be implemented in child class")
    
    @abstractmethod
    def original_recommendation():
        raise NotImplementedError("Must be implemented in child class")
    
    @abstractmethod
    def mfc_recommendation():
        raise NotImplementedError("Must be implemented in child class")
    
    @abstractmethod
    def stats():
        raise NotImplementedError("Must be implemented in child class")


class MFCInterface(MFCInterfaceBase):
    """
    Implementation of the MFC Interface.
    """
    def __init__(self, song_id) -> None:
        self.song_id = song_id
        self.mfc = MFC()
        self.uas = UAS(self.song_id)
        self.data = DataExtractor()
        super().__init__()

    def current_song(self):
        """
        Implements the method from the base class, returning the current song's ID.
        
        Returns:
        - str: ID of the current song.
        """
        song = self.song_id
        result = song.replace('song_id_', '')
        return result
  
    def mfc_recommendation(self):
        """
        Implements the method from the base class, returning the MFC-based song recommendation.
        
        Returns:
        - str: ID of the MFC-based recommended song.
        """
        return self.mfc.get_next_song(self.song_id)

    def original_recommendation(self):
        """
        Implements the method from the base class, returning the original song recommendation.
        
        Returns:
        - str: ID of the original recommended song.
        """
        data = self.data.get_inner_data("songs", "user_id_1")

        for k, v in data.items():
            if k =="user_id_1":
                result = v['played_songs'][self.song_id]

        return result[0]
    
    def stats(self):
        """
        Implements the method from the base class, returning statistics related to the recommendations.
        
        Returns:
        - dict: Statistics related to the recommendations.
        - 'user_count' (int): Total number of users (constant value of 50 for demonstration purposes).
        - 'active_users_count' (int): Number of active users simulated by the User Activity Simulator.
        - 'original_song' (str): ID of the current song.
        - 'default_song' (str): ID of the original recommended song.
        - 'mfc_song' (str): ID of the MFC-based recommended song.
        - 'users_count_and_choosen_songs' (List[dict]): List containing dictionaries with information about each user.
            - 'user_id' (int): ID of the user.
            - 'original_song' (str): Original recommended song for the user.
            - 'mfc_song' (str): MFC-based recommended song for the user.
        """
        current_song =  self.song_id
        recomended_songs = self.mfc.get_next_songs(current_song)
        active_users_data = self.data.get_mfc_users_data(current_song, recomended_songs[0], recomended_songs[1])

        stats = {
            'user_count': 50,
            'active_users_count': self.uas.active_users_behaviour(),
            'original_song': current_song,
            'default_song': self.original_recommendation(),
            'mfc_song': self.mfc_recommendation(),
            'users_count_and_choosen_songs': active_users_data
        }

        return stats
