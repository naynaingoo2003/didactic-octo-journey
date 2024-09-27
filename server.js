const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const port = 3000;

// Update these paths to match your PM2 app's log files
const outLogPath = path.join(process.env.HOME, '.pm2/logs/app-out.log');
const errorLogPath = path.join(process.env.HOME, '.pm2/logs/app-error.log');

app.get('/', (req, res) => {
    // Read the standard output log
    fs.readFile(outLogPath, 'utf8', (err, outData) => {
        if (err) {
            console.error('Error reading output log file:', err);
            return res.status(500).send('Error reading output log file');
        }

        // Get the last 100 lines of the output log
        const outLines = outData.trim().split('\n');
        const last100OutLines = outLines.slice(-50).join('\n');

        // Read the error log
        fs.readFile(errorLogPath, 'utf8', (err, errorData) => {
            if (err) {
                console.error('Error reading error log file:', err);
                return res.status(500).send('Error reading error log file');
            }

            // Get the last 100 lines of the error log
            const errorLines = errorData.trim().split('\n');
            const last100ErrorLines = errorLines.slice(-100).join('\n');

            // Render the logs with basic HTML and Tailwind CSS for styling
            res.send(`
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>PM2 Logs</title>
                    <script src="https://cdn.tailwindcss.com"></script>
                </head>
                <body class="bg-gray-900 text-white p-4">
                    <h1 class="text-3xl font-bold mb-4">PM2 Logs - Last 100 Lines</h1>
                    <h2 class="text-2xl font-bold mb-2">Output Log</h2>
                    <pre class="bg-gray-800 p-4 rounded-lg overflow-x-auto">${last100OutLines}</pre>
                    <h2 class="text-2xl font-bold mt-4 mb-2">Error Log</h2>
                    <pre class="bg-gray-800 p-4 rounded-lg overflow-x-auto">${last100ErrorLines}</pre>
                </body>
                </html>
            `);
        });
    });
});

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
