import { useRef, useState } from "react";

function Attendance() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [message, setMessage] = useState("");

  const startCamera = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    videoRef.current.srcObject = stream;
  };

  const captureAndSend = async () => {
    const canvas = canvasRef.current;
    const video = videoRef.current;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    canvas.toBlob(async (blob) => {
      const formData = new FormData();
      formData.append("file", blob, "face.jpg");

      const res = await fetch("http://127.0.0.1:8000/mark-attendance", {
        method: "POST",
        body: formData
      });

      const data = await res.json();
      setMessage(JSON.stringify(data));
    }, "image/jpeg");
  };

  return (
    <div>
      <h3>Attendance</h3>
      <video ref={videoRef} autoPlay playsInline width="300" />
      <br />
      <button onClick={startCamera}>Start Camera</button>
      <button onClick={captureAndSend}>Mark Attendance</button>
      <canvas ref={canvasRef} style={{ display: "none" }} />
      <p>{message}</p>
    </div>
  );
}

export default Attendance;
