import React, { FormEvent, useState } from "react";
import {
  ArrowDown,
  ArrowRight,
  ArrowUpRight,
  BedDouble,
  Compass,
  MapPin,
  Plane,
  Send,
  Sparkles,
} from "lucide-react";

interface LandingPageProps {
  onNavigate: (page: string) => void;
  onSetPrompt?: (prompt: string) => void;
}

const modes = [
  { label: "Flights", icon: Plane },
  { label: "Hotels", icon: BedDouble },
  { label: "Experiences", icon: Sparkles },
] as const;

const destinations = [
  {
    name: "Farther afield",
    country: "A world of possibility",
    note: "Let curiosity lead",
    image: "/images/travel-world.jpg",
    prompt:
      "Help me discover an unforgettable destination for my next trip, with a mix of iconic sights and local experiences.",
  },
  {
    name: "The journey",
    country: "Take to the skies",
    note: "Make getting there part of it",
    image: "/images/travel-flight.jpg",
    prompt:
      "Help me plan a smooth flight-focused getaway, including the best time to travel and what to do when I arrive.",
  },
  {
    name: "Island retreat",
    country: "Maldives",
    note: "Slow days by the water",
    image: "/images/travel-island.jpg",
    prompt:
      "Plan a relaxing island escape to the Maldives with beautiful beaches, a memorable stay, and time to unwind.",
  },
  {
    name: "Alpine stillness",
    country: "Canadian Rockies",
    note: "Find your mountain air",
    image: "/images/travel-lake.jpg",
    prompt:
      "Plan a scenic trip to the Canadian Rockies with turquoise lakes, mountain views, and easy-to-moderate hikes.",
  },
  {
    name: "Wild horizons",
    country: "Mountain trails",
    note: "Go a little further",
    image: "/images/travel-hike.jpg",
    prompt:
      "Plan an inspiring mountain hiking trip with beautiful trails, comfortable places to stay, and enough time to explore.",
  },
];

export const LandingPage: React.FC<LandingPageProps> = ({ onNavigate, onSetPrompt }) => {
  const [activeMode, setActiveMode] = useState<(typeof modes)[number]["label"]>("Experiences");
  const [prompt, setPrompt] = useState("");

  const submitPrompt = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const cleanPrompt = prompt.trim();
    if (!cleanPrompt) return;
    onSetPrompt?.(cleanPrompt);
    onNavigate("planner");
  };

  const chooseDestination = (destinationPrompt: string) => {
    setPrompt(destinationPrompt);
    setActiveMode("Experiences");
  };

  return (
    <div className="luxury-landing">
      <section className="luxury-hero" aria-labelledby="landing-title">
        <div className="hero-orb hero-orb-one" />
        <div className="hero-orb hero-orb-two" />
        <div className="hero-grid" />

        <div className="hero-content">
          <div className="hero-copy">
            <div className="hero-eyebrow">
              <span className="eyebrow-spark"><Sparkles size={13} /></span>
              A more thoughtful way to travel
            </div>
            <h1 id="landing-title">
              Where will
              <br />
              you go <span>next?</span>
            </h1>
            <p className="hero-description">
              Tell us what moves you. We’ll bring the world a little closer, with a journey
              designed around you.
            </p>

            <div className="hero-mode-label">Your journey, your way</div>
            <div className="hero-mode-switch" role="group" aria-label="Travel planning focus">
              {modes.map(({ label, icon: Icon }) => (
                <button
                  key={label}
                  type="button"
                  aria-pressed={activeMode === label}
                  className={`mode-pill ${activeMode === label ? "mode-pill-active" : ""}`}
                  onClick={() => setActiveMode(label)}
                >
                  <Icon size={15} strokeWidth={1.8} />
                  {label}
                </button>
              ))}
            </div>

            <button className="discover-link" onClick={() => onNavigate("planner")}>
              Start planning <ArrowRight size={15} />
            </button>
          </div>

          <div className="assistant-column">
            <div className="assistant-card">
              <div className="assistant-topline">
                <div className="assistant-identity">
                  <div className="assistant-avatar"><Compass size={20} /></div>
                  <div>
                    <span className="assistant-name">Tripto</span>
                    <span className="assistant-role">Your personal travel concierge</span>
                  </div>
                </div>
                <span className="online-indicator"><i /> Here for you</span>
              </div>

              <div className="assistant-conversation">
                <div className="assistant-date"><span /> A LITTLE INSPIRATION <span /></div>
                <div className="assistant-message">
                  <span className="message-kicker">Hello, traveler <span>✳</span></span>
                  <h2>Hello, I’m Tripto.<br />How can I help you today?</h2>
                  <p>Dream it up — a faraway escape, a weekend reset, or somewhere wonderfully unexpected.</p>
                </div>
                <div className="suggestion-row">
                  <button onClick={() => chooseDestination(destinations[0].prompt)}>A tropical escape <ArrowUpRight size={13} /></button>
                  <button onClick={() => chooseDestination(destinations[1].prompt)}>Somewhere soulful <ArrowUpRight size={13} /></button>
                </div>
              </div>

              <form className="assistant-input-wrap" onSubmit={submitPrompt}>
                <label className="sr-only" htmlFor="trip-prompt">Describe your ideal trip</label>
                <textarea
                  id="trip-prompt"
                  rows={2}
                  maxLength={2000}
                  value={prompt}
                  onChange={(event) => setPrompt(event.target.value)}
                  placeholder={
                    activeMode === "Flights"
                      ? "Where would you like to fly?"
                      : activeMode === "Hotels"
                        ? "Tell me about your perfect stay..."
                        : "I’m dreaming of a trip to..."
                  }
                />
                <div className="input-toolbar">
                  <span><Sparkles size={13} /> Thoughtful plans, made for you</span>
                  <button type="submit" aria-label="Start planning" disabled={!prompt.trim()}>
                    <Send size={16} />
                  </button>
                </div>
              </form>
              <div className="assistant-footnote">VoyageAI brings a team of travel specialists to every plan.</div>
            </div>
            <div className="hero-footnote"><span /> Made for the way you want to feel.</div>
          </div>

          <aside className="destination-rail" aria-label="Destination inspiration">
            <div className="rail-heading">
              <div>
                <span className="rail-kicker">A world of possibility</span>
                <h2>Places to begin</h2>
              </div>
              <span className="rail-count">01 — 05</span>
            </div>
            <div className="destination-stack">
              {destinations.map((destination, index) => (
                <button
                  type="button"
                  className="destination-card"
                  key={destination.name}
                  onClick={() => chooseDestination(destination.prompt)}
                  aria-label={`Plan a trip to ${destination.name}`}
                >
                  <img className="destination-image" src={destination.image} alt="" />
                  <span className="destination-shade" />
                  <span className="destination-number">0{index + 1}</span>
                  <span className="destination-copy">
                    <span className="destination-location"><MapPin size={12} /> {destination.country}</span>
                    <span className="destination-title">{destination.name}</span>
                    <span className="destination-note">{destination.note}</span>
                  </span>
                  <span className="destination-arrow"><ArrowUpRight size={15} /></span>
                </button>
              ))}
            </div>
            <button className="all-destinations" onClick={() => onNavigate("planner")}>
              Explore beyond the ordinary <ArrowRight size={14} />
            </button>
          </aside>
        </div>

        <div className="hero-bottomline">
          <span><span className="bottomline-dot" /> A little more wonder in every mile</span>
          <button onClick={() => onNavigate("planner")}>SCROLL TO EXPLORE <ArrowDown size={13} /></button>
          <span>DESIGNED AROUND YOU <span className="bottomline-star">✳</span></span>
        </div>
      </section>
    </div>
  );
};
