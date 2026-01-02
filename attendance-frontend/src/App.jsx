import { useState } from "react";
import Attendance from "./Attendance";
import Admin from "./Admin";

function App() {
  const [page, setPage] = useState("attendance");

  return (
    <div style={{ padding: 20 }}>
      <h2>Facial Attendance System</h2>

      <button onClick={() => setPage("attendance")}>Attendance</button>
      <button onClick={() => setPage("admin")}>Admin</button>

      <hr />

      {page === "attendance" && <Attendance />}
      {page === "admin" && <Admin />}
    </div>
  );
}

export default App;
