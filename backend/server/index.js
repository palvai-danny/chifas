//index.js
require("dotenv").config();
const express = require("express");
const cors = require("cors");
const mongoose = require("mongoose");
const multer = require("multer");

const authRoutes = require("./controllers/auth");
const { runOCR } = require("./controllers/ocrController");
const Login = require("./models/loginSchema");

const app = express();
const PORT = 8787;

const dns = require('node:dns/promises');
dns.setServers(['1.1.1.1', '1.0.0.1', '8.8.8.8', '8.8.4.4']);  // Cloudflare + Google

// MongoDB Connection
mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log("MongoDB Connected"))
  .catch(err => console.log(err));

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.use("/", authRoutes);

// File Upload
// const upload = multer({ dest: "uploads/" });
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// OCR route
// app.post("/ocr", upload.single("file"), runOCR) ;
app.post("/ocr", upload.fields([
  { name: "aadhaar", maxCount: 1 },
  { name: "memo", maxCount: 1 }
]), runOCR);

//  SAVE DETAILS ROUTE
app.post("/save-details", async (req, res) => {
  try {
    const { userId, ...data } = req.body;

    if (!userId) {
      return res.status(400).json({ message: "User not found" });
    }

    await Login.findByIdAndUpdate(userId, data);

    res.json({ message: "Details saved successfully" });

  } catch (err) {
    console.log(err);
    res.status(500).json({ message: "Error saving details" });
  }
});
app.post("/get-user-data", async (req, res) => {
  try {
    const { userId } = req.body;

    if (!userId) {
      return res.status(400).json({ message: "User not found" });
    }

    const user = await Login.findById(userId).lean();

    if (!user) {
      return res.status(404).json({ message: "User not found" });
    }

    res.json(user);

  } catch (err) {
    console.log(err);
    res.status(500).json({ message: "Error fetching user data" });
  }
});

// Start Server
app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});