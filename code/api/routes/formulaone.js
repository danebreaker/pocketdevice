import express from "express";
import { sportsDB } from "../index.js";

export const formulaOneRouter = express.Router();

formulaOneRouter.get('/', async (req, res) => {
    try {
        const data = await sportsDB.all(`SELECT Event_ID, Event, Date, Venue FROM Formula1_Schedule WHERE Date >= ? ORDER BY Date LIMIT 5;`, new Date() - 12 * 60 * 60 * 1000);
        res.status(200).send(data)
    } catch (e) {
        console.error(e);
        res.status(500).send({
            msg: "Failed"
        })
    }
})

formulaOneRouter.get('/gp', async (req, res) => {
    try {
        const data = await sportsDB.all(`SELECT Event_ID, Event, Date, Venue
                                            FROM Formula1_Schedule
                                            WHERE Event LIKE '%Grand Prix%'
                                                AND Event NOT LIKE '%Free Practice 1%'
                                                AND Event NOT LIKE '%Free Practice 2%'
                                                AND Event NOT LIKE '%Free Practice 3%'
                                                AND Event NOT LIKE '%Qualifying%'
                                                AND Event NOT LIKE '%Sprint%'
                                                AND Event NOT LIKE '%Sprint Qualifying%'
                                                AND Date >= ?
                                            ORDER BY Date
                                            LIMIT 5;`, new Date());
        res.status(200).send(data)
    } catch (e) {
        console.error(e);
        res.status(500).send({
            msg: "Failed"
        })
    }
})