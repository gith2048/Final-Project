// Contact.jsx
import React, { useState } from "react";

const Contact = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    message: "",
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const { name, email, message } = formData;

    const mailtoBody = `Name: ${name}\nEmail: ${email}\n\nMessage:\n${message}`;
    const mailtoLink = `mailto:sathithyagasathi@gmail.com?subject=Contact from ${encodeURIComponent(
      name
    )}&body=${encodeURIComponent(mailtoBody)}`;

    window.location.href = mailtoLink;
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
      <form
        onSubmit={handleSubmit}
        className="bg-white shadow-md rounded-lg p-8 w-full max-w-md"
      >
        <h2 className="text-2xl font-bold text-center text-blue-600 mb-6">
          Contact Us
        </h2>

        <label htmlFor="name" className="block mb-2 font-medium">
          Name
        </label>
        <input
          type="text"
          id="name"
          name="name"
          required
          placeholder="Your full name"
          value={formData.name}
          onChange={handleChange}
          className="w-full border border-gray-300 p-2 rounded mb-4"
        />

        <label htmlFor="email" className="block mb-2 font-medium">
          Email
        </label>
        <input
          type="email"
          id="email"
          name="email"
          required
          placeholder="you@example.com"
          value={formData.email}
          onChange={handleChange}
          className="w-full border border-gray-300 p-2 rounded mb-4"
        />

        <label htmlFor="message" className="block mb-2 font-medium">
          Message
        </label>
        <textarea
          id="message"
          name="message"
          required
          placeholder="Write your message here..."
          value={formData.message}
          onChange={handleChange}
          className="w-full border border-gray-300 p-2 rounded mb-6"
          rows="5"
        ></textarea>

        <button
          type="submit"
          className="w-full bg-blue-600 text-white font-semibold py-2 px-4 rounded hover:bg-blue-700 transition"
        >
          Send Message
        </button>
      </form>
    </div>
  );
};

export default Contact;