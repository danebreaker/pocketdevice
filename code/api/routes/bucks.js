import express from "express";
import { sportsDB } from "../index.js";

export const bucksRouter = express.Router();

bucksRouter.get('/', async (req, res) => {
    try {
        const data = await sportsDB.all(`SELECT s.Event_ID, s.Date/1000 as Date, a.Team as Home_Team, b.Team as Away_Team, s.Home_Score, s.Away_Score
                                      FROM NBA_Schedule as s
                                      JOIN NBA_Teams as a ON a.Team_ID == s.Home_Team_ID
                                      JOIN NBA_Teams as b ON b.Team_ID == s.Away_Team_ID
                                      WHERE ((s.Home_Team_ID == 134874 OR s.Away_Team_ID == 134874) AND Date >= ?) ORDER BY Date LIMIT 5;`, 
                                      new Date() - 12 * 60 * 60 * 1000);
        res.status(200).send(data)
    } catch (e) {
        console.error(e);
        res.status(500).send({
            msg: "Failed"
        })
    }
})