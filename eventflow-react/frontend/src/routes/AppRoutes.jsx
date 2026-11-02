import { Routes, Route } from "react-router-dom";
import Home from "../pages/Home";
import EventDetails from "../pages/EventDetails";
import Login from "../pages/Login";
import Register from "../pages/Register";
import Search from "../pages/Search";
import HighlightedEvents from "../pages/HighlightedEvents";
import TodayEvents from "../pages/TodayEvents";
import MyRegistrations from "../pages/MyRegistrations";
import MyEvents from "../pages/MyEvents";
import CreateEvent from "../pages/CreateEvent";
import EditEvent from "../pages/EditEvent";
import EventRegistrations from "../pages/EventRegistrations";
import PrivateRoute from "./PrivateRoute";

export default function AppRoutes() {
  return (
    <Routes>
      {/* Rotas Públicas */}
      <Route path="/" element={<Home />} />
      <Route path="/event/:id/" element={<EventDetails />} />
      <Route path="/users/login/" element={<Login />} />
      <Route path="/users/register/" element={<Register />} />
      <Route path="/search/" element={<Search />} />
      <Route path="/events/highlighted/" element={<HighlightedEvents />} />
      <Route path="/events/today/" element={<TodayEvents />} />

      {/* Rotas Protegidas (Participante / Organizador) */}
      <Route
        path="/registrations/me/"
        element={
          <PrivateRoute>
            <MyRegistrations />
          </PrivateRoute>
        }
      />
      <Route
        path="/events/me/"
        element={
          <PrivateRoute>
            <MyEvents />
          </PrivateRoute>
        }
      />
      <Route
        path="/events/create/"
        element={
          <PrivateRoute>
            <CreateEvent />
          </PrivateRoute>
        }
      />
      <Route
        path="/event/:id/edit/"
        element={
          <PrivateRoute>
            <EditEvent />
          </PrivateRoute>
        }
      />
      <Route
        path="/event/:id/registrations/"
        element={
          <PrivateRoute>
            <EventRegistrations />
          </PrivateRoute>
        }
      />

      {/* Rota Fallback */}
      <Route path="*" element={<Home />} />
    </Routes>
  );
}
