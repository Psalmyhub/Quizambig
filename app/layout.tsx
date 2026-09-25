import "./globals.css";

export const metadata = {
  title: "Quizambig",
  description: "Semantic quizzes powered by GenLayer",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
