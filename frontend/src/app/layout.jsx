import './globals.css';

export const metadata = {
  title: 'Customer Support FTE',
  description: 'AI-powered Customer Success',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
