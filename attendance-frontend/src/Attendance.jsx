import { useRef, useState } from "react";
import { apiFetch } from "./apiClient";

function Attendance({ auth }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const startCamera = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    videoRef.current.srcObject = stream;
  };

  const captureAndSend = async () => {
    if (!auth?.token) {
      setMessage("Please login first to mark attendance.");
      return;
    }

    const canvas = canvasRef.current;
    const video = videoRef.current;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    canvas.toBlob(
      async (blob) => {
        setLoading(true);
        setMessage("");
        try {
          const formData = new FormData();
          formData.append("file", blob, "face.jpg");

          const data = await apiFetch("/api/v1/attendance/mark", {
            method: "POST",
            token: auth.token,
            body: formData,
          });

          setMessage(
            `Status: ${data.status}, confidence: ${(data.confidence * 100).toFixed(
              1
            )}%, liveness: ${data.liveness_score ?? "n/a"}`
          );
        } catch (err) {
          setMessage(`Error: ${err.message}`);
        } finally {
          setLoading(false);
        }
      },
      "image/jpeg"
    );
  };

  return (
    <div>
      <h3>Attendance</h3>
      {!auth?.token && (
        <p style={{ color: "red" }}>
          Please login with your username/password in the header to mark
          attendance.
        </p>
      )}
      <video ref={videoRef} autoPlay playsInline width="300" />
      <br />
      <button onClick={startCamera}>Start Camera</button>
      <button onClick={captureAndSend} disabled={loading || !auth?.token}>
        {loading ? "Processing..." : "Mark Attendance"}
      </button>
      <canvas ref={canvasRef} style={{ display: "none" }} />
      <p>{message}</p>
    </div>
  );
}

export default Attendance;
