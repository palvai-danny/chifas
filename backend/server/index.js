// // require('dotenv').config();  // ← only one, no dots or repeats

// // const mongoose = require('mongoose');

// // const uri = process.env.MONGO_URI;  // ← make sure this is mongodb+srv://... in your .env

// // // VERY IMPORTANT: Add this BEFORE the connect() call
// // // For Node v18+ (recommended)
// // const dns = require('node:dns/promises');
// // dns.setServers(['1.1.1.1', '1.0.0.1', '8.8.8.8', '8.8.4.4']);  // Cloudflare + Google

// // // Alternative (works in older Node too):
// // // const dns = require('dns');
// // // dns.setServers(['1.1.1.1', '8.8.8.8']);

// // mongoose.connect(uri)
// //   .then(() => console.log('Connected successfully to MongoDB!'))
// //   .catch(err => console.error('MongoDB connection error:', err));
// require('dotenv').config();
// const express = require("express");
// const cors = require("cors");
// const connectDB = require("./db");
// const authRoutes = require("./controllers/auth");

// const multer = require("multer");
// const { runOCR } = require("./controllers/ocrController");

// const app = express();
// const PORT = process.env.PORT || 8787;
// // const PORT = 8787;

// app.listen(PORT, () => {
//   console.log(`Node Server running at http://localhost:${PORT}`);
// });

// // const PORT = process.env.PORT || 8787;

// const dns = require('node:dns/promises');
// dns.setServers(['1.1.1.1', '1.0.0.1', '8.8.8.8', '8.8.4.4']);  // Cloudflare + Google

// // connect MongoDB
// connectDB();

// // Middleware
// app.use(cors());
// app.use(express.json());

// const upload = multer({ dest: "uploads/" });

// // Routes
// app.use("/", authRoutes);

// app.post("/ocr", upload.single("file1"), runOCR);


// app.listen(PORT, () => {
//   console.log(`Server running on http://localhost:${PORT}`);
// });

require("dotenv").config();
const express = require("express");
const cors = require("cors");
const mongoose = require("mongoose");
const multer = require("multer");

const authRoutes = require("./controllers/auth");
const { runOCR } = require("./controllers/ocrController");

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
const upload = multer({ dest: "uploads/" });

// OCR route
// app.post("/ocr", upload.single("file"), runOCR);
app.post("/ocr", upload.fields([
  { name: "aadhaar", maxCount: 1 },
  { name: "memo", maxCount: 1 }
]), runOCR);

// Start Server
app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});

