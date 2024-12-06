

class Track():

    # TODO: Static method to pull from mongo cache

    def __init__(self, track: dict):
        
        self.name = track.get("name")
        self.spotify_id = track.get("id")

        self.artists = track.get("artists")
        
        self.album_type = track["album"].get("album_type")
        self.album_name = track["album"].get("album_name")
        self.spotify_album_url = track["album"]["external_urls"].get("spotify")

        self.duration_ms = track.get("duration_ms")
        self.explicit = track.get("explicit")
        self.spotify_track_url = track["external_urls"].get("spotify")

        # Global meta
        self.isrc = track["external_ids"].get("isrc")
        self.ean = track["external_ids"].get("ean") # This will most likely be None for tracks
        self.upc = track["external_ids"].get("upc") # This will most likely be None for tracks

