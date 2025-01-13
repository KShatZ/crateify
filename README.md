<div align="center">
    <h1>Crateify</h1>
</div>

<div align="center">
    <img src="docs/crateify-logo.png" alt="Temporary Crateify Logo">
</div>


## Project Description:
Crateify is a web application designed to facilitate and enhance Spotify playlist creation for DJs, curators, and music aficionados. The idea behind Crateify was to create "a Rekordbox or Serato for Spotify," mimicking the DJ software experience by displaying track audio features such as BPM and key. Additionally, Crateify leverages the Spotify API to include more interesting metadata, such as genre and artist details.

Future plans included integrating the Spotify recommendation engine along with large language models (LLMs) like ChatGPT or Claude to assist with generating playlists.

>Unfortunately, development of the Crateify MVP has been paused due to Spotify deprecating a significant portion of its API endpoints related to track audio features. These endpoints were a critical driver for the application's functionality, and their removal has rendered much of the intended features unattainable. As a result, some features are currently hard-coded for demonstration purposes. <br><br>This deprecation significantly impacted the developer community, affecting numerous applications reliant on the Spotify API. I am actively researching alternative music data sources and music analysis software/APIs to resume development. However, Spotify's API was the most extensive and accessible source of music data available, while many alternative solutions involve high operational costs. I remain optimistic about finding a suitable replacement to continue this project.

## Tech Used:

### Client Side:
The UI and client-side functionality of this application were built using <ins>React.js and React Router</ins>, successfully implementing the single-page application (SPA) experience.

### Server Side:
The backend logic and API were developed using <ins>Python</ins> and its <ins>Flask</ins> library, with extensive utilization of <ins>Spotify's API</ins>.

### Database:
Data persistence and caching strategies currently utilize <ins>MongoDB</ins>. Future plans include integrating <ins>Redis</ins> to enhance caching, further improving user experience and mitigating Spotify API rate limits.


## Application Screenshots
![Crateify Screenshots](docs/screenshots.png)
