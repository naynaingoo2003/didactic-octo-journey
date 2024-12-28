const express = require('express');
const path = require('path');
const app = express();
const port = 3002;
const filename = '4.json'
// Serve static files from the current directory (root directory)
app.use(express.static(__dirname));

// Optionally, serve the specific 2.json file with the correct content type
app.get(filename, (req, res) => {
  res.setHeader('Content-Type', 'application/json; charset=utf-8'); // Set UTF-8 encoding
  res.sendFile(path.join(__dirname, filename)); // Serve the 2.json file
});

app.listen(port, () => {
  console.log(`Server is running on http://137.184.129.81:${port}`);
});
