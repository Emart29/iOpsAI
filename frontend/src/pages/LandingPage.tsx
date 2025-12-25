import { Navbar } from '../components/layout/Navbar';
import { Footer } from '../components/layout/Footer';
import { Hero } from '../components/features/landing/Hero';
import { Features } from '../components/features/landing/Features';
import { HowItWorks } from '../components/features/landing/HowItWorks';
import { Contact } from '../components/features/landing/Contact';

export const LandingPage = () => {
    return (
        <div className="min-h-screen">
            <Navbar />
            <Hero />
            <Features />
            <HowItWorks />
            <Contact />
            <Footer />
        </div>
    );
};
