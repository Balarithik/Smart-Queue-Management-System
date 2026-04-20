import { useEffect, useState } from "react";
import { api } from "../../app/api";

export function NotificationSettingsPage() {
  const [optIn, setOptIn] = useState(true);
  const [phone, setPhone] = useState("");

  useEffect(() => {
    api.get("/notifications/settings/").then((res) => {
      setOptIn(res.data.whatsapp_opt_in);
      setPhone(res.data.phone_number);
    });
  }, []);

  const save = async () => {
    await api.patch("/notifications/settings/", { whatsapp_opt_in: optIn });
  };

  return (
    <div className="p-6">
      <h2 className="text-xl font-semibold mb-4">Notification Settings</h2>
      <div className="card space-y-2">
        <p>{phone}</p>
        <label className="flex items-center gap-2">
          <input type="checkbox" checked={optIn} onChange={(e) => setOptIn(e.target.checked)} />
          WhatsApp updates
        </label>
        <button className="rounded bg-brand-600 text-white px-4 py-2" onClick={save}>
          Save
        </button>
      </div>
    </div>
  );
}
