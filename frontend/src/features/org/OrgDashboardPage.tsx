import { useState } from "react";
import { api } from "../../app/api";

export function OrgDashboardPage() {
  const [service, setService] = useState("1");
  const [counter, setCounter] = useState("1");
  const [result, setResult] = useState("");

  const callNext = async () => {
    const { data } = await api.post("/queues/entries/call_next/", { service, counter });
    setResult(`Called ${data.token}`);
  };

  return (
    <div className="p-6 space-y-3">
      <h2 className="text-xl font-semibold">Organization Dashboard</h2>
      <div className="card space-y-2">
        <input className="border p-2 rounded w-full" value={service} onChange={(e) => setService(e.target.value)} />
        <input className="border p-2 rounded w-full" value={counter} onChange={(e) => setCounter(e.target.value)} />
        <button className="rounded bg-brand-600 text-white px-4 py-2" onClick={callNext}>
          Call Next
        </button>
      </div>
      {!!result && <p>{result}</p>}
    </div>
  );
}
