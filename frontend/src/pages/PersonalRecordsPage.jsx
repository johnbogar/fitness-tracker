import React, { useState, useEffect } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

const API = "http://localhost:5000";

const UNITS = ["lbs", "kg", "km", "miles", "minutes", "seconds", "reps", "other"];

export default function PersonalRecordsPage() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    exercise: "",
    value: "",
    unit: "lbs",
    achieved_on: new Date().toISOString().split("T")[0],
    notes: "",
  });
  const [formError, setFormError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const fetchRecords = async () => {
    try {
      const res = await axios.get(`${API}/api/personal_records`, { withCredentials: true });
      setRecords(res.data);
    } catch (err) {
      setError("Failed to load personal records.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError("");
    if (!form.exercise.trim() || !form.value) {
      setFormError("Exercise and value are required.");
      return;
    }
    setSubmitting(true);
    try {
      await axios.post(`${API}/api/personal_records`, form, { withCredentials: true });
      setShowForm(false);
      setForm({ exercise: "", value: "", unit: "lbs", achieved_on: new Date().toISOString().split("T")[0], notes: "" });
      fetchRecords();
    } catch (err) {
      setFormError(err.response?.data?.error || "Failed to add record.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this personal record?")) return;
    try {
      await axios.delete(`${API}/api/personal_records/${id}`, { withCredentials: true });
      setRecords(records.filter((r) => r.id !== id));
    } catch (err) {
      alert("Failed to delete record.");
    }
  };

  // Group records by exercise for best-per-exercise summary
  const bestByExercise = {};
  records.forEach((r) => {
    if (!bestByExercise[r.exercise] || r.value > bestByExercise[r.exercise].value) {
      bestByExercise[r.exercise] = r;
    }
  });

  return (
    <div style={{ padding: "24px", maxWidth: "900px", margin: "0 auto", fontFamily: "sans-serif" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
        <div>
          <Link to="/dashboard" style={{ color: "#666", textDecoration: "none", fontSize: "14px" }}>
            &larr; Back to Dashboard
          </Link>
          <h1 style={{ margin: "8px 0 4px", fontSize: "28px" }}>Personal Records</h1>
          <p style={{ color: "#666", margin: 0 }}>Track your best performances over time</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          style={{
            background: "#2563eb", color: "#fff", border: "none", borderRadius: "8px",
            padding: "10px 20px", cursor: "pointer", fontSize: "15px", fontWeight: 600
          }}
        >
          {showForm ? "Cancel" : "+ Add PR"}
        </button>
      </div>

      {showForm && (
        <div style={{ background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: "12px", padding: "20px", marginBottom: "24px" }}>
          <h2 style={{ margin: "0 0 16px", fontSize: "18px" }}>Log a Personal Record</h2>
          {formError && <div style={{ color: "#dc2626", marginBottom: "12px" }}>{formError}</div>}
          <form onSubmit={handleSubmit}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginBottom: "12px" }}>
              <div>
                <label style={{ display: "block", marginBottom: "4px", fontSize: "13px", fontWeight: 600 }}>Exercise *</label>
                <input
                  type="text"
                  value={form.exercise}
                  onChange={(e) => setForm({ ...form, exercise: e.target.value })}
                  placeholder="e.g. Bench Press"
                  style={{ width: "100%", padding: "8px 10px", border: "1px solid #cbd5e1", borderRadius: "6px", fontSize: "14px", boxSizing: "border-box" }}
                />
              </div>
              <div>
                <label style={{ display: "block", marginBottom: "4px", fontSize: "13px", fontWeight: 600 }}>Value *</label>
                <input
                  type="number"
                  step="0.01"
                  value={form.value}
                  onChange={(e) => setForm({ ...form, value: e.target.value })}
                  placeholder="e.g. 225"
                  style={{ width: "100%", padding: "8px 10px", border: "1px solid #cbd5e1", borderRadius: "6px", fontSize: "14px", boxSizing: "border-box" }}
                />
              </div>
              <div>
                <label style={{ display: "block", marginBottom: "4px", fontSize: "13px", fontWeight: 600 }}>Unit</label>
                <select
                  value={form.unit}
                  onChange={(e) => setForm({ ...form, unit: e.target.value })}
                  style={{ width: "100%", padding: "8px 10px", border: "1px solid #cbd5e1", borderRadius: "6px", fontSize: "14px", boxSizing: "border-box" }}
                >
                  {UNITS.map((u) => <option key={u} value={u}>{u}</option>)}
                </select>
              </div>
              <div>
                <label style={{ display: "block", marginBottom: "4px", fontSize: "13px", fontWeight: 600 }}>Date Achieved</label>
                <input
                  type="date"
                  value={form.achieved_on}
                  onChange={(e) => setForm({ ...form, achieved_on: e.target.value })}
                  style={{ width: "100%", padding: "8px 10px", border: "1px solid #cbd5e1", borderRadius: "6px", fontSize: "14px", boxSizing: "border-box" }}
                />
              </div>
            </div>
            <div style={{ marginBottom: "16px" }}>
              <label style={{ display: "block", marginBottom: "4px", fontSize: "13px", fontWeight: 600 }}>Notes (optional)</label>
              <input
                type="text"
                value={form.notes}
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
                placeholder="e.g. First time hitting 225"
                style={{ width: "100%", padding: "8px 10px", border: "1px solid #cbd5e1", borderRadius: "6px", fontSize: "14px", boxSizing: "border-box" }}
              />
            </div>
            <button
              type="submit"
              disabled={submitting}
              style={{
                background: "#16a34a", color: "#fff", border: "none", borderRadius: "8px",
                padding: "10px 24px", cursor: "pointer", fontSize: "15px", fontWeight: 600
              }}
            >
              {submitting ? "Saving..." : "Save PR"}
            </button>
          </form>
        </div>
      )}

      {Object.keys(bestByExercise).length > 0 && (
        <div style={{ marginBottom: "28px" }}>
          <h2 style={{ fontSize: "18px", marginBottom: "12px" }}>Your Best Records</h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "12px" }}>
            {Object.values(bestByExercise).map((r) => (
              <div key={r.exercise} style={{
                background: "linear-gradient(135deg, #1e3a5f, #2563eb)",
                borderRadius: "10px", padding: "16px", color: "#fff"
              }}>
                <div style={{ fontSize: "12px", opacity: 0.8, marginBottom: "4px" }}>BEST</div>
                <div style={{ fontSize: "22px", fontWeight: 700 }}>{r.value} <span style={{ fontSize: "14px" }}>{r.unit}</span></div>
                <div style={{ fontSize: "14px", fontWeight: 600, marginTop: "4px" }}>{r.exercise}</div>
                <div style={{ fontSize: "12px", opacity: 0.7, marginTop: "4px" }}>{r.achieved_on}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div>
        <h2 style={{ fontSize: "18px", marginBottom: "12px" }}>All Records</h2>
        {loading ? (
          <p>Loading...</p>
        ) : error ? (
          <p style={{ color: "#dc2626" }}>{error}</p>
        ) : records.length === 0 ? (
          <div style={{ textAlign: "center", padding: "48px", background: "#f8fafc", borderRadius: "12px", color: "#666" }}>
            <div style={{ fontSize: "48px", marginBottom: "12px" }}>🏅</div>
            <p style={{ margin: 0, fontSize: "16px" }}>No personal records yet. Log your first PR!</p>
          </div>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "14px" }}>
            <thead>
              <tr style={{ background: "#f1f5f9" }}>
                <th style={{ padding: "10px 12px", textAlign: "left", border: "1px solid #e2e8f0" }}>Exercise</th>
                <th style={{ padding: "10px 12px", textAlign: "left", border: "1px solid #e2e8f0" }}>Value</th>
                <th style={{ padding: "10px 12px", textAlign: "left", border: "1px solid #e2e8f0" }}>Unit</th>
                <th style={{ padding: "10px 12px", textAlign: "left", border: "1px solid #e2e8f0" }}>Date</th>
                <th style={{ padding: "10px 12px", textAlign: "left", border: "1px solid #e2e8f0" }}>Notes</th>
                <th style={{ padding: "10px 12px", textAlign: "center", border: "1px solid #e2e8f0" }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {records.map((r) => (
                <tr key={r.id} style={{ borderBottom: "1px solid #e2e8f0" }}>
                  <td style={{ padding: "10px 12px", border: "1px solid #e2e8f0", fontWeight: 600 }}>{r.exercise}</td>
                  <td style={{ padding: "10px 12px", border: "1px solid #e2e8f0" }}>{r.value}</td>
                  <td style={{ padding: "10px 12px", border: "1px solid #e2e8f0" }}>{r.unit}</td>
                  <td style={{ padding: "10px 12px", border: "1px solid #e2e8f0" }}>{r.achieved_on}</td>
                  <td style={{ padding: "10px 12px", border: "1px solid #e2e8f0", color: "#666" }}>{r.notes || "-"}</td>
                  <td style={{ padding: "10px 12px", border: "1px solid #e2e8f0", textAlign: "center" }}>
                    <button
                      onClick={() => handleDelete(r.id)}
                      style={{ background: "#dc2626", color: "#fff", border: "none", borderRadius: "6px", padding: "4px 12px", cursor: "pointer", fontSize: "13px" }}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
