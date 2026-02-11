const express = require("express");
const router = express.Router();
const Login = require("../models/loginSchema");

// SIGNUP
router.post("/signup", async (req, res) => {
  try {
    const { email, password } = req.body;

    const exists = await Login.findOne({ email });
    if (exists) return res.status(400).json({ message: "User already exists" });

    const login = new Login({ email, password });
    await login.save();

    res.json({ message: "Signup successful" });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Server error" });
  }
});

// LOGIN
// router.post("/login", async (req, res) => {
//   try {
//     const { email, password } = req.body;

//     const login = await Login.findOne({ email });
//     if (!login) return res.status(400).json({ message: "Invalid email or password" });

//     const match = await login.comparePassword(password);
//     if (!match) return res.status(400).json({ message: "Invalid email or password" });

//     res.json({ message: "Login successful" });
//   } catch (err) {
//     console.error(err);
//     res.status(500).json({ message: "Server error" });
//   }
// });
// LOGIN
router.post("/login", async (req, res) => {
  try {
    const { email, password } = req.body;

    const user = await Login.findOne({ email });
    if (!user) {
      return res.status(400).json({ message: "User not found" });
    }

    const isMatch = user.comparePassword(password);
    if (!isMatch) {
      return res.status(400).json({ message: "Invalid password" });
    }

    // 🔥 Send userId back
    res.json({ 
      message: "Login successful",
      userId: user._id 
    });

  } catch (err) {
    res.status(500).json({ message: "Server error" });
  }
});


module.exports = router;