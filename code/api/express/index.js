import express from "express";
import sqlite3 from "sqlite3";
import { open } from "sqlite";

const app = express();
const port = 8001;

export const db = await open({
  filename: "./db.db",
  driver: sqlite3.Database,
});

app.get('/', async (req, res) => {
  try {
    const data = await db.all(`SELECT * FROM Brewers_Games;`);
    console.log(data)
    res.status(200).send(data)
} catch (e) {
    console.error(e);
    res.status(500).send({
        msg: "Failed"
    })
}
})

app.listen(port, () => {
  console.log(`My API has been opened on :${port}`);
});
