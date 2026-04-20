import { useState } from "react";
import { QrReader } from "react-qr-reader";
import { api } from "../../app/api";

export function QRScannerPage() {
  const [message, setMessage] = useState("Scan a service QR code");

  const onScan = async (value: string | null) => {
    if (!value) return;
    const [, organization_slug, service_code] = value.split(":");
    const { data } = await api.post("/queues/entries/join_qr/", { organization_slug, service_code });
    setMessage(`Joined queue at position ${data.position}`);
  };

  return (
    <div className="p-6 space-y-4">
      <h2 className="text-xl font-semibold">QR Queue Join</h2>
      <div className="card">
        <QrReader constraints={{ facingMode: "environment" }} onResult={(r) => onScan(r?.getText() ?? null)} />
      </div>
      <p>{message}</p>
    </div>
  );
}
