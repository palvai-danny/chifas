// const mongoose = require("mongoose");

// const loginSchema = new mongoose.Schema(
//   {
   
//     email: {
//       type: String,
//       required: true,
//       unique: true,
//     },
//     password: {
//         type: String,
//         required: true,
//     },
//   },
//   { timestamps: true }
// );
// loginSchema.methods.comparePassword = function(password) {
//   return this.password === password;
// };
// module.exports = mongoose.model("Login", loginSchema);
const mongoose = require("mongoose");

const loginSchema = new mongoose.Schema(
  {
    email: {
      type: String,
      required: true,
      unique: true,
    },

    password: {
      type: String,
      required: true,
    },

    // 🔹 OCR Extracted Details
    student_name: { type: String, default: "" },
    father_name: { type: String, default: "" },
    mother_name: { type: String, default: "" },
    dob: { type: String, default: "" },
    gender: { type: String, default: "" },
    aadhaar: { type: String, default: "" },

    // 🔹 Manual Details
    candidate_email: { type: String, default: "" },
    parent_email: { type: String, default: "" },
    candidate_mobile: { type: String, default: "" },
    father_mobile: { type: String, default: "" },
    mother_mobile: { type: String, default: "" },

    category: { type: String, default: "" },
    country: { type: String, default: "" },

    current_address: { type: String, default: "" },
    district: { type: String, default: "" },
    state: { type: String, default: "" },
    pincode: { type: String, default: "" }

  },
  { timestamps: true }
);

// Simple password compare (no hashing version)
loginSchema.methods.comparePassword = function(password) {
  return this.password === password;
};

module.exports = mongoose.model("Login", loginSchema);
