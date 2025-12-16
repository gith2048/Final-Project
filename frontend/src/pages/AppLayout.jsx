import { useLocation } from 'react-router-dom';
import Header from "../components/Header";
import Footer from "../components/Footer";


const AppLayout = ({ children, isAuthenticated }) => {
  const location = useLocation();
  const isDashboardView = location.pathname === "/dashboard";

  return (
    <>
      <Header isAuthenticated={isAuthenticated} />
      <main className={isDashboardView ? "" : "p-4"}>{children}</main>
      {!isDashboardView && <Footer />}
    </>
  );
};

export default AppLayout;