const express = require('express');
const path = require('path');

const app = express();
const port = 3001;

// Serve the filteredMoviesData.json file
app.get('/filteredMoviesData', (req, res) => {
    res.sendFile(path.join(__dirname, 'db_movie.json'));
});

// Start the server
app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
