const urlBtn = document.getElementById("urlBtn");
const fileBtn = document.getElementById("fileBtn");
const inputArea = document.getElementById("inputArea");
const preview = document.getElementById("preview");
const previewImg = document.getElementById("previewImg");
const processBtn = document.getElementById("processBtn");
const result = document.getElementById("result");
const resultGrid = document.getElementById("resultGrid");

// ✅ FastAPI backend API base (port 8000 default for uvicorn)
const API_BASE = "http://127.0.0.1:8000";

let uploadedFile = null; // to hold File object

// Handle URL Upload
urlBtn.addEventListener("click", () => {
  inputArea.innerHTML = `
    <input type="text" id="urlInput" placeholder="Enter Image URL" />
    <button onclick="loadImageFromURL()">Upload</button>
  `;
  inputArea.classList.remove("hidden");
});

// Handle File Upload
fileBtn.addEventListener("click", () => {
  inputArea.innerHTML = `
    <input type="file" id="fileInput" accept="image/*" />
  `;
  document.getElementById("fileInput").addEventListener("change", loadImageFromFile);
  inputArea.classList.remove("hidden");
});

// Load from URL
function loadImageFromURL() {
  const url = document.getElementById("urlInput").value;
  if (url) {
    previewImg.src = url;
    preview.classList.remove("hidden");

    // Fetch image from URL and convert to File
    fetch(url)
      .then(res => res.blob())
      .then(blob => {
        uploadedFile = new File([blob], "uploaded.jpg", { type: blob.type });
      });
  }
}

// Load from File
function loadImageFromFile(event) {
  const file = event.target.files[0];
  if (file) {
    uploadedFile = file; // save to global
    const reader = new FileReader();
    reader.onload = function(e) {
      previewImg.src = e.target.result;
      preview.classList.remove("hidden");
    };
    reader.readAsDataURL(file);
  }
}

// Call FastAPI backend to get similar images
processBtn.addEventListener("click", async () => {
  if (!uploadedFile) {
    alert("Please upload an image first!");
    return;
  }

  const formData = new FormData();
  formData.append("file", uploadedFile);

  try {
    // ✅ FastAPI endpoint /compare-image/
    const res = await fetch(`${API_BASE}/compare-image/`, {
      method: "POST",
      body: formData
    });
    const data = await res.json();

    result.classList.remove("hidden");
    resultGrid.innerHTML = ""; // clear previous

    if (data.most_similar && data.most_similar.length > 0) {
      data.most_similar.forEach(obj => {
        const img = document.createElement("img");
        // 🔑 obj.path = "folder/file.jpg"
        img.src = `${API_BASE}/dataset/${obj.path}`;
        img.title = `${obj.path} (similarity: ${obj.score.toFixed(2)})`;
        resultGrid.appendChild(img);
      });
    } else {
      resultGrid.innerHTML = "<p>No similar images found.</p>";
    }
  } catch (err) {
    console.error(err);
    alert("Error connecting to backend.");
  }
});
