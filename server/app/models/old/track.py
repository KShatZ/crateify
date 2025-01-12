from field_names import CAMELOT

class Track():

    def __init__(self, track):

        # -- Track Meta -- #
        meta = track.get("track")
        album = meta.get("album")

        self.id = meta.get("id")
        self.name = meta.get("name")
        self.artists = meta.get("artists")
        self.explicit = meta.get("explicit")
        self.duration_ms = meta.get("duration_ms")
        self.spotify_url = meta["external_urls"].get("spotify")
        self.cover_art = album.get("images")[0] if album.get("images") else None
        self.album_id = album.get("id")
        self.album_type = album.get("album_type")
        self.album_name = album.get("name")
        self.album_href = album.get("href")

        # -- Track Audio Features -- #
        audio_features = track["audio_features"]
        self.bpm = audio_features.get("tempo")
        self.key = str(audio_features.get("key", -1))
        self.mode = audio_features.get("mode")

        # -- Tracks' Playlist -- #
        self.playlist_id = track.get("playlist_id")
        self.added_at = track.get("added_at") # TODO: Prob need different format


    @property
    def camelot(self):
        """Returns the camelot notation key for the track (used by DJ's), based
        off the Spotify API provided values for the tracks
        pitch class (key) and modality (mode).

        :return: The camelot notation key for the track
        :rtype: string
        """

        # Key or Mode not identified
        if self.key == -1 or self.mode is None:
            print("HJere")
            return None

        pitch_class = CAMELOT.PITCH_CLASS.get(self.key)

        return CAMELOT.MAJOR.get(pitch_class) if self.mode == 1 \
            else CAMELOT.MINOR.get(pitch_class)
    

    @property
    def artist_string(self) -> str:
        """Formats a string containing all the artists that 
        the track belongs too. This is used for displaying the
        tracks artists in the UI.

        :return: A formatted string containing the artists of the track
        seperated by commas if there are multiple.
        :rtype: str
        """

        artists = [artist.get("name") for artist in self.artists]
        return ", ".join(artists)
    

    @property
    def duration_string(self) -> str:
        """Converts the tracks duration_ms into minutes and seconds
        formating it into a string to be used in the UI.

        :return: The duration of the track in minutes and seconds.
        :rtype: str
        """

        total_seconds = self.duration_ms / 1000
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60

        return f"{minutes} minutes {seconds} seconds"


    def serialize(self) -> dict:

        track = {
            "id": self.id,
            "name": self.name,
            "artists": self.artist_string,
            "cover_art": self.cover_art.get("url") if self.cover_art else "",
            "duration": self.duration_string,
            "explicit": self.explicit,
            "bpm": self.bpm,
            "key": self.camelot,
            "spotify_url": self.spotify_url,
            "playlist_id": self.playlist_id,
            "added_at": self.added_at,
        }

        return track
