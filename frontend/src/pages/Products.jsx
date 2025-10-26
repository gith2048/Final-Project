// src/pages/Products.jsx
import React from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";

// Reusable Card Component
const Card = ({ children, className = "", hoverScale = 1.05 }) => (
  <motion.div
    className={`bg-white p-6 rounded-lg shadow ${className}`}
    whileHover={{ scale: hoverScale }}
    transition={{ type: "spring", stiffness: 300 }}
  >
    {children}
  </motion.div>
);

const Products = () => {
  const products = [
    {
      id: 1,
      name: "Smart IoT Monitor",
      image: "/assets/smart_iot_monitor.jpg", // store locally in public/images/
      description: "Real-time machine monitoring for predictive maintenance.",
      features: ["Predictive alerts", "IoT sensors", "Data analytics"],
    },
    {
      id: 2,
      name: "Predictive Dashboard",
      image: "/assets/predictive_dashboard.jpg",
      description: "Analytics & insights to optimize your operations.",
      features: ["Machine learning", "Custom dashboards", "Reports & alerts"],
    },
    {
      id: 3,
      name: "AI Maintenance Predictor",
      image: "/assets/ai_maintenance_predictor.jpg",
      description: "Prevent downtime using advanced AI algorithms.",
      features: ["Failure prediction", "Cost optimization", "OEE improvement"],
    },
  ];

  const approach = [
    { title: "Monitor", desc: "Track machine performance in real-time.", icon: "fas fa-eye" },
    { title: "Predict", desc: "AI detects potential failures before they occur.", icon: "fas fa-robot" },
    { title: "Optimize", desc: "Reduce downtime and improve efficiency.", icon: "fas fa-chart-line" },
  ];



  const faqs = [
    { q: "How quickly can we implement your solutions?", a: "Most implementations take 4-6 weeks depending on complexity." },
    { q: "What types of machines can your systems monitor?", a: "Our solutions monitor virtually any industrial equipment." },
    { q: "Do I need to replace my current maintenance system?", a: "No, our solutions integrate with existing systems." },
    { q: "What's the typical ROI for your solutions?", a: "Most clients see ROI within 6-12 months." },
  ];

  return (
    <div className="w-full overflow-hidden font-sans">
      {/* Hero */}
      <section className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white py-24 px-4 flex flex-col items-center justify-center">
        <motion.h1 className="text-5xl md:text-6xl font-bold mb-4 text-center"
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}>
          Our Products
        </motion.h1>
        <motion.p className="text-lg md:text-2xl max-w-3xl text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 0.5 }}>
          Explore predictive maintenance solutions designed to maximize uptime and efficiency.
        </motion.p>
      </section>

      {/* Products */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto text-center mb-12">
          <h2 className="text-4xl font-bold mb-4">Our Solutions</h2>
          <p className="text-gray-600 text-lg md:text-xl">Each product addresses maintenance challenges and integrates seamlessly.</p>
        </div>
        <div className="max-w-6xl mx-auto grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8">
          {products.map((p) => (
            <Card key={p.id}>
              <img src={p.image} alt={p.name} loading="lazy" className="mx-auto mb-4 h-48 w-full object-cover rounded-lg" />
              <h3 className="font-bold text-xl mb-2">{p.name}</h3>
              <p className="text-gray-600 mb-4">{p.description}</p>
              <h4 className="font-semibold mb-2">Key Features:</h4>
              <ul className="list-disc list-inside text-gray-600 mb-4">
                {p.features.map((f, i) => <li key={i}>{f}</li>)}
              </ul>
             <div className="flex flex-col sm:flex-row justify-end gap-3">
          <Link to="/contact"  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition">Request Demo</Link>
           </div>
             
            </Card>
          ))}
        </div>
      </section>

      {/* Our Approach */}
      <section className="py-16 px-4 bg-gray-50">
        <div className="max-w-6xl mx-auto text-center mb-12">
          <h2 className="text-4xl font-bold mb-4">Our Approach</h2>
          <p className="text-gray-600 text-lg md:text-xl">How we deliver exceptional predictive maintenance solutions.</p>
        </div>
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
          {approach.map((a, i) => (
            <Card key={i} hoverScale={1.08}>
              <h3 className="font-bold text-xl mb-2">{a.title}</h3>
              <p className="text-gray-600">{a.desc}</p>
            </Card>
          ))}
        </div>
      </section>

      

     

      {/* FAQ Accordion */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto text-center mb-12">
          <h2 className="text-4xl font-bold mb-4">Frequently Asked Questions</h2>
        </div>
        <div className="max-w-3xl mx-auto space-y-4">
          {faqs.map((f, i) => (
            <details key={i} className="bg-gray-50 p-4 rounded shadow cursor-pointer">
              <summary className="font-bold">{f.q}</summary>
              <p className="mt-2 text-gray-600">{f.a}</p>
            </details>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 px-4 bg-gradient-to-r from-blue-600 to-indigo-700 text-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-4">Ready to Transform Your Maintenance Strategy?</h2>
          <p className="text-lg md:text-xl mb-6">Contact us today to schedule a demo or consultation.</p>
          <Link to="/contact" className="px-6 py-3 bg-yellow-400 text-blue-800 font-bold rounded-lg hover:bg-yellow-500 transition">
            Connect With Us
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Products;
