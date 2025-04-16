import express from "express";
import sqlite3 from "sqlite3";
import { open } from "sqlite";

import { brewersRouter } from "./routes/brewers.js";
import { bucksRouter } from "./routes/bucks.js";
import { formulaOneRouter } from "./routes/formulaone.js";
import { spotifyRouter } from "./routes/spotify.js";
import { wotd_router } from "./routes/wotd.js";

import mlb_sched from './raw_data/mlb_sched.json' with {type: "json"};
import mlb_teams from './raw_data/mlb_teams.json' with {type: "json"};

import nba_sched from './raw_data/nba_sched.json' with {type: "json"};
import nba_teams from './raw_data/nba_teams.json' with {type: "json"};

import f1_sched from './raw_data/f1_sched.json' with {type: "json"};
import f1_teams from './raw_data/f1_teams.json' with {type: "json"};

const app = express();
const port = 8000;

export const sportsDB = await open({
  filename: "./sports.db",
  driver: sqlite3.Database,
});

app.get("/", async (req, res) => {
  res.status(200).sendFile("index.html", { root: "./html/" });
});

app.use("/brewers", brewersRouter);
app.use("/bucks", bucksRouter);
app.use("/f1", formulaOneRouter);
// app.use("/spotify", spotifyRouter);
app.use("/wotd", wotd_router);

app.listen(port, () => {
  console.log(`My API has been opened on :${port}`);
});

// let data = mlb_sched.events;
// for (let i = 0; i < data.length; i++) {
//   await sportsDB.run("INSERT INTO MLB_Schedule (Event_ID, Event, Season, Home_Team_ID, Home_Score, Away_Team_ID, Away_Score, Date, Event_Thumbnail, Venue_ID, Venue) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data[i].idEvent, data[i].strEvent, data[i].strSeason, data[i].idHomeTeam, data[i].intHomeScore, data[i].idAwayTeam, data[i].intAwayScore, new Date(data[i].strTimestamp), data[i].strThumb, data[i].idVenue, data[i].strVenue)
// }

// let data = mlb_teams.teams;
// for (let i = 0; i < data.length; i++) {
//   await sportsDB.run("INSERT INTO MLB_Teams (Team_ID, Team, Team_Short, Badge, Logo, Banner) VALUES (?, ?, ?, ?, ?, ?)", data[i].idTeam, data[i].strTeam, data[i].strTeamShort, data[i].strBadge, data[i].strLogo, data[i].strBanner);
// }

// data = nba_sched.events;
// for (let i = 0; i < data.length; i++) {
//   await sportsDB.run("INSERT INTO NBA_Schedule (Event_ID, Event, Season, Home_Team_ID, Home_Score, Away_Team_ID, Away_Score, Date, Event_Thumbnail, Venue_ID, Venue) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data[i].idEvent, data[i].strEvent, data[i].strSeason, data[i].idHomeTeam, data[i].intHomeScore, data[i].idAwayTeam, data[i].intAwayScore, new Date(data[i].strTimestamp), data[i].strThumb, data[i].idVenue, data[i].strVenue)
// }

// data = nba_teams.teams;
// for (let i = 0; i < data.length; i++) {
//   await sportsDB.run("INSERT INTO NBA_Teams (Team_ID, Team, Team_Short, Badge, Logo, Banner) VALUES (?, ?, ?, ?, ?, ?)", data[i].idTeam, data[i].strTeam, data[i].strTeamShort, data[i].strBadge, data[i].strLogo, data[i].strBanner);
// }

// let data = f1_sched.events;
// for (let i = 0; i < data.length; i++) {
//   await sportsDB.run("INSERT INTO Formula1_Schedule (Event_ID, Event, Season, Date, Event_Thumbnail, Venue_ID, Venue) VALUES (?, ?, ?, ?, ?, ?, ?)", data[i].idEvent, data[i].strEvent, data[i].strSeason, new Date(data[i].strTimestamp), data[i].strThumb, data[i].idVenue, data[i].strVenue)
// }

// let data = f1_teams.teams;
// for (let i = 0; i < data.length; i++) {
//   await sportsDB.run("INSERT INTO Formula1_Teams (Team_ID, Team, Team_Short, Badge, Logo, Banner) VALUES (?, ?, ?, ?, ?, ?)", data[i].idTeam, data[i].strTeam, data[i].strTeamAlternate, data[i].strBadge, data[i].strLogo, data[i].strBanner);
// }