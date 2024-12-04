from datetime import datetime

from pymongo import MongoClient

from ..helpers.spotify.spotify_api import SpotifyAPI
from field_names import DB


class Playlist:

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
            print(f"Playlist.load_playlist() -- User({self.user.id}) --- There was an issue checking cache for Playlist({self.id}) --- {e}")
            return False

        if cached_meta:
            # Load From cache
            if self.snap_id is None or self.snap_id == cached_meta["snapshot_id"]:
                # TODO: Tracks
                self.meta = cached_meta

                return True

        
        # Load From Spotify, update mongo
        playlist_data = self._fetch_from_spotify()
        self._update_playlist(playlist_data)

        # meta_update()
        # track_update()
        
        # If never cached, all tracks will need audio details, if cached only the new ones.
        # If no mongo data, no need for the below conditionals, just pull from spotify


   
        
        return
    

    def _update_playlist(self, playlist_data: dict):

        # --- Popuplate Meta --- #
        meta = {}
        for key, value in playlist_data.items():

            # TODO: Create a class level set with fields to skip

            if key == "id":
                meta["spotify_id"] = value
            
            if key == "images": # TODO: Update function for cover art -- Expires after 1 day

                if value is None or len(value) == 0:
                    meta["cover_art"] = None
                else:
                    cover_art = value[0].get("url")
                    meta["cover_art"] = cover_art

            elif key == "tracks":
                total_tracks = value.get("total")
        
                track_ids = []
                for track in value["items"]:
                    
                    track_ids.append({
                        "spotify_id": track["track"].get("id"),
                        "added_at": track.get("added_at"),
                        "added_by": track.get("added_by"), # TODO: Clean up to only be array of id's
                    })

                    # TODO: Track Class populate into self.tracks

                meta["total_tracks"] = total_tracks
                meta["tracks"] = track_ids
                if total_tracks != len(track_ids):
                    #TODO
                    print(f"Playlist._update_playlist() -- User({self.user.id}) Playlist({self.id}) --- Only got {len(track_ids)} track_ids instead of {total_tracks}")

            else:
                meta[key] = value

        meta["meta_updated_at"] = datetime.now()

        # --- Update Mongo Doc --- #
        try:
            # TODO: Single Mongo Instance
            mongo = MongoClient(host=DB.MONGO_URI) 
            update_result = mongo[self.user.id][DB.PLAYLISTS_COLLECTION].update_one({"spotify_id": self.id}, {"$set": meta}, upsert=True)
        except Exception as e:
            print(f"Playlist._update_playlist() -- User({self.user.id}) --- There was an error updating mongo doc for Playlist({self.id}) --- {e}")

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
        #self.tracks
        return True



    def _fetch_from_spotify(self) -> dict:

        spotify_api = SpotifyAPI(self.user)
        playlist = spotify_api.get_playlist(self.id)

        return playlist

