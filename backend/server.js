const express = require('express');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

const dbPath = path.resolve(__dirname, '../data/crm.db');
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('Error connecting to database:', err.message);
    } else {
        console.log('Connected to SQLite DB at', dbPath);
        // Ensure table exists just in case
        db.run(`CREATE TABLE IF NOT EXISTS leads (
            username   TEXT PRIMARY KEY,
            data       TEXT NOT NULL,
            closer     TEXT NOT NULL DEFAULT '',
            score      INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )`);
    }
});

// GET all leads
app.get('/api/leads', (req, res) => {
    db.all('SELECT data, closer FROM leads ORDER BY score DESC', [], (err, rows) => {
        if (err) {
            console.error('Error fetching leads:', err.message);
            return res.status(500).json({ error: err.message });
        }
        
        const leads = rows.map(row => {
            let parsedData = {};
            try {
                // Python json.dumps might output NaN which JS JSON.parse throws on
                const safeData = row.data.replace(/:\s*NaN/g, ': null').replace(/:\s*Infinity/g, ': null');
                parsedData = JSON.parse(safeData);
            } catch (e) {
                console.error('Error parsing lead data:', e.message);
            }
            parsedData.closer = row.closer;
            return parsedData;
        });

        res.json(leads);
    });
});

// UPDATE closer
app.put('/api/leads/:username/closer', (req, res) => {
    const username = req.params.username;
    const { closer } = req.body;
    
    if (typeof closer === 'undefined') {
        return res.status(400).json({ error: 'closer is required' });
    }

    db.run(
        "UPDATE leads SET closer = ?, updated_at = datetime('now') WHERE username = ?",
        [closer, username],
        function(err) {
            if (err) {
                return res.status(500).json({ error: err.message });
            }
            
            // Need to update the data json string as well to keep closer synced inside
            db.get("SELECT data FROM leads WHERE username = ?", [username], (err, row) => {
                if (!err && row && row.data) {
                    try {
                        let parsedData = JSON.parse(row.data);
                        parsedData.closer = closer;
                        db.run(
                            "UPDATE leads SET data = ? WHERE username = ?",
                            [JSON.stringify(parsedData), username]
                        );
                    } catch (e) {}
                }
            });

            res.json({ success: true, updated: this.changes });
        }
    );
});

const PORT = 3001;
app.listen(PORT, () => {
    console.log(`Backend API running on http://localhost:${PORT}`);
});
