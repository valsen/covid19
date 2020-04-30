## Description
A single-page website that displays a chart overlaying coronavirus related google search trends on top of daily new reported cases of COVID-19. A dropdown selector lets the user choose either the United States or Sweden, meaning the google trends and covid cases are local for that country. A text input field lets the user choose up to 5 comma-separated search terms for the google trends.

Data is fetched from Google Trends, covidtracking.com and covid-api.com.

## Infrastructure
- The frontend (written in Svelte) and backend (Python Flask) each have their own Dockerfile for containarization. 
- The client is a multi-stage container, that first builds the static files and then serves them with NGINX.
- A docker-compose file is used to create a container swarm in which the frontend and backend can communicate with each other
- Google Cloud Build integration with the Github repo, triggers Google to run a cloudbuild.yaml file that in turn builds the containers with docker-compose
- A terraform config file allows an easy way to spin up a Google Compute Engine instance, which the website could be deployed to (not implemented)

## To run the server locally:
- Clone this repo
- Make sure docker is installed
- From root folder, run `docker-compose up`
- Access the the website in a browser at `localhost` (default port is 80)