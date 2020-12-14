# CMU Interactive Data Science Final Project

* **Title**: Lyric Visualization
* **Track**: Interactive Visualization/Application
* **Team members**:
  * Contact person: Peter Schaldenbrand - pschalde@andrew.cmu.edu
  * Paulina Davison - pldaviso@andrew.cmu.edu

![A screenshot of the application.](app_screenshot.png)

## Abstract

Comparing text is a difficult task since it requires high level thinking and a strong grasp on a language.  Natural Language Processing (NLP) provides tools to help analyze text such as sentiment analysis and clustering of words/sentences.  Lyrics from music provide an interesting use case for NLP as music is often compared and contrasted.  These NLP tools are often used by researchers and authors to explore a hypothesis about lyrics such as word usage between genres of music and sentiment of songs, but there does not exist a tool that lets users explore their own hypotheses of lyrics by comparing them.  In this project, we introduce the first tool designed to facilitate the comparison of song lyrics.  Users can compare any two songs along three dimensions: word similarities, line similarities, and positivity.  With this application, users were able to extract shared words or similar words between the two songs, explore which lines of lyrics are very similar or dissimilar amongst the songs, and investigate how each artist uses positivity in their lyrics.

## Running Locally
- Clone the repository
- `cd fp-lyric-visualization`
- `pip3 install -r requirements.txt` To install dependencies.
- `python3 -m textblob.download_corpora` To install corpora for textblob.
- `python3 server.py [--port 8081]` to run the server out of port 8081.
- The application should now be live at http://localhost:8081

## Viewing Online
Between December 8th, 2020 and December 18th, 2020 the application is available via http://32a5b21dc47e.ngrok.io/

## Paper and Video
The paper is in [Report.MD](https://github.com/CMU-IDS-2020/fp-lyric-visualization/blob/main/Report.md) in this repository.
The video is available to the instructors on Canvas.

## Work distribution and Project Process
Peter did 55% of the work and Paulina did 45% of the work. In developing the proposal, Peter and Paulina separately brainstormed ideas. They utilized office hours to receive guidance on the idea selection, collaborated in writing the project proposal, and utilized office hours to receive feedback on the proposal write-up. In the proposal there were several data sources that were presented, and some that were recommended in the feedback on the proposal. Paulina lead the development of code to gather features from these sources for the song "Just the Two of Us" by Will Smith, which was used as an example for the Design Review Prototype. Word positivity vs. line positivity and the parts of speech of words in a line were the features that were presented in the Design Review Prototype. In later iterations, Peter added T-Distributed Stochastic Neighbor Embedding (TSNE) for words and lines. In addition, Peter and Paulina added a different view of word positivity vs. line positivity based on a joint decision to treat positivity as a discrete quantity rather than a continuous quantity from the new knowledge that the value returned was a confidence of a machine learning model. Paulina gathered synonyms and antonyms for words using the Merriam-Webster Dictionary API, but after brainstorming how to display these connections, Peter and Paulina decided to focus on other features for the final project. This decision was influenced by the fact that the synonyms and antonyms were grouped based on usage, but there was no clear way to distinguish between different usages of the same word in the lyrics.

In the first discussions of whether to develop using Streamlit, D3.JS, or another structure, Peter and Paulina decided to use D3.JS because they thought that it would provide them a desired flexibility to create some unusual or creative visualizations for their dataset. In addition, they wanted to learn the basics of what many professional data visualizations utilize. Peter lead the development of the code for the web application. He created the interactive techniques of: selecting a word (or later - line) in the song lyrics and having the corresponding point be highlighted in the scatter plot; selecting a point (on click) or points (on brush) in the scatter plot and having the corresponding words be highlighted in the song lyrics; and using the tooltip in the scatter plot to being able to learn which word was associated with the point. In addition, he developed the ability to click on a line and see the part of speech of each word, to view the positivity of the lines as a heat-map next to the lyrics, and to have a fish-eye view of the lyrics so that the current lyric being hovered over would be bigger than the ones around it. Of these techniques used in the Design Review Prototype, the scatter plot interaction was kept for the final project and the positivity heat-map was kept but changed to show discrete values (negative or positive only). For the final project, Peter added the ability to see two songs and have their data mapped to the same scatter plots as well as the functionality for different pairs of example songs and including the Spotify preview for each song. Both Peter and Paulina fixed small bugs that they saw in the application and that impacted the user experience. Paulina lead the development of the Final Project Report. Throughout the entire development process, Peter and Paulina met via zoom meetings to collaborate on the project and discuss the design of the web application.
