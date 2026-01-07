import { useState, useEffect } from "react";
import { apiFetch } from "./apiClient";

function Admin({ auth }) {
  const [view, setView] = useState("add");
  
  // Add User state
  const [name, setName] = useState("");
  const [roll, setRoll] = useState("");
  const [password, setPassword] = useState("");
  const [newUserId, setNewUserId] = useState(null);
  const [enrollFile, setEnrollFile] = useState(null);
  const [msg, setMsg] = useState("");
  
  // Attendance state
  const [attendance, setAttendance] = useState([]);

  const fetchAttendance = async () => {
    if (!auth?.token) return;
    try {
      const data = await apiFetch("/api/v1/attendance/logs?limit=100", {
        method: "GET",
        token: auth.token,
      });
      setAttendance(data);
    } catch (err) {
      console.error("Failed to fetch attendance", err);
      setAttendance([]);
    }
  };

  useEffect(() => {
    if (view === "records") {
      fetchAttendance();
    }
  }, [view]);

  const submitUser = async () => {
    if (!name || !roll || !password) {
      setMsg("Please fill all fields");
      return;
    }
    if (!auth?.token) {
      setMsg("You must be logged in as admin");
      return;
    }
    try {
      const data = await apiFetch("/api/v1/users", {
        method: "POST",
        token: auth.token,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          full_name: name,
          roll_no: roll,
          password,
          role: "STUDENT",
        }),
      });
      setMsg("✅ User created. Now upload a face image to enroll.");
      setNewUserId(data.id);
      setName("");
      setRoll("");
      setPassword("");
    } catch (error) {
      setMsg(`❌ ${error.message}`);
    }
  };

  const enrollFace = async () => {
    if (!newUserId) {
      setMsg("Create a user first before enrolling face.");
      return;
    }
    if (!enrollFile) {
      setMsg("Select an image to enroll.");
      return;
    }
    if (!auth?.token) {
      setMsg("You must be logged in as admin");
      return;
    }
    try {
      const formData = new FormData();
      formData.append("file", enrollFile);
      const data = await apiFetch(`/api/v1/users/${newUserId}/enroll`, {
        method: "POST",
        token: auth.token,
        body: formData,
      });
      setMsg(
        `✅ Face enrolled (model: ${data.model_version}, liveness: ${data.liveness_score})`
      );
      setEnrollFile(null);
    } catch (error) {
      setMsg(`❌ ${error.message}`);
    }
  };

  if (!auth?.token || auth.role !== "ADMIN") {
    return (
      <div>
        <h3>Admin Panel</h3>
        <p style={{ color: "red" }}>
          Admin login required. Please login as <strong>admin</strong> in the
          header.
        </p>
      </div>
    );
  }

  return (
    <div>
      <h3>Admin Panel</h3>
      
      <button onClick={() => setView("add")}>Add & Enroll User</button>
      <button onClick={() => setView("records")}>View Attendance</button>
      
      <hr />
      
      {view === "add" && (
        <div>
          <h4>Add New User</h4>
          <input
            placeholder="Full name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <br />
          <input
            placeholder="Roll No / Employee ID"
            value={roll}
            onChange={(e) => setRoll(e.target.value)}
          />
          <br />
          <input
            type="password"
            placeholder="Initial password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <br />
          <button onClick={submitUser}>Create User</button>

          {newUserId && (
            <>
              <hr />
              <h4>Enroll Face for User ID: {newUserId}</h4>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => setEnrollFile(e.target.files[0])}
              />
              <br />
              <button onClick={enrollFace}>Upload & Enroll Face</button>
            </>
          )}

          <p
            style={{
              color: msg.startsWith("✅") ? "green" : "red",
              fontWeight: "bold",
            }}
          >
            {msg}
          </p>
        </div>
      )}
      
      {view === "records" && (
        <div>
          <h4>Attendance Records</h4>
          <button onClick={fetchAttendance}>Refresh</button>
          <br /><br />
          
          {attendance.length === 0 ? (
            <p>No attendance records found</p>
          ) : (
            <table
              border="1"
              cellPadding="8"
              style={{ borderCollapse: "collapse", fontSize: 14 }}
            >
              <thead>
                <tr>
                  <th>User ID</th>
                  <th>Date</th>
                  <th>Type</th>
                  <th>Timestamp</th>
                  <th>Confidence</th>
                  <th>Liveness</th>
                  <th>Manual</th>
                </tr>
              </thead>
              <tbody>
                {attendance.map((record) => (
                  <tr key={record.id}>
                    <td>{record.user_id}</td>
                    <td>{record.date}</td>
                    <td>{record.type}</td>
                    <td>{record.timestamp}</td>
                    <td>{record.confidence}</td>
                    <td>{record.liveness_score ?? "-"}</td>
                    <td>{record.manual_override ? "Yes" : "No"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}

export default Admin;
