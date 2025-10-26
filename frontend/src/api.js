import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:5000", // your Flask backend
});

export default api;