import React from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";

const About = () => {
  const team = [
    {
      name: "Sarah Johnson",
      role: "CEO & Co-Founder",
      image: "https://images.pexels.com/photos/2381069/pexels-photo-2381069.jpeg?auto=compress&cs=tinysrgb&w=600",
      bio: "With 20+ years in industrial automation, Sarah leads our company vision and strategy."
    },
    {
      name: "David Chen",
      role: "CTO & Co-Founder",
      image: "https://images.pexels.com/photos/2379004/pexels-photo-2379004.jpeg?auto=compress&cs=tinysrgb&w=600",
      bio: "David oversees technology development, bringing expertise in AI and machine learning."
    },
    {
      name: "Michael Rodriguez",
      role: "VP of Engineering",
      image: "https://images.pexels.com/photos/762020/pexels-photo-762020.jpeg?auto=compress&cs=tinysrgb&w=600",
      bio: "Michael leads product development ensuring highest standards."
    },
    {
      name: "Jennifer Kim",
      role: "Director of Customer Success",
      image: "https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg?auto=compress&cs=tinysrgb&w=600",
      bio: "Jennifer ensures clients achieve maximum value from our solutions."
    },
  ];

  const approach = [
    { icon: "fas fa-search", title: "Assessment", desc: "We begin by understanding your equipment and challenges." },
    { icon: "fas fa-cogs", title: "Implementation", desc: "Deploy sensors, configure software, integrate systems." },
    { icon: "fas fa-chart-line", title: "Optimization", desc: "Refine algorithms to improve prediction accuracy over time." },
  ];

  const certifications = [
    { title: "ISO 9001", desc: "Quality Management", image: "https://via.placeholder.com/100?text=ISO+9001" },
    { title: "ISO 27001", desc: "Information Security", image: "https://via.placeholder.com/100?text=ISO+27001" },
    { title: "AI Ethics", desc: "Responsible AI Use", image: "https://via.placeholder.com/100?text=AI+Ethics" },
    { title: "Industry 4.0", desc: "Smart Manufacturing", image: "https://via.placeholder.com/100?text=Industry+4.0" },
  ];

  return (
    <div className="w-full overflow-hidden">

      {/* Hero */}
      <section className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white py-24 px-4 text-center">
        <motion.h1 className="text-4xl sm:text-5xl md:text-6xl font-bold mb-4"
          initial={{ opacity: 0, y: -50 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 1 }}
        >
          About Optimus-PdM
        </motion.h1>
        <motion.p className="text-lg sm:text-xl md:text-2xl max-w-3xl mx-auto"
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 1, delay: 0.5 }}
        >
          Learn about our mission, our team, and our commitment to revolutionizing industrial maintenance.
        </motion.p>
      </section>

      {/* Company Overview */}
      <section className="py-16 px-4 max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
        <motion.div className="space-y-4" initial={{ opacity: 0, x: -50 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}>
          <h2 className="text-3xl font-bold">Our Story</h2>
          <p>Founded in 2020 by industry veterans, Optimus-PdM bridges the gap between reactive and predictive maintenance.</p>
          <p>Our solutions leverage machine learning, IoT, and advanced analytics to reduce downtime and extend equipment life.</p>
          <p>Deployed across multiple industries including manufacturing, energy, transportation, and healthcare, we help clients achieve measurable results.</p>
        </motion.div>
        <motion.img src="https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg?auto=compress&cs=tinysrgb&w=600"
          alt="PredictMaintain Office"
          className="w-full rounded-lg shadow-lg"
          initial={{ opacity: 0, x: 50 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}
        />
      </section>

      {/* Mission & Vision */}
      <section className="py-16 px-4 bg-gray-50 max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
        <motion.div initial={{ opacity: 0, x: -50 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}>
          <h2 className="text-3xl font-bold mb-4">Our Mission</h2>
          <p>Empower businesses with intelligent maintenance solutions to prevent unplanned downtime and optimize efficiency.</p>
          <h2 className="text-3xl font-bold mt-8 mb-4">Our Vision</h2>
          <p>Lead the global transition to predictive maintenance, anticipating failures before they occur.</p>
          <h2 className="text-3xl font-bold mt-8 mb-4">Our Values</h2>
          <ul className="list-disc pl-6 space-y-2">
            <li><strong>Innovation:</strong> Pushing the boundaries of predictive analytics</li>
            <li><strong>Excellence:</strong> Highest quality in products and services</li>
            <li><strong>Partnership:</strong> Building lasting client relationships</li>
            <li><strong>Sustainability:</strong> Extending equipment life and reducing waste</li>
          </ul>
        </motion.div>
        <motion.img src="https://images.pexels.com/photos/3183151/pexels-photo-3183151.jpeg?auto=compress&cs=tinysrgb&w=600"
          alt="Mission Vision"
          className="w-full rounded-lg shadow-lg"
          initial={{ opacity: 0, x: 50 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}
        />
      </section>

      

{/* Our Approach */}
<section className="py-20 px-4 bg-gray-50">
  <div className="max-w-6xl mx-auto text-center">
    <h2 className="text-4xl md:text-5xl font-extrabold mb-4 text-gray-800">
      Our Approach
    </h2>
    <p className="text-gray-600 text-lg md:text-xl mb-16">
      How we deliver exceptional predictive maintenance solutions with efficiency, innovation, and precision.
    </p>

    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-10">
      {approach.map((a, i) => (
        <motion.div
          key={i}
          className="bg-white rounded-xl shadow-lg p-8 flex flex-col items-center text-center transition-transform duration-300 hover:scale-105 hover:shadow-2xl"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: i * 0.2 }}
        >
          <i className={`${a.icon} text-5xl text-blue-600 mb-4`}></i>
          <h3 className="text-2xl font-bold mb-2 text-gray-800">{a.title}</h3>
          <p className="text-gray-600 text-base md:text-lg">{a.desc}</p>
        </motion.div>
      ))}
    </div>
  </div>
</section>



  

      {/* CTA */}
      <section className="py-16 px-4 bg-blue-600 text-white text-center">
        <h2 className="text-3xl md:text-4xl font-bold mb-4">Join Our Journey</h2>
        <p className="text-gray-200 mb-6">Partner with us to transform your maintenance operations and drive operational excellence.</p>
        <Link to="/contact" className="px-6 py-3 bg-white text-blue-600 font-bold rounded-lg hover:bg-gray-100 transition">
          Connect With Us
        </Link>
      </section>

    </div>
  );
};

export default About;
