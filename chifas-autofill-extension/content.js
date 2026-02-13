// Runs on every site

(async function () {

  // Try to get userId from CHIFAS site
  let userId = null;

  try {
    userId = localStorage.getItem("chifasUserId");
  } catch (e) {}

  if (!userId) return;

  // If form exists, notify popup badge
  const inputs = document.querySelectorAll("input, textarea, select");

  if (inputs.length > 3) {
    chrome.runtime.sendMessage({ formDetected: true });
  }

})();
