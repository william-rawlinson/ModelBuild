import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import DesignModelPage from "./pages/DesignModelPage";
import ViewModelPage from "./pages/ViewModelPage";
import Layout from "./components/Layout";


export default function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<DesignModelPage />} />
          <Route path="/view_model" element={<ViewModelPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}
