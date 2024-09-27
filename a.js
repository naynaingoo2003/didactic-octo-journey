const axios = require('axios');
const fs = require('fs');
const path = require('path');
const ProgressBar = require('progress');

// URL of the JSON data
const url = 'http://89.117.1.221:3000/filteredMoviesData';

// Path where the JSON file will be saved
const filePath = path.join(__dirname, 'db_movie.json');

// Make a GET request and track progress
axios({
    method: 'get',
    url: url,
    responseType: 'stream',
})
.then(response => {
    const totalLength = response.headers['content-length'];
    const progressBar = new ProgressBar('-> downloading [:bar] :percent :etas', {
        width: 40,
        complete: '=',
        incomplete: ' ',
        renderThrottle: 1,
        total: parseInt(totalLength)
    });

    response.data.on('data', (chunk) => progressBar.tick(chunk.length));

    const writer = fs.createWriteStream(filePath);
    response.data.pipe(writer);

    writer.on('finish', () => {
        console.log('File downloaded and saved as db_movie.json');
    });

    writer.on('error', (err) => {
        console.error('Error writing the file:', err);
    });
})
.catch(error => {
    console.error('Error downloading the file:', error);
});
