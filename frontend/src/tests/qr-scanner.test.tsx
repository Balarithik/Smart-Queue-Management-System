import { render, screen } from "@testing-library/react";
import { QRScannerPage } from "../features/qr/QRScannerPage";

describe("QRScannerPage", () => {
  it("renders scanner title", () => {
    render(<QRScannerPage />);
    expect(screen.getByText(/QR Queue Join/i)).toBeInTheDocument();
  });
});
