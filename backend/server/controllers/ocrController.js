//ocr controller.js
const axios = require("axios");
const FormData = require("form-data");
const fs = require("fs");
const Login = require("../models/loginSchema");

exports.runOCR = async (req, res) => {
  try {
    
    const userId = req.body.userId;
    console.log(userId);
    if (!userId) {
      return res.status(400).json({ error: "User not identified" });
    }

    const aadhaarFile = req.files["aadhaar"]?.[0];
    console.log("af: ",aadhaarFile);
    const memoFile = req.files["memo"]?.[0];
    console.log("af: ",memoFile);
    if (!aadhaarFile || !memoFile) {
      return res.status(400).json({ error: "Both files required" });
    }

    const formData = new FormData();
    formData.append("aadhaar", aadhaarFile.buffer, aadhaarFile.originalname);
    formData.append("memo", memoFile.buffer, memoFile.originalname);
    console.log(1);
    const response = await axios.post(
      "http://127.0.0.1:5000/ocr",
      formData,
      { headers: formData.getHeaders() }
    );

    const ocrData = response.data;
    console.log("od: ",ocrData);
    await Login.findByIdAndUpdate(userId, {
      student_name: ocrData.student_name,
      father_name: ocrData.father_name,
      mother_name: ocrData.mother_name,
      dob: ocrData.dob,
      gender: ocrData.gender,
      aadhaar: ocrData.aadhaar
    });
    console.log(2);
    res.json(ocrData);

  } catch (err) {
    console.log(3);
    console.log(err.message);
    res.status(500).json({ error: "OCR fuckedup!" });
  }
};