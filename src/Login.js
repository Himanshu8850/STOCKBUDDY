import { useState } from "react";
import "./Login.css";

function Login({ onLogin, onDemo }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onLogin({ email, password });
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div className="logo">SB</div>
          <div>
            <h1>Welcome back</h1>
            <p>Sign in to view your portfolio.</p>
          </div>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <label className="field">
            <span>Email</span>
            <input
              type="email"
              placeholder="you@stockbuddy.ai"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </label>

          <label className="field">
            <span>Password</span>
            <input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </label>

          <button type="submit" className="login-btn primary">
            Sign in
          </button>
        </form>

        <div className="divider">
          <span>or</span>
        </div>

        <button type="button" className="login-btn secondary" onClick={onDemo}>
          Explore demo mode
        </button>

        <p className="footnote">No account? Demo mode uses sample data.</p>
      </div>
    </div>
  );
}

export default Login;
