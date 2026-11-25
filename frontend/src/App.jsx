
import { useEffect, useState, useRef } from "react";
import { PipecatClient } from "@pipecat-ai/client-js";
import { SmallWebRTCTransport } from "@pipecat-ai/small-webrtc-transport";
import "./App.css";

const API = "http://localhost:8000";

function App() {
  const [doctors, setDoctors] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [date, setDate] = useState("2026-11-25");
  const [doctorId, setDoctorId] = useState("");
  const [time, setTime] = useState("");
  const [phone, setPhone] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [cancelPhone, setCancelPhone] = useState("");
  const [cancelConfirmed, setCancelConfirmed] = useState(false);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const clientRef = useRef(null);
  const [callStatus, setCallStatus] = useState("Disconnected");
  const [transcript, setTranscript] = useState([]);

  const selectedDoctor = doctors.find(
    (doctor) => doctor.id === Number(doctorId)
  );

  async function loadData() {
    try {
      const [doctorResponse, appointmentResponse] = await Promise.all([
        fetch(`${API}/api/doctors`),
        fetch(`${API}/api/appointments`)
      ]);

      if (!doctorResponse.ok || !appointmentResponse.ok) {
        throw new Error("Could not load dashboard data.");
      }

      setDoctors(await doctorResponse.json());
      setAppointments(await appointmentResponse.json());
    } catch (error) {
      setMessage("Backend connection failed. Is the Python server running?");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  async function bookAppointment(event) {
    event.preventDefault();
    setMessage("");

    if (!confirmed) {
      setMessage("Please confirm the phone number before booking.");
      return;
    }

    try {
      const response = await fetch(`${API}/api/book`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          doctor_id: Number(doctorId),
          date,
          time,
          phone,
          phone_confirmed: confirmed
        })
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Booking failed.");
      }

      setMessage(result.message);
      setPhone("");
      setTime("");
      setConfirmed(false);
      await loadData();
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function cancelAppointment(event) {
    event.preventDefault();
    setMessage("");

    if (!cancelConfirmed) {
      setMessage("Please confirm the phone number before cancellation.");
      return;
    }

    try {
      const response = await fetch(`${API}/api/cancel`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phone: cancelPhone,
          phone_confirmed: cancelConfirmed
        })
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Cancellation failed.");
      }

      setMessage(result.message);
      setCancelPhone("");
      setCancelConfirmed(false);
      await loadData();
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function startVoiceCall() {
  try {
    setCallStatus("Connecting...");
    setTranscript([]);

    const client = new PipecatClient({
      transport: new SmallWebRTCTransport(),
      enableMic: true,
      enableCam: false,
      callbacks: {
        onConnected: () => setCallStatus("Connected"),
        onDisconnected: () => setCallStatus("Disconnected"),

        onUserTranscript: (data) => {
          if (data.final) {
            setTranscript((old) => [
              ...old,
              { speaker: "You", text: data.text }
            ]);
          }
        },

        onBotTranscript: (data) => {
          setTranscript((old) => [
            ...old,
            { speaker: "CareFlow AI", text: data.text }
          ]);
        },

        onError: (error) => {
          console.error("Voice error:", error);
          setCallStatus("Connection error");
        }
      }
    });

    clientRef.current = client;

    await client.startBotAndConnect({
      endpoint: "http://localhost:7860/start",
      requestData: {
        transport: "webrtc",
        enableDefaultIceServers: true
      }
    });

  } catch (error) {
    console.error("Could not start voice call:", error);
    setCallStatus("Connection failed");
  }
}

async function endVoiceCall() {
  if (clientRef.current) {
    await clientRef.current.disconnect();
    clientRef.current = null;
  }

  setCallStatus("Disconnected");
}

async function startVoiceCall() {
  try {
    setCallStatus("Connecting...");
    setTranscript([]);

    const client = new PipecatClient({
      transport: new SmallWebRTCTransport(),
      enableMic: true,
      enableCam: false,
      callbacks: {
        onConnected: () => setCallStatus("Connected"),
        onDisconnected: () => setCallStatus("Disconnected"),

        onUserTranscript: (data) => {
          if (data.final) {
            setTranscript((old) => [
              ...old,
              { speaker: "You", text: data.text }
            ]);
          }
        },

        onBotTranscript: (data) => {
          setTranscript((old) => [
            ...old,
            { speaker: "CareFlow AI", text: data.text }
          ]);
        },

        onError: (error) => {
          console.error("Voice error:", error);
          setCallStatus("Connection error");
        }
      }
    });

    clientRef.current = client;

    await client.startBotAndConnect({
      endpoint: "http://localhost:7860/start",
      requestData: {
        transport: "webrtc",
        enableDefaultIceServers: true
      }
    });

  } catch (error) {
    console.error("Could not start voice call:", error);
    setCallStatus("Connection failed");
  }
}

async function endVoiceCall() {
  if (clientRef.current) {
    await clientRef.current.disconnect();
    clientRef.current = null;
  }

  setCallStatus("Disconnected");
}

  if (loading) {
    return <div className="loading">Loading CareFlow AI...</div>;
  }

  return (
    <div className="app">
      <header className="navbar">
        <h2>CareFlow AI</h2>
        <span>Voice Appointment Assistant</span>
      </header>

      <main className="dashboard">
        <section className="welcome">
          <p className="tag">AI-POWERED HEALTHCARE</p>
          <h1>Your healthcare, simplified.</h1>
          <p>
            Check doctors, book appointments and manage your visits
            with CareFlow AI.
          </p>
        </section>

        {message && <div className="message">{message}</div>}

        <section className="call-card">
  <div className="circle">🎙️</div>
  <h2>CareFlow Voice Assistant</h2>

  <p>Talk naturally to book or manage doctor appointments.</p>

  <span className="status">
    Voice status: {callStatus}
  </span>

  <div style={{ marginTop: "20px" }}>
    <button
      onClick={startVoiceCall}
      disabled={
        callStatus === "Connected" ||
        callStatus === "Connecting..."
      }
    >
      Start Voice Call
    </button>

    <button
      onClick={endVoiceCall}
      className="cancel-button"
      disabled={callStatus !== "Connected"}
      style={{ marginLeft: "10px" }}
    >
      End Call
    </button>
  </div>

  <div style={{ marginTop: "20px", textAlign: "left" }}>
    <h3>Live Conversation</h3>

    {transcript.length === 0 ? (
      <p>Your conversation will appear here.</p>
    ) : (
      transcript.map((item, index) => (
        <p key={index}>
          <strong>{item.speaker}:</strong> {item.text}
        </p>
      ))
    )}
  </div>
</section>

        <section className="panel">
          <h2>Available Doctors</h2>
          {doctors.map((doctor) => (
            <div className="doctor" key={doctor.id}>
              <div>
                <h3>{doctor.name}</h3>
                <p>{doctor.speciality} · {doctor.experience}</p>
                <small>Slots: {doctor.slots.join(" | ")}</small>
              </div>
            </div>
          ))}
        </section>

        <section className="panel">
          <h2>Book an Appointment</h2>
          <form onSubmit={bookAppointment}>
            <label>Choose doctor</label>
            <select
              value={doctorId}
              onChange={(e) => {
                setDoctorId(e.target.value);
                setTime("");
              }}
              required
            >
              <option value="">Select a doctor</option>
              {doctors.map((doctor) => (
                <option key={doctor.id} value={doctor.id}>
                  {doctor.name} — {doctor.speciality}
                </option>
              ))}
            </select>

            <label>Appointment date</label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              required
            />

            <label>Available time slot</label>
            <select
              value={time}
              onChange={(e) => setTime(e.target.value)}
              required
              disabled={!selectedDoctor}
            >
              <option value="">Select a time</option>
              {selectedDoctor?.slots.map((slot) => (
                <option key={slot} value={slot}>
                  {slot}
                </option>
              ))}
            </select>

            <label>Patient phone number</label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="Enter 10-digit phone number"
              maxLength={10}
              required
            />

            <label className="check">
              <input
                type="checkbox"
                checked={confirmed}
                onChange={(e) => setConfirmed(e.target.checked)}
              />
              I confirm this phone number.
            </label>

            <button type="submit">Book Appointment</button>
          </form>
        </section>

        <section className="panel">
          <h2>Cancel an Appointment</h2>
          <form onSubmit={cancelAppointment}>
            <label>Patient phone number</label>
            <input
              type="tel"
              value={cancelPhone}
              onChange={(e) => setCancelPhone(e.target.value)}
              placeholder="Enter booking phone number"
              maxLength={10}
              required
            />

            <label className="check">
              <input
                type="checkbox"
                checked={cancelConfirmed}
                onChange={(e) => setCancelConfirmed(e.target.checked)}
              />
              I confirm this phone number.
            </label>

            <button type="submit" className="cancel-button">
              Cancel Appointment
            </button>
          </form>
        </section>

        <section className="panel">
          <h2>Appointments ({appointments.length})</h2>
          {appointments.length === 0 ? (
            <p>No appointments yet.</p>
          ) : (
            appointments.map((appointment) => (
              <div className="appointment" key={appointment.id}>
                <h3>{appointment.doctor_name}</h3>
                <p>
                  {appointment.speciality} · {appointment.date} · {appointment.time}
                </p>
                <p>Phone: {appointment.phone}</p>
                <strong className={
                  appointment.status === "Booked" ? "booked" : "cancelled"
                }>
                  {appointment.status}
                </strong>
              </div>
            ))
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
