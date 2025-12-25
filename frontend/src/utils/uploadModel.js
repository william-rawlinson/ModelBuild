// utils/uploadModel.js

export async function uploadModelFile(file) {
  if (!file) throw new Error("No file provided");

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("http://127.0.0.1:8000/upload-model/", {
    method: "POST",
    body: formData,
  });

  // Parse backend response JSON
  const data = await response.json();

  if (!response.ok) {
    // Throw error with string message
    throw new Error(data.message || "Upload failed");
  }

  // Return the string message only
  console.log("Backend response:", data);
  return data.message;
}
