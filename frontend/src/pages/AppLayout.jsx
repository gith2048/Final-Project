import React from 'react';
import { useLocation } from 'react-router-dom';
import Header from "../components/Header";
import Footer from "../components/Footer";


const AppLayout = ({ children, isAuthenticated }) => {
  const location = useLocation();
  const isDashboardView = location.pathname === "/dashboard";

  return (
    <>
      {!isDashboardView && <Header isAuthenticated={isAuthenticated} />}
      <main className="p-4">{children}</main>
      {!isDashboardView && <Footer />}
    </>
  );
};

export default AppLayout;