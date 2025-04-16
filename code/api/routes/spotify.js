import express from "express";

export const spotifyRouter = express.Router();

let access_token = null;

spotifyRouter.get('/token', async (req, res) => {

    try {
        const resp = await fetch("https://accounts.spotify.com/api/token", {
            body: "grant_type=client_credentials&client_id=7ecd03c4d0bb4de196b65b82e135ef6a&client_secret=ebf48a41eed441618f29dff1938a5cf7",
            headers: {
              "Content-Type": "application/x-www-form-urlencoded"
            },
            method: "POST"
          })
    
        const data = await resp.json()
        access_token = data.access_token;

        res.status(200).send("success")
    } catch (e) {
        res.status(400).send("Failed")
    }
})

spotifyRouter.get('/playbackstate', async (req, res) => {
    try {
        const resp = await fetch("https://api.spotify.com/v1/me/player", {
            headers: {
                Authorization: `Bearer ${access_token}`
            },
            method: "GET"
        })
        console.log(resp)
        const data = await resp.json()
        console.log(data)
        res.status(200).send(data)
    } catch (e) {
        res.status(400).send("Failed")
    }
})