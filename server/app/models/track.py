

class Track():

    # TODO: Static method to pull from mongo cache

    def __init__(self, track: dict):
        
        self.name = track.get("name")
        self.spotify_id = track.get("id")

        self.artists = track.get("artists")        
        self.album = {
            "name": track["album"].get("album_name"),
            "type": track["album"].get("album_type"),
            "spotify_url": track["album"]["external_urls"].get("spotify")
        }

        self.cover_art = track["album"].get("images")[0].get("url") if track["album"].get("images") else None
        self.duration_ms = track.get("duration_ms")
        self.explicit = track.get("explicit")
        self.spotify_url = track["external_urls"].get("spotify")

        # Global meta
        self.isrc = track["external_ids"].get("isrc")
        self.ean = track["external_ids"].get("ean") # This will most likely be None for tracks
        self.upc = track["external_ids"].get("upc") # This will most likely be None for tracks

        self.audio_attributes = None # RIP... thanks spotify :(

    
    def get_artists_string(self) -> str:
        """Generates a string containg all artists the track belongs to, each
        artists is seperated by a comma. Functionality is mainly for creating
        a string to display on the UI.

        :return: String containing the tracks artists seperated by comma and space.
        :rtype: str
        """

        all_artists = [artist.get("name") for artist in self.artists]
        
        artist_string = ", ".join(all_artists)
        return artist_string
    

    def get_duration_string(self) -> str:
        """Converts the tracks duration_ms into a string that 
        contains minutes and seconds. Functionality mainly inteded
        for displaying track duration in the UI.

        :return: Track duration in minutes and seconds
        :rtype: str
        """

        total_seconds = self.duration_ms / 1000
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60

        duration = f"{minutes} minutes {seconds} seconds"
        return duration
    

    def get_camelot_notation(self) -> str:
        # RIP... thanks spotify :(
        pass


    def serialize(self) -> dict:
        """Serializes the current instance into a dict in order to send to client.

        :return: The track details in a dict in order to send to client.
        :rtype: dict
        """

        track = {
            "name": self.name,
            "spotify_id": self.spotify_id,
            "spotify_url": self.spotify_url,
            "artists": self.get_artists_string(),
            "album": self.album,
            "cover_art": self.cover_art,
            "isrc": self.isrc,
            "duration": self.get_duration_string(),
            "explicit": self.explicit,
            "audio_attributes": { # RIP
                "bpm": "spotify_messed_this_up",
                "key": "spotify_messed_this_up"
            }
        }
        return track
