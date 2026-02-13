const loginSection = document.getElementById("loginSection");
const autofillSection = document.getElementById("autofillSection");
const statusDiv = document.getElementById("status");

// Check if already logged in
chrome.storage.local.get("chifasUserId", (result) => {
  if (result.chifasUserId) {
    showAutofill();
  }
});

// LOGIN
document.getElementById("loginBtn").addEventListener("click", async () => {

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const res = await fetch("http://localhost:8787/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  const data = await res.json();

  if (!res.ok) {
    statusDiv.innerText = data.message;
    return;
  }

  chrome.storage.local.set({ chifasUserId: data.userId }, () => {
    showAutofill();
  });
});


// AUTOFILL BUTTON
document.getElementById("autofillBtn").addEventListener("click", async () => {

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  chrome.storage.local.get("chifasUserId", async (result) => {

    const userId = result.chifasUserId;
    if (!userId) {
      statusDiv.innerText = "Not logged in";
      return;
    }

    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: autofillFunction,
      args: [userId]
    });

  });

});


// LOGOUT
document.getElementById("logoutBtn").addEventListener("click", () => {
  chrome.storage.local.remove("chifasUserId", () => {
    loginSection.style.display = "block";
    autofillSection.style.display = "none";
  });
});


function showAutofill() {
  loginSection.style.display = "none";
  autofillSection.style.display = "block";
  statusDiv.innerText = "Logged in";
}


// INJECTED FUNCTION
async function autofillFunction(userId) {

  const response = await fetch("http://localhost:8787/get-user-data", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ userId })
  });

  const user = await response.json();

  const inputs = document.querySelectorAll("input, textarea");

  inputs.forEach(input => {

    const name = (input.name || input.id || "").toLowerCase();

    if ((name.includes("candidate") && name.includes("name"))||name.includes("Candidate Name"))
      input.value = user.student_name;

    else if (name.includes("father"))
      input.value = user.father_name;

    else if (name.includes("mother"))
      input.value = user.mother_name;

    else if (name.includes("dob"))
      input.value = user.dob;

    else if (name.includes("email"))
      input.value = user.candidate_email || user.email;

    else if (name.includes("mobile") || name.includes("phone"))
      input.value = user.candidate_mobile;

    else if (name.includes("address"))
      input.value = user.current_address;

    else if (name.includes("state"))
      input.value = user.state;

    else if (name.includes("pin"))
      input.value = user.pincode;

  });

}
