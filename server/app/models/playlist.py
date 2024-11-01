from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from pymongo import MongoClient, InsertOne, DeleteOne, UpdateOne

from field_names import DB, SPOTIFY
from . import Track
from ..helpers.spotify_api import SpotifyAPI


class Playlist():

    mongo = MongoClient(DB.MONGO_URI)

    def __init__(self, playlist_id, user_id, snap_id=None):

        self.playlist_collection = self.mongo[user_id][playlist_id]

        self.id = playlist_id
        self.snap_id = snap_id
        self.user_id = user_id

        self.meta = self.playlist_collection.find_one({"_id": "meta"})
        self.track_ids = self.meta.get("track_ids", []) if self.meta else []
 
        if self.meta:
            # No change since last pull, get tracks from mongo
            if self.snap_id == self.meta.get("snap_id"):
                self.tracks = self.pull_tracks_from_mongo()
                return
            
            # -- Log -- #
            print(f"Playlist() -- User: {self.user_id} -- Pulling Playlist: {playlist_id} from Spotify... snaps don't match")

        meta, track_ids, new_tracks = self.pull_from_spotify()
        self.meta = meta
        self.track_ids = track_ids["track_ids"]
        
        self.modify_playlist_collection(meta, track_ids, new_tracks)
        self.tracks = self.pull_tracks_from_mongo()


    @property
    def duration(self) -> str:
        """Calculates playlists' total duration and formats it in a
        string in the format hours minutes seconds. This string is to
        be used in the UI to show the duration.

        :return: The total playlist duration in hours minutes and seconds
        :rtype: str
        """

        if not self.tracks:
            return None
        
        total_ms = 0
        for track in self.tracks:
            total_ms += track.duration_ms

        # Total Hour(s), Minute(s), Second(s)
        h = total_ms // 3600000
        m = (total_ms % 3600000) // 60000
        s = (total_ms % 60000) // 1000 # NOTE: I do not round seconds up like spotify does

        # Format Duration String
        m = str(m) + " minutes " if m != 1 else str(m) + " minute "
        s = str(s) + " seconds" if s != 1 else str(s) + " second"
    
        if h == 0:
            return m + s
        
        h = str(h) + " hours " if h != 1 else str(h) + " hour "
        return h + m + s


    # Pull from Spotify, populates mongo collection with new tracks
    def pull_from_spotify(self):

        endpoint = f"/playlists/{self.id}"
        params = {
            "fields": "collaborative,description,followers,href,id,images,name,public,snapshot_id,tracks"
        }

        request = SpotifyAPI(self.user_id, endpoint=endpoint, params=params)

        # TODO: Handle api request error
        if not request.send():
            pass

        new_tracks, track_ids = self.__pull_tracks(request.response_data.get("tracks"))
        meta = self.__create_meta(request.response_data, track_ids)

        return (meta, track_ids, new_tracks)


    def pull_tracks_from_mongo(self):

        track_docs = self.playlist_collection.find({"_id": {"$ne": "meta"}}, {"_id": 0})

        tracks = []
        for track in track_docs:
            tracks.append(Track(track))

        return tracks


    def modify_playlist_collection(self, meta, track_ids, new_tracks):
        
        writes = []
        
        # Tracks to Delete
        for id in track_ids["delete"]:
            writes.append(DeleteOne({"track.id": id}))
        
        # Update/Upsert Meta
        writes.append(UpdateOne({"_id": "meta"}, {"$set": meta}, upsert=True))

        # Tracks to Insert
        for track in new_tracks:
            writes.append(InsertOne(track))
        
        if writes:
            try:
                bulk_write = self.playlist_collection.bulk_write(writes)
                
                results = [bulk_write.modified_count, bulk_write.deleted_count, bulk_write.inserted_count, bulk_write.upserted_count]
                if sum(results) != (len(writes)):
                    #TODO: Handle
                    print(f"__update_playlist_col() -- User: {self.user_id} - There was an issue updating all track docs in Playlist: {self.id}")

                # -- Log -- #
                print(f"__update_playlist_col() -- User: {self.user_id} - Playlist {self.id} Collection Updated - Docs Modified: {results[0]}, Deleted: {results[1]}, Inserted: {results[2]}, Upserted: {results[3]}")
            
            except Exception as BulkWriteError:
                #TODO: Handle
                # -- Log -- #
                print(f"__update_playlist_col() -- User: {self.user_id} -  BulkWriteError: {BulkWriteError}")


    def __create_meta(self, data, track_ids):
        """Creates meta doc for the playlist using the data returned from
        the playlist endpoint: /playlist/{playlistID}

        :param data: The data received from Spotify's get playlist endpoint
        :type data: dict
        :return: A meta doc for this playlist
        :rtype: dict
        """

        images = data.get("images")
        if not images:
            image = None
        else:
            image = images[0].get("url")

        return {
            "_id": "meta",
            "meta_created_at": datetime.now(),
            "spotify_id": data.get("id"),
            "name": data.get("name"),
            "snap_id": data.get("snapshot_id"),
            "cover_art": image,
            "description": data.get("descrption"),
            "collaborative": data.get("collaborative"),
            "href": data.get("href"),
            "public": data.get("public"),
            "total_tracks": data["tracks"].get("total"),
            "track_ids": track_ids["track_ids"]
        }


    def __pull_tracks(self, initial_tracks):
        """Get's all of the playlists track ids, creates a track doc with meta and audio feature data
        for new tracks. This is used when pulling playlist data from spotify, therefore takes the 
        initial set of tracks returned by the get playlist endpoint.

        :param initial_tracks: The initial tracks that come with the data for the
        Spotify get playlist endpoint.
        :type initial_tracks: list of dicts
        :return: The track documents that contain both the meta and audio feature data
        :rtype: list of dicts
        """

        new_tracks = []
        ids = {
            "new": [],
            "duplicate": []
        }

        pulled_tracks = initial_tracks.get("items")
        self.__extract_tracks(pulled_tracks, new_tracks, ids)

        next = initial_tracks.get("next")
        next_page = self.__clean_first_tracks_next(url=next)
        while next_page:
            
            request = SpotifyAPI(self.user_id, url=next_page)

            # TODO: Handle API Request Error
            if not request.send():
                pass
            
            pulled_tracks = request.response_data.get("items")
            self.__extract_tracks(pulled_tracks, new_tracks, ids)
            
            next_page = request.response_data.get("next")

        ids["track_ids"] = ids["new"] + ids["duplicate"]
        ids["delete"] = set(self.track_ids) - set(ids["track_ids"]) 

        return (new_tracks, ids)


    def __extract_tracks(self, pulled_tracks, all_pulled_tracks, ids):

        new_tracks = []

        # Create Track documents 
        for track in pulled_tracks:
            
            # TODO: Handle error in key access
            track_id = track["track"].get("id")
            
            # Already have the track in mongo collection
            if track_id in self.track_ids:
                ids["duplicate"].append(track_id)
                continue
            
            ids["new"].append(track_id)
                
            new_tracks.append({
                "playlist_id": self.id,
                "added_at": track.get("added_at"),
                "added_by": track.get("added_by"),
                "track": track.get("track"),
            })

        # Get Audio Features For New Tracks - Spotify API
        if new_tracks:

            start = len(all_pulled_tracks)

            audio_features = self.__get_audio_features(ids["new"][start:])
            print(f"pulled features for {len(audio_features)} tracks")

            print("New Tracks: ", len(new_tracks))
            print("Audio Features: ", len(audio_features))

            # Update Track Docs With Audio Feature Data
            for i, features in enumerate(audio_features):
                try:
                    features_track_id = features.get("id")
                except Exception as e:
                    print("The feature in question:", features)
                    print("The error:", e)

                current_track = new_tracks[i]
                current_track_id = current_track["track"].get("id")

                # TODO: Better Handling Possibily - If this ever even happens??
                if features_track_id != current_track_id:
                    # -- Log -- #
                    print(f"__extract_tracks -- Playlist: {self.id} - User: {self.user_id} - Audio features returned do not match the order that was sent. feature_id: {features_track_id} at index: {i} does not match index_id: {current_track_id}")
                    current_track["audio_features"] = {}
                    continue

                current_track["audio_features"] = features

            # Append the new track docs
            all_pulled_tracks.extend(new_tracks)


    def __get_audio_features(self, track_ids):
        """Helper function to get the audio features of tracks (no more than 100)
        from Spotify API.

        :param track_ids: A list of Spotify track ids to get audio features
        for. Maximum of 100 tracks.
        :type track_ids: list of strings
        :return: The audio features for each track pulled from Spotify API
        :rtype: list of dicts
        """

        endpoint = "/audio-features"
        params = {
            "ids": ",".join(track_ids)
        }

        request = SpotifyAPI(self.user_id, endpoint=endpoint, params=params)
        # TODO: Handle Request Error
        if not request.send():
            pass

        return request.response_data.get("audio_features")
    

    def __clean_first_tracks_next(self, url):
        """Helper function to clean up the first next value obtained
        from the request to the /playlist/{playlistID} Spotify API endpoint.
        
        Ensures that the API url has the track limit set to the max track
        limit and removes the fields parameter if it exits. 

        :param url: The first next value obtained when requesting playlist
        from Spotify API
        :type url: string
        :return: Modified URL to be used in the next request to obtain all
        of the playlists tracks
        :rtype: string
        """

        if not url:
            return None

        parsed_url = urlparse(url)
        
        params = parse_qs(parsed_url.query)
        params.pop("fields", None) # Default None to prevent KeyError
        params["limit"] = SPOTIFY.PARAM_TRACK_LIMIT

        return urlunparse(parsed_url._replace(query=urlencode(params, doseq=True)))
    