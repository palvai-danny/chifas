const express = require("express");
const router = express.Router();
const Login = require("../models/loginSchema");

// SIGNUP
const bcrypt = require("bcryptjs");

router.post("/signup", async (req, res) => {
  try {
    const { email, password } = req.body;

    //  1. Check if fields exist
    if (!email || !password) {
      return res.status(400).json({ message: "All fields are required" });
    }

    //  2. Email format validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return res.status(400).json({ message: "Invalid email format" });
    }

    //  3. Password strength validation
    if (password.length < 8) {
      return res.status(400).json({ message: "Password must be at least 8 characters" });
    }

    //  4. Check duplicate user
    const exists = await Login.findOne({ email });
    if (exists) {
      return res.status(400).json({ message: "User already exists" });
    }

    //  5. Hash password (VERY IMPORTANT)
    const hashedPassword = await bcrypt.hash(password, 10);

    const login = new Login({
      email,
      password: hashedPassword
    });

    await login.save();

    res.json({ message: "Signup successful" });

  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Server error" });
  }
});

// LOGIN
router.post("/login", async (req, res) => {
  try {
    const { email, password } = req.body;

    const user = await Login.findOne({ email });
    if (!user) {
      return res.status(400).json({ message: "Invalid Email " });
    }

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(400).json({ message: "Invalid Password" });
    }

    res.json({ message: "Login successful", userId: user._id });

  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Server error" });
  }
});


module.exports = router;