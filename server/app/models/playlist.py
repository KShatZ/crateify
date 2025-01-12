from datetime import datetime
from typing import Optional

from pymongo import MongoClient, UpdateOne

from ..helpers.spotify.spotify_api import SpotifyAPI
from field_names import DB
from .track import Track


class Playlist:

    SERIALIZE_IGNORE = ["_id", "href", "meta_updated_at", "owner", "primary_color", "uri", "type"]

    def __init__(self, playlist_id: str, user, snap_id: str = None):

        self.id = playlist_id
        self.snap_id = snap_id
        self.user = user

        # Empty on initialization, need to be fetched
        self.meta = None
        self.tracks = []


    def load_playlist(self):
        # TODO: Throttle deliberate snap_id mismatches from user. 

        # --- Check for Mongo Cache --- #
        try:
            # NOTE: Single Mongo Instance
            mongo = MongoClient(host=DB.MONGO_URI)
            playlist_collection = mongo[self.user.id][DB.PLAYLISTS_COLLECTION]
            cached_meta = playlist_collection.find_one({"spotify_id": self.id})
        except Exception as e:
            mongo.close()
            print(f"Playlist.load_playlist() -- User({self.user.id}) --- There was an issue checking cache for Playlist({self.id}) --- {e}")
            return False

        # If never cached, all tracks will need audio details, if cached only the new ones. NOTE: No longer possibile with Spotifys horrible behaviour...
        if cached_meta:
            # --- Load From cache --- #
            if self.snap_id is None or self.snap_id == cached_meta["snapshot_id"]:
                # --- Populate Meta --- #
                self.meta = cached_meta             
            
                # --- Pull and Populate Tracks --- # TODO: Function
                tracks_collection = mongo[self.user.id][DB.TRACKS_COLLECTION]

                filter = {"spotify_id": {"$in": [track["id"] for track in self.meta["tracks"]]}}
                projection = {
                    "_id": 0, 
                    "name": 1, 
                    "id": 1, "artists": 1, "album": 1, "duration_ms": 1, "explicit": 1, "external_urls": 1, "external_ids": 1,
                } # TODO: Class VAR and dict comprehension
                track_docs = tracks_collection.find(filter, projection)
                
                self.tracks.extend(Track(track) for track in track_docs)
                mongo.close()
                print(f"Playlist.load_playlist() -- User({self.user.id}) --- Playlist({self.id}) loaded from cache...")

                return True

        mongo.close()

        # --- Load From Spotify --- # 
        playlist_meta, playlist_tracks = self._fetch_from_spotify()
        if not playlist_meta and not playlist_tracks:
            # NOTE: Janky Way of handling invalid playlist id (and other errors)
            print(f"Playlist.load_playlist() -- User({self.user.id}) --- Unable to load Playlist({self.id}) due to issue in pulling it's data from Spotify.")
            return False
        
        updated = self._update_playlist(playlist_meta, playlist_tracks)
        if not updated:
            print(f"Playlist.load_playlist() -- User({self.user.id}) --- There was a problem updating Playlist({self.id}) data during load")
            return False

        print(f"Playlist.load_playlist() -- User({self.user.id}) --- Playlist({self.id}) loaded from Spotify pull...")
        return True


    def get_duration_string(self) -> Optional[str]:
        """Generated the total playlist duration in the format of hours minutes seconds.
        This string is mainly generated to be used in the UI to show the total
        playlist duration.

        :return: String formated in hours minutes seconds for total duration of playlist
        :rtype: Optional[str]
        """

        if self.meta is None:
            return None
        
        duration_ms = self.meta.get("duration_ms")

        h = duration_ms // 3600000
        m = (duration_ms % 3600000) // 60000
        s = (duration_ms % 60000) // 1000 # NOTE: Seconds are not rounded up like spotify does

        minute_string = str(m) + " minutes " if m != 1 else str(m) + " minute "
        second_string = str(s) + " seconds" if s != 1 else str(s) + " second"

        if h == 0:
            return minute_string + second_string
        else:
            hour_string = str(h) + " hours " if h != 1 else str(h) + " hour "
            return hour_string + minute_string + second_string

    
    def serialize(self) -> Optional[dict]:
        """Serializes the playlist data into a dict to be sent to 
        the client.

        :return: A dict containing meta and track information to be sent
        to the client
        :rtype: Optional[dict]
        """

        if not self.meta and not self.tracks:
            return None

        meta = {key:value for key, value in self.meta.items() if key not in Playlist.SERIALIZE_IGNORE}
        meta["owner"] = {
            "display_name": self.meta["owner"].get("display_name"),
            "profile_url": self.meta["owner"]["external_urls"].get("spotify"),
        }
        meta["duration_string"] = self.get_duration_string()

        tracks = [track.serialize() for track in self.tracks]

        return {
            "meta": meta,
            "tracks": tracks
        }
    
    def _fetch_from_spotify(self) -> tuple:
        """Fetches fresh playlist data from Spotify API. Data includes playlist
        meta data along with all track objects belonging to the playlist. These
        are returned as a tuple containing each part.

        :return: All data associated with the current playlist, split into playlist_meta (dict)
        and playlist_tracks (list) and returned as tuple
        :rtype: tuple
        """

        spotify_api = SpotifyAPI(self.user)
        playlist = spotify_api.get_playlist(self.id)

        if not playlist:
            return (None, None)

        playlist_tracks = playlist["tracks"].get("items", [])

        playlist_meta = playlist
        playlist_meta["total_tracks"] = playlist["tracks"].get("total")
        del playlist_meta["tracks"]
        
        return playlist_meta, playlist_tracks


    def _update_playlist(self, playlist_meta: dict, playlist_tracks: list) -> bool:
        """Given playlist data (meta and tracks) populates the mongo playlist and track collections
        for the current user as well as populates the current Playlist instance with the meta data
        and Track objects.

        :param playlist_meta: Meta data associated with the playlist, as given by Spotify API
        :type playlist_meta: dict
        :param playlist_tracks: The tracks that belong to the current playlist, as given by Spotify API
        :type playlist_tracks: list
        :return: Whether or not the updating of the playlist was succesful
        :rtype: bool
        """

        # --- Meta Population --- # function?
        meta = {}
        for key, value in playlist_meta.items():
            # TODO: Create a class level set with fields to skip

            if key == "id":
                meta["spotify_id"] = value

            elif key == "images": # TODO: Update function for cover art -- Expires after 1 day
                if value is None or len(value) == 0:
                    meta["cover_art"] = None
                else:
                    cover_art = value[0].get("url")
                    meta["cover_art"] = cover_art
            elif key == "external_urls":
                meta["spotify_url"] = value.get("spotify")
            elif key == "followers":
                meta["followers"] = value.get("total")
            else:
                meta[key] = value

        # --- Track Population --- # function?
        tracks_meta = []
        track_docs = []
        total_duration_ms = 0
        for track in playlist_tracks:
            
            tracks_meta.append({
                "id": track["track"].get("id"),
                "added_at": track.get("added_at"),
                "added_by": track.get("added_by")
            })
            
            track_doc = track.get("track")
            track_doc["spotify_id"] = track_doc.pop("id")
            track_doc["playlists"] = [self.id]
            track_docs.append(track_doc)

            total_duration_ms += track["track"].get("duration_ms")

        if meta["total_tracks"] != len(tracks_meta):
            print(f"Playlist._update_playlist() -- User({self.user.id}) Playlist({self.id}) --- Only processed {len(tracks_meta)} tracks instead of {meta['total_tracks']}")

        meta["tracks"] = tracks_meta
        meta["duration_ms"] = total_duration_ms
        meta["meta_updated_at"] = datetime.now()

    
        # --- Update Mongo Playlist Doc --- # TODO: Function
        try:
            # TODO: Single Mongo Instance
            mongo = MongoClient(host=DB.MONGO_URI) 
            update_result = mongo[self.user.id][DB.PLAYLISTS_COLLECTION].update_one({"spotify_id": self.id}, {"$set": meta}, upsert=True)
            mongo.close()
        except Exception as e:
            mongo.close()
            print(f"Playlist._update_playlist() -- User({self.user.id}) --- There was an error updating mongo doc for Playlist({self.id}) --- {e}")
            return False

        if update_result.matched_count == 0:
            upserted_id = update_result.upserted_id
            print(f"Playlist._update_playlist() -- User({self.user.id}) --- Created new mongo doc for Playlist({self.id}) with _id = {upserted_id}")
        else:
            if update_result.modified_count == 1:
                print(f"Playlist._update_playlist() -- User({self.user.id}) --- Successfully updated mongo doc for Playlist({self.id})")
            else:
                print(f"Playlist._update_playlist() -- User({self.user.id}) --- There was an issue updating mongo doc for Playlist({self.id})")
                return False
        
        self.meta = meta

        # --- Update/Populate Track Mongo Docs --- # TODO: Function
        try:
            bulk_ops = []
            for track in track_docs:

                self.tracks.append(Track(track))

                # Prepare Mongo Docs
                filter = {"spotify_id": track.get("spotify_id")}
                update = {
                    "$set": {key:value for key, value in track.items() if key != "playlists"},
                    "$addToSet": {"playlists": {"$each": track.get("playlists")}}
                }
                bulk_ops.append(UpdateOne(filter, update, upsert=True))

            mongo = MongoClient(host=DB.MONGO_URI)
            track_collection = mongo[self.user.id][DB.TRACKS_COLLECTION]
        
            update_result = track_collection.bulk_write(bulk_ops)
            print(f"Playlist._update_playlist() -- User({self.user.id}) --- Added {update_result.upserted_count} new tracks to Tracks collection.")
            print(f"Playlist._update_playlist() -- User({self.user.id}) --- Updated {update_result.modified_count} tracks in Tracks collection.")

            mongo.close()
        except Exception as e:
            mongo.close()
            print(f"Playlist._update_playlist() -- User({self.user.id}) --- There was an error updating track collection for tracks in Playlist({self.id}) --- {e}")
            return False
        
        return True
    