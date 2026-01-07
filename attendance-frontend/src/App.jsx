import { useState } from "react";
import Attendance from "./Attendance";
import Admin from "./Admin";
import { API_BASE } from "./apiClient";

function App() {
  const [page, setPage] = useState("attendance");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [auth, setAuth] = useState({
    token: null,
    username: null,
    role: null,
  });
  const [authError, setAuthError] = useState("");

  const isLoggedIn = !!auth.token;

  const handleLogin = async () => {
    setAuthError("");
    try {
      const body = new URLSearchParams();
      body.set("username", username);
      body.set("password", password);

      const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body,
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Login failed");
      }

      const role = username === "admin" ? "ADMIN" : "USER";
      setAuth({
        token: data.access_token,
        username,
        role,
      });
      setPassword("");
    } catch (err) {
      setAuthError(err.message);
    }
  };

  const handleLogout = () => {
    setAuth({ token: null, username: null, role: null });
    setUsername("");
    setPassword("");
    setAuthError("");
  };

  return (
    <div style={{ padding: 20, maxWidth: 900, margin: "0 auto" }}>
      <h2>Facial Attendance System</h2>

      {/* Simple login bar */}
      <div
        style={{
          display: "flex",
          gap: 8,
          alignItems: "center",
          marginBottom: 16,
          flexWrap: "wrap",
        }}
      >
        {isLoggedIn ? (
          <>
            <span>
              Logged in as <strong>{auth.username}</strong>{" "}
              {auth.role === "ADMIN" && "(admin)"}
            </span>
            <button onClick={handleLogout}>Logout</button>
          </>
        ) : (
          <>
            <input
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <input
              placeholder="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <button onClick={handleLogin}>Login</button>
            {authError && (
              <span style={{ color: "red", fontSize: 12 }}>{authError}</span>
            )}
          </>
        )}
      </div>

      {/* Navigation */}
      <div style={{ marginBottom: 12 }}>
        <button
          onClick={() => setPage("attendance")}
          disabled={page === "attendance"}
        >
          Attendance
        </button>
        <button
          onClick={() => setPage("admin")}
          disabled={page === "admin"}
          style={{ marginLeft: 8 }}
        >
          Admin
        </button>
      </div>

      <hr />

      {page === "attendance" && <Attendance auth={auth} />}
      {page === "admin" && <Admin auth={auth} />}
    </div>
  );
}

export default App;

