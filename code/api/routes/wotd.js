import express from "express";

export const wotd_router = express.Router();

wotd_router.get('/en', async (req, res) => {
  res.status(200).send("Under construction")
})

wotd_router.get('/fr', async (req, res) => {
  res.status(200).send("Under construction")
})

wotd_router.get('/it', async (req, res) => {
  res.status(200).send("Under construction")
})

wotd_router.get('/sp', async (req, res) => {
  res.status(200).send("Under construction")
})