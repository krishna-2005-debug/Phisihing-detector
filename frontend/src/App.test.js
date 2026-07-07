import { render, screen } from "@testing-library/react";
import App from "./App";

test("renders app without crashing", () => {
  render(<App />);
});

test("renders page title", () => {
  render(<App />);
  expect(screen.getByText(/Phishing URL Scanner/i)).toBeInTheDocument();
});

test("renders settings controls", () => {
  render(<App />);
  expect(screen.getByText(/Sensitivity/i)).toBeInTheDocument();
  expect(screen.getByText(/Deep HTML analysis/i)).toBeInTheDocument();
  expect(screen.getByText(/Force offline demo/i)).toBeInTheDocument();
});

test("renders recent scans in sidebar", () => {
  render(<App />);
  expect(screen.getByText(/Recent scans/i)).toBeInTheDocument();
  expect(screen.getByText(/secure-login-bank-verification.com/i)).toBeInTheDocument();
});
