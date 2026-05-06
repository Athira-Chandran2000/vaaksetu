import React, { useState, useRef } from 'react';
import './CallInterface.css';

/**
 * CallInterface — Citizen call simulator for the demo.
 * Allows text input and audio recording to test the VaakSetu pipeline.
 */

const SAMPLE_QUERIES = [
  { label: "Ration Card (Kannada)", text: "Nanna ration card update aagilla, mooru tingalu aaytu application haakiddu, yenu aagide gottilla", language: "kannada" },
  { label: "Water Supply (Kannada)", text: "Namm area alli neeru barilla, eradu dina aaytu, BWSSB ge phone maadidru yaaradru phone ettilla", language: "kannada" },
  { label: "Pension Delay (Kannada)", text: "Nanna ajji ge pension baribeku ittu, mooru tingalu aaytu barilla, dayavittu sahaya maadi", language: "kannada" },
  { label: "Road Pothole (English)", text: "There is a very dangerous pothole on the main road in Jayanagar 4th Block, near the bus stop. Two accidents have already happened.", language: "english" },
  { label: "Land Dispute (Kannada)", text: "Namm hola jamin survey number 78 alli problem ide, pakkada mane avru namm jaaga tagondu idare, bhoomi record alli confusion ide", language: "kannada" },
  { label: "Emergency Distress", text: "HELP! Please turant sahaya beku, namma mane pakka tree beelide, current wire mele biddide, bahut dangerous hai!!", language: "kannada-english" },
  { label: "Garbage (Hindi)", text: "Teen din se kachra nahi uthaya gaya hai, BBMP wale koi dhyan nahi de rahe, bahut gandagi ho gayi hai", language: "hindi" },
  { label: "Seva Sindhu Status", text: "Naan income certificate ge Seva Sindhu nalli apply maadidde, ondu tingalu aaytu, application status check maadoke gottilla", language: "kannada" },
];

export default function CallInterface({ onSubmitText, onSubmitAudio, isProcessing, transcriptHistory = [] }) {
  const [text, setText] = useState('');
  const [language, setLanguage] = useState('kannada');
  const [dialect, setDialect] = useState('standard');
  const [isRecording, setIsRecording] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);
  const chatEndRef = useRef(null);

  // Auto-scroll to bottom of chat
  React.useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [transcriptHistory]);

  const handleSubmitText = () => {
    if (!text.trim() || isProcessing) return;
    onSubmitText?.(text.trim(), language, dialect);
    setText(''); // Clear input after sending
  };

  const handleSampleQuery = (sample) => {
    setText(sample.text);
    setLanguage(sample.language);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        stream.getTracks().forEach(t => t.stop());
        onSubmitAudio?.(blob, language, dialect);
        clearInterval(timerRef.current);
        setRecordingDuration(0);
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingDuration(0);
      timerRef.current = setInterval(() => {
        setRecordingDuration(d => d + 1);
      }, 1000);
    } catch (err) {
      console.error('Microphone access denied:', err);
      alert('Microphone access is required for audio recording.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className="call-interface glass-card chat-mode">
      <div className="ci-header">
        <h3 className="ci-title">🤖 VaakSetu Chatbot</h3>
        <div className="ci-status">
          <span className={`status-dot ${isProcessing ? 'warning' : 'active'}`} />
          <span>{isProcessing ? 'Thinking...' : 'Online'}</span>
        </div>
      </div>

      {/* Chat Window */}
      <div className="chat-window">
        {transcriptHistory.length === 0 ? (
          <div className="chat-empty">
            <div className="chat-empty-icon">👋</div>
            <p>How can I help you today?</p>
            <span>Ask about Ration cards, Water supply, or Government services in Kannada, Hindi, or English.</span>
          </div>
        ) : (
          <div className="chat-messages">
            {transcriptHistory.map((entry, i) => (
              <div key={i} className={`transcript-entry animate-fade-in ${entry.source === 'agent' ? 'agent-message' : ''}`}>
                <div className="transcript-meta">
                  <span className={`badge ${entry.source === 'agent' ? 'badge-success' : 'badge-accent'}`}>
                    {entry.source === 'agent' ? 'AGENT' : entry.language}
                  </span>
                  <span className="transcript-time">
                    {new Date(entry.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    {entry.source === 'audio' && ' 🎙️'}
                  </span>
                </div>
                <p className="transcript-text">{entry.text}</p>
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="chat-input-container">
        <div className="chat-controls-mini">
           <select
            className="select-mini"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
          >
            <option value="kannada">Kannada</option>
            <option value="hindi">Hindi</option>
            <option value="english">English</option>
          </select>
        </div>

        <div className="ci-text-input chat-style">
          <textarea
            className="textarea chat-textarea"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Type your message..."
            rows={1}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmitText();
              }
            }}
          />
          
          <div className="chat-actions">
            {!isRecording ? (
              <button className="btn-circle" onClick={startRecording} title="Record Audio">
                🎙️
              </button>
            ) : (
              <button className="btn-circle btn-danger recording-pulse" onClick={stopRecording}>
                ⏹️
              </button>
            )}
            
            <button
              className="btn-circle btn-primary"
              onClick={handleSubmitText}
              disabled={!text.trim() || isProcessing}
            >
              {isProcessing ? '⏳' : '🚀'}
            </button>
          </div>
        </div>
      </div>

      {/* Quick Suggestions */}
      <div className="ci-samples mini">
        <h4 className="ci-samples-title">Test Scenarios (Click to try)</h4>
        <div className="sample-vertical-list">
          {SAMPLE_QUERIES.map((sample, i) => (
            <button
              key={i}
              className="btn btn-ghost sample-btn-pill vertical"
              onClick={() => handleSampleQuery(sample)}
            >
              <span className="sample-emoji">💬</span>
              {sample.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
