import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../App';
import { BrowserRouter } from 'react-router-dom';

// Helper to render with router
const renderWithRouter = (ui: React.ReactElement) => {
    return render(<BrowserRouter>{ui}</BrowserRouter>);
};

describe('App routing', () => {
    test('renders landing page by default', () => {
        renderWithRouter(<App />);
        expect(screen.getByText(/iOps/i)).toBeInTheDocument();
    });

    test('navigates to dashboard page', () => {
        renderWithRouter(<App />);
        const launchBtn = screen.getByRole('link', { name: /launch app/i });
        fireEvent.click(launchBtn);
        // DashboardPage contains some known text, e.g., "Dashboard"
        expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
    });
});

describe('Dark mode toggle', () => {
    test('toggles dark mode and persists', () => {
        renderWithRouter(<App />);
        const toggleBtn = screen.getByTitle(/switch to dark mode/i) as HTMLButtonElement;
        // Initially light mode
        expect(document.documentElement.classList.contains('dark')).toBeFalsy();
        fireEvent.click(toggleBtn);
        expect(document.documentElement.classList.contains('dark')).toBeTruthy();
        // Simulate reload by re‑rendering
        renderWithRouter(<App />);
        // Should still be dark because localStorage saved it
        expect(document.documentElement.classList.contains('dark')).toBeTruthy();
    });
});
