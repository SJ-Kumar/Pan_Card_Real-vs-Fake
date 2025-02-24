import React, { useEffect, useRef, useState } from "react"; import cv from "opencv.js";

const IDCardCapture = () => { const videoRef = useRef(null); const canvasRef = useRef(null); const [capturedImage, setCapturedImage] = useState(null); const [boundingBox, setBoundingBox] = useState(null); const [steadyCount, setSteadyCount] = useState(0);

useEffect(() => { const video = videoRef.current; if (!video) return;

navigator.mediaDevices
  .getUserMedia({ video: true })
  .then((stream) => {
    video.srcObject = stream;
    video.play();
  });

}, []);

const detectIDCard = () => { if (!videoRef.current || !canvasRef.current) return;

const video = videoRef.current;
const canvas = canvasRef.current;
const ctx = canvas.getContext("2d");
canvas.width = video.videoWidth;
canvas.height = video.videoHeight;
ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

let src = cv.imread(canvas);
let gray = new cv.Mat();
let edges = new cv.Mat();
cv.cvtColor(src, gray, cv.COLOR_RGBA2GRAY, 0);
cv.Canny(gray, edges, 50, 150);

let contours = new cv.MatVector();
let hierarchy = new cv.Mat();
cv.findContours(edges, contours, hierarchy, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE);

let maxArea = 0;
let bestRect = null;

for (let i = 0; i < contours.size(); i++) {
  let rect = cv.boundingRect(contours.get(i));
  let area = rect.width * rect.height;
  if (area > maxArea) {
    maxArea = area;
    bestRect = rect;
  }
}

if (bestRect) {
  const { x, y, width, height } = bestRect;
  setBoundingBox({ x, y, width, height });

  if (steadyCount >= 60) {
    captureIDCard(x, y, width, height);
  } else {
    setSteadyCount((prev) => prev + 1);
  }
} else {
  setSteadyCount(0);
}

src.delete();
gray.delete();
edges.delete();
contours.delete();
hierarchy.delete();

requestAnimationFrame(detectIDCard);

};

useEffect(() => { requestAnimationFrame(detectIDCard); }, []);

const captureIDCard = (x, y, width, height) => { if (!videoRef.current) return; const video = videoRef.current; const canvas = document.createElement("canvas"); canvas.width = width; canvas.height = height; const ctx = canvas.getContext("2d"); ctx.drawImage(video, x, y, width, height, 0, 0, width, height); setCapturedImage(canvas.toDataURL("image/png")); };

return ( <div> <video ref={videoRef} style={{ width: "100%", maxHeight: "400px" }} /> <canvas ref={canvasRef} style={{ display: "none" }} /> {boundingBox && ( <div style={{ position: "absolute", top: boundingBox.y, left: boundingBox.x, width: boundingBox.width, height: boundingBox.height, border: "2px solid red", }} ></div> )} {capturedImage && ( <div> <h3>Captured ID Card</h3> <img src={capturedImage} alt="Captured ID" style={{ width: "300px" }} /> <button onClick={() => setCapturedImage(null)}>Retake</button> <button onClick={() => console.log("Send to OCR API", capturedImage)}> Confirm & Send to OCR </button> </div> )} </div> ); };

export default IDCardCapture;

