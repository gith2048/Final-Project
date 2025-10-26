import React from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  FaChartLine,
  FaTools,
  FaMoneyBillWave,
  FaTachometerAlt,
} from "react-icons/fa";

const Home = () => {
  const features = [
    {
      icon: <FaChartLine className="text-4xl text-blue-600 mb-4" />,
      title: "Reduce Downtime",
      desc: "Prevent unexpected failures and reduce downtime by up to 50%.",
    },
    {
      icon: <FaTools className="text-4xl text-blue-600 mb-4" />,
      title: "Extend Equipment Life",
      desc: "Optimize schedules to extend equipment lifetime.",
    },
    {
      icon: <FaMoneyBillWave className="text-4xl text-blue-600 mb-4" />,
      title: "Lower Costs",
      desc: "Reduce maintenance costs by eliminating unnecessary repairs.",
    },
    {
      icon: <FaTachometerAlt className="text-4xl text-blue-600 mb-4" />,
      title: "Increase Efficiency",
      desc: "Boost overall equipment effectiveness (OEE).",
    },
  ];

  const products = [
    {
      id: 1,
      name: "Smart IoT Monitor",
      image: "/assets/smart_iot_monitor.jpg",
      description: "Real-time machine monitoring",
    },
    {
      id: 2,
      name: "Predictive Dashboard",
      image: "/assets/predictive_dashboard.jpg",
      description: "Analytics & insights",
    },
    {
      id: 3,
      name: "AI Maintenance Predictor",
      image: "/assets/ai_maintenance_predictor.jpg",
      description: "Prevent downtime with AI",
    },
  ];

  return (
    <div className="w-full overflow-hidden">

      {/* Hero Section with Background Image */}
      <div className="relative w-full h-screen overflow-hidden bg-slate-900">
        {/* Background Image */}
        <img
          src="https://images.unsplash.com/photo-1759661966728-4a02e3c6ed91?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx0ZWNobm9sb2d5JTIwZGF0YSUyMGFuYWx5dGljc3xlbnwxfHx8fDE3NjA5NDQxNjh8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
          alt="Predictive Maintenance - Technology Background"
          className="w-full h-full object-cover opacity-60"
        />

        {/* Overlay for contrast */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900/70 via-slate-900/40 to-slate-900/80" />

        {/* Hero Content */}
        <div className="absolute inset-0 flex items-center justify-center z-10">
          <div className="text-center px-4 text-white">
            <motion.h1
              className="text-4xl sm:text-5xl md:text-6xl font-bold mb-4"
              initial={{ opacity: 0, y: -50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1 }}
            >
              Transforming Maintenance Through Prediction
            </motion.h1>
            <motion.p
              className="mb-6 text-lg sm:text-xl md:text-2xl"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 1, delay: 0.5 }}
            >
              Prevent downtime, extend machine life, and maximize efficiency with our predictive maintenance solutions.
            </motion.p>
            <motion.div
              className="space-x-4 flex justify-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 1, delay: 1 }}
            >
              <Link
                to="/products"
                className="px-6 py-3 bg-yellow-400 text-blue-800 font-bold rounded-lg hover:bg-yellow-500 transition"
              >
                Explore Solutions
              </Link>
              <Link
                to="/contact"
                className="px-6 py-3 border-2 border-white rounded-lg hover:bg-white hover:text-blue-800 transition"
              >
                Contact Us
              </Link>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <section className="py-16 px-4 bg-white">
        <div className="max-w-7xl mx-auto grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8">
          {features.map((feature, i) => (
            <motion.div
              key={i}
              className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition text-center flex flex-col items-center"
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.2 }}
            >
              {feature.icon}
              <h3 className="font-bold text-xl mb-2">{feature.title}</h3>
              <p className="text-gray-600">{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Products Section */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Our Solutions</h2>
          <p className="text-gray-600 text-lg md:text-xl">
            Range of predictive maintenance products designed for smooth operations.
          </p>
        </div>
        <div className="max-w-6xl mx-auto grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8">
          {products.map((product) => (
            <motion.div
              key={product.id}
              className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition text-center"
              whileHover={{ scale: 1.05 }}
            >
              <img
                src={product.image}
                alt={product.name}
                className="mx-auto mb-4 h-40 object-contain"
              />
              <h3 className="font-bold text-xl mb-2">{product.name}</h3>
              <p className="text-gray-600 mb-4">{product.description}</p>
              <Link
                to="/products"
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
              >
                Learn More
              </Link>
            </motion.div>
          ))}
        </div>
        <div className="w-full flex justify-center mt-12">
          <Link
            to="/products"
            className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            Know More
          </Link>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-4 bg-blue-600 text-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to Optimize Your Maintenance Strategy?
          </h2>
          <p className="text-lg md:text-xl mb-6">
            Schedule a consultation with our experts to discover how our solutions can benefit your operations.
          </p>
          <Link
            to="/contact"
            className="px-6 py-3 bg-yellow-400 text-blue-800 font-bold rounded-lg hover:bg-yellow-500 transition"
          >
            Connect With Us
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Home;