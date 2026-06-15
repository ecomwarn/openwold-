import { useState } from 'react';
import Nav from './components/Nav.jsx';
import Hero from './components/Hero.jsx';
import HowItWorks from './components/HowItWorks.jsx';
import SocialProof from './components/SocialProof.jsx';
import Features from './components/Features.jsx';
import Marquee from './components/Marquee.jsx';
import Comparison from './components/Comparison.jsx';
import Trust from './components/Trust.jsx';
import FAQ from './components/FAQ.jsx';
import Footer from './components/Footer.jsx';
import EmailModal from './components/EmailModal.jsx';

export default function App() {
  const [modalOpen, setModalOpen] = useState(false);
  const openModal = () => setModalOpen(true);
  const closeModal = () => setModalOpen(false);

  return (
    <>
      <Nav onCtaClick={openModal} />
      <main>
        <Hero onCtaClick={openModal} />
        <HowItWorks />
        <SocialProof />
        <Features />
        <Marquee />
        <Comparison />
        <Trust />
        <FAQ />
      </main>
      <Footer onSignUpClick={openModal} />
      <EmailModal open={modalOpen} onClose={closeModal} />
    </>
  );
}
