import { render, screen } from "@testing-library/react";
import { NotificationSettingsPage } from "../features/notifications/NotificationSettingsPage";

describe("NotificationSettingsPage", () => {
  it("renders heading", () => {
    render(<NotificationSettingsPage />);
    expect(screen.getByText(/Notification Settings/i)).toBeInTheDocument();
  });
});
