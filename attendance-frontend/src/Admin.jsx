import { useState, useEffect } from "react";

function Admin() {
  const [view, setView] = useState("add");
  
  // Add User state
  const [name, setName] = useState("");
  const [roll, setRoll] = useState("");
  const [file, setFile] = useState(null);
  const [msg, setMsg] = useState("");
  
  // Attendance state
  const [attendance, setAttendance] = useState([]);

  const fetchAttendance = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/attendance/list");
      const data = await res.json();
      setAttendance(data);
    } catch (err) {
      console.error("Failed to fetch attendance");
      setAttendance([]);
    }
  };

  useEffect(() => {
    if (view === "records") {
      fetchAttendance();
    }
  }, [view]);

  const submit = async () => {
    if (!name || !roll || !file) {
      setMsg("Please fill all fields and select an image");
      return;
    }

    const formData = new FormData();
    formData.append("name", name);
    formData.append("roll_no", roll);
    formData.append("file", file);

    try {
      const res = await fetch("http://127.0.0.1:8000/add-user", {
        method: "POST",
        body: formData
      });

      const data = await res.json();
      
      if (res.ok) {
        setMsg(`✅ ${data.message || "User added successfully"}`);
        setName("");
        setRoll("");
        setFile(null);
      } else {
        setMsg(`❌ ${data.detail || "Failed to add user"}`);
      }
    } catch (error) {
      setMsg(`❌ Error: ${error.message}`);
    }
  };

  return (
    <div>
      <h3>Admin Panel</h3>
      
      <button onClick={() => setView("add")}>Add User</button>
      <button onClick={() => setView("records")}>View Attendance</button>
      
      <hr />
      
      {view === "add" && (
        <div>
          <h4>Add New User</h4>
          <input 
            placeholder="Name" 
            value={name}
            onChange={e => setName(e.target.value)} 
          />
          <br />
          <input 
            placeholder="Roll No" 
            value={roll}
            onChange={e => setRoll(e.target.value)} 
          />
          <br />
          <input 
            type="file" 
            accept="image/*"
            onChange={e => setFile(e.target.files[0])} 
          />
          <br />
          <button onClick={submit}>Add User</button>
          <p style={{ 
            color: msg.startsWith("✅") ? "green" : "red",
            fontWeight: "bold"
          }}>
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
            <table border="1" cellPadding="8" style={{ borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Date</th>
                  <th>Entry Time</th>
                  <th>Exit Time</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {attendance.map((record) => (
                  <tr key={record.id}>
                    <td>{record.name}</td>
                    <td>{record.date}</td>
                    <td>{record.entry_time || "-"}</td>
                    <td>{record.exit_time || "-"}</td>
                    <td>
                      {record.exit_time ? "Completed" : "Present"}
                    </td>
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
