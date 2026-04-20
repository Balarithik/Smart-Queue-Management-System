import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { api } from "../../app/api";
import { useAuthStore } from "../../store/useAuthStore";

export function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const setSession = useAuthStore((s) => s.setSession);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    const { data } = await api.post("/auth/login/", { username, password });
    setSession(data.access, "user");
    navigate("/join");
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <motion.form initial={{ opacity: 0 }} animate={{ opacity: 1 }} onSubmit={submit} className="card w-full max-w-md space-y-3">
        <h1 className="text-2xl font-bold">Smart Queue Login</h1>
        <input className="w-full border rounded p-2" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" />
        <input className="w-full border rounded p-2" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
        <button className="w-full rounded bg-brand-600 text-white py-2 hover:bg-brand-500 transition">Login</button>
      </motion.form>
    </div>
  );
}
