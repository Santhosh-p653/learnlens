export const metadata = {
  title: "LearnLens — Learning Made Accessible",
  description: "Photo to simplified explanation, spoken in your language.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: "system-ui, sans-serif", background: "#0b1120", color: "#e5e7eb" }}>
        {children}
      </body>
    </html>
  );
}